# -*- coding: utf-8 -*-
"""
/***************************************************************************
OpenLayers Plugin
A QGIS plugin

                             -------------------
begin                : 2009-11-30
copyright            : (C) 2009 by Pirmin Kalberer, Sourcepole
email                : pka at sourcepole.ch
modified             : 2018-11-23 by Minpa Lee, mapplus at gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# Import the PyQt and QGIS libraries
import contextlib

from qgis.PyQt.QtCore import (QSettings, QTranslator, QCoreApplication, qVersion)
from qgis.PyQt.QtWidgets import (QApplication, QLineEdit, QInputDialog,
                                 QAction, QMenu)
from qgis.PyQt.QtGui import QIcon
from qgis.core import (QgsCoordinateTransform, Qgis, QgsProject,
                       QgsPluginLayerRegistry, QgsLayerTree, QgsLayerTreeLayer,
                       QgsRasterLayer, QgsMessageLog)

from . import resources_rc
from .about_dialog import AboutDialog
from .openlayers_layer import OpenlayersLayer
from .openlayers_plugin_layer_type import OpenlayersPluginLayerType
from .weblayers.weblayer_registry import WebLayerTypeRegistry

from .weblayers.vworld_maps import (OlVWorldStreetLayer,
                                    OlVWorldSatelliteLayer,
                                    OlVWorldGrayLayer,
                                    OlVWorldHybridLayer)

from .weblayers.naver_maps import (OlNaverStreetLayer,
                                   OlNaverHybridLayer,
                                   OlNaverSatelliteLayer,
                                   OlNaverPhysicalLayer,
                                   OlNaverCadastralLayer)

from .weblayers.osm_maps import OlOSMStandardLayer

from .weblayers.azure_maps import (OlAzureRoadLayer,
                                   OlAzureSatelliteLayer,
                                   OlAzureHybridLayer,
                                   OlAzureMapsLayer,
                                   getAzureMapsKey,
                                   setAzureMapsKey,
                                   AZURE_MAPS_SIGNUP_URL)

from . import network_hooks

import os.path
import time
import collections
import requests


class OpenlayersPlugin:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # Keep a reference to all OL layers to avoid GC
        self._ol_layers = []
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, "i18n", "openlayers_{}.qm".format(locale))

        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > "4.3.3":
                QCoreApplication.installTranslator(self.translator)

        self._olLayerTypeRegistry = WebLayerTypeRegistry(self)
        # Lazy-construct the About dialog on first use so any Qt6 enum quirks
        # in the generated ui_about_dialog.py do not block plugin load.
        self.dlgAbout = None
        self.pluginLayerRegistry = QgsPluginLayerRegistry()
        # Naver UA workaround: registered in initGui, removed in unload.
        self._naverUaPreprocessorId = None
        # Azure Maps layer types tracked separately so we can toggle their
        # menu actions enabled/disabled when the subscription key changes.
        self._azureLayerTypes = []

    def _getAboutDialog(self):
        if self.dlgAbout is None:
            self.dlgAbout = AboutDialog()
            self.dlgAbout.finished.connect(self._publicationInfoClosed)
        return self.dlgAbout

    def _showAbout(self):
        self._getAboutDialog().show()

    def _attachAzureConfigureAction(self):
        """Place 'Configure Azure Maps Key…' inside the Azure Maps submenu.

        Called once after the per-group submenus have been assembled in
        initGui. A leading separator distinguishes the action from the
        layer entries above it.
        """
        if not self._azureLayerTypes:
            return
        azureGroup = self._azureLayerTypes[0].group
        if azureGroup is None:
            return
        azureMenu = azureGroup.menu()
        azureMenu.addSeparator()
        azureMenu.addAction(self._actionAzureKey)

    def _refreshAzureMenuState(self):
        """Enable Azure layer menu entries only when a key is configured.

        Re-run after the key is set or cleared in the configure dialog so
        the menu state reflects the current QSettings value without a
        plugin reload.
        """
        keyPresent = bool(getAzureMapsKey())
        tooltipWhenDisabled = (
            "먼저 Azure 구독 키를 설정해 주세요 "
            "(이 그룹의 'Azure 구독 키 설정…' 항목)."
        )
        for layer in self._azureLayerTypes:
            action = getattr(layer, "_actionAddLayer", None)
            if action is None:
                # initGui's per-group loop has not run yet; nothing to do.
                continue
            action.setEnabled(keyPresent)
            action.setToolTip("" if keyPresent else tooltipWhenDisabled)

    def _configureAzureMapsKey(self):
        # Simple modal text prompt; equivalent UX to other QGIS plugins that
        # require an API key (no custom QDialog needed for a single field).
        currentKey = getAzureMapsKey()
        prompt = (
            "Azure Maps 구독 키(subscription key)를 입력하세요.\n"
            "무료 S0 등급 가입:\n"
            "  " + AZURE_MAPS_SIGNUP_URL + "\n\n"
            "비워두고 확인을 누르면 저장된 키가 삭제됩니다."
        )
        key, ok = QInputDialog.getText(
            self.iface.mainWindow(),
            "Azure 지도 — 구독 키 설정",
            prompt,
            QLineEdit.EchoMode.Normal,
            currentKey,
        )
        if not ok:
            return
        setAzureMapsKey(key.strip())
        # Reflect the new state on the Azure layer actions immediately so
        # the user does not have to reopen the menu or reload the plugin.
        self._refreshAzureMenuState()
        if key.strip():
            self.iface.messageBar().pushMessage(
                "TMS for Korea",
                "Azure 구독 키가 저장되었습니다. 이제 Azure 지도 레이어를 추가할 수 있습니다.",
                level=Qgis.MessageLevel.Info,
                duration=5,
            )
        else:
            self.iface.messageBar().pushMessage(
                "TMS for Korea",
                "Azure 구독 키가 삭제되었습니다.",
                level=Qgis.MessageLevel.Info,
                duration=4,
            )

    def initGui(self):
        # Install Naver UA workaround as early as possible so it is active
        # by the time any layer issues its first tile request.
        self._naverUaPreprocessorId = network_hooks.install()

        self._olMenu = QMenu("TMS for Korea")
        self._olMenu.setIcon(QIcon(":/plugins/openlayers/openlayers.png"))

        self._actionAbout = QAction("TMS for Korea 정보", self.iface.mainWindow())
        self._actionAbout.triggered.connect(self._showAbout)
        self._olMenu.addAction(self._actionAbout)

        # The Azure key action is created here but attached to the Azure
        # Maps submenu later (not to the top-level TMS menu) so the key
        # entry sits alongside the layers it gates.
        self._actionAzureKey = QAction("Azure 구독 키 설정…", self.iface.mainWindow())
        self._actionAzureKey.triggered.connect(self._configureAzureMapsKey)

        # Kakao Maps - upstream policy block since 2025-10-20.
        # The CDN (*.daumcdn.net) rejects direct tile access regardless of
        # any API key; restoration requires embedding Kakao's JavaScript
        # SDK via QtWebEngine, which is a separate phase. Until then a
        # disabled placeholder submenu surfaces the situation in the UI
        # so users discover it without reading the README.
        # self._olLayerTypeRegistry.register(OlDaumStreetLayer())
        # self._olLayerTypeRegistry.register(OlDaumHybridLayer())
        # self._olLayerTypeRegistry.register(OlDaumSatelliteLayer())
        # self._olLayerTypeRegistry.register(OlDaumPhysicalLayer())
        # self._olLayerTypeRegistry.register(OlDaumCadstralLayer())

        # Naver Maps - 3857(New)
        self._olLayerTypeRegistry.register(OlNaverStreetLayer())
        self._olLayerTypeRegistry.register(OlNaverHybridLayer())
        self._olLayerTypeRegistry.register(OlNaverSatelliteLayer())
        self._olLayerTypeRegistry.register(OlNaverPhysicalLayer())
        self._olLayerTypeRegistry.register(OlNaverCadastralLayer())

        # Naver Maps - 5179(Old)
        #self._olLayerTypeRegistry.register(OlNaverStreet5179Layer())
        #self._olLayerTypeRegistry.register(OlNaverHybrid5179Layer())
        #self._olLayerTypeRegistry.register(OlNaverSatellite5179Layer())
        #self._olLayerTypeRegistry.register(OlNaverPhysical5179Layer())
        #self._olLayerTypeRegistry.register(OlNaverCadastral5179Layer())

        # VWorld - 3857
        self._olLayerTypeRegistry.register(OlVWorldStreetLayer())
        self._olLayerTypeRegistry.register(OlVWorldSatelliteLayer())
        self._olLayerTypeRegistry.register(OlVWorldGrayLayer())
        self._olLayerTypeRegistry.register(OlVWorldHybridLayer())

        # OpenStreetMap - 3857
        self._olLayerTypeRegistry.register(OlOSMStandardLayer())

        # Azure Maps - 3857 (requires user-supplied subscription key).
        # Kept in a separate list so the menu actions for these can be
        # toggled enabled/disabled based on whether the key is configured.
        self._azureLayerTypes = [
            OlAzureRoadLayer(),
            OlAzureSatelliteLayer(),
            OlAzureHybridLayer(),
        ]
        for layer in self._azureLayerTypes:
            self._olLayerTypeRegistry.register(layer)

        # NGII - 5179
        #self._olLayerTypeRegistry.register(OlNgiiStreetLayer())
        #self._olLayerTypeRegistry.register(OlNgiiBlankLayer())
        #self._olLayerTypeRegistry.register(OlNgiiEnglishLayer())
        #self._olLayerTypeRegistry.register(OlNgiiHighDensityLayer())
        #self._olLayerTypeRegistry.register(OlNgiiColorBlindLayer())

        # Mango - 3857
        #self._olLayerTypeRegistry.register(OlMangoBaseMapLayer())
        #self._olLayerTypeRegistry.register(OlMangoBaseMapGrayLayer())
        #self._olLayerTypeRegistry.register(OlMangoHiDPIMapLayer())
        #self._olLayerTypeRegistry.register(OlMangoHiDPIMapGrayLayer())

        for group in self._olLayerTypeRegistry.groups():
            groupMenu = group.menu()
            for layer in self._olLayerTypeRegistry.groupLayerTypes(group):
                layer.addMenuEntry(groupMenu, self.iface.mainWindow())
            self._olMenu.addMenu(groupMenu)

        # Attach the Azure key action inside the Azure Maps submenu (now
        # that its QMenu exists from the loop above) and reflect the
        # current key state on the layer actions.
        self._attachAzureConfigureAction()
        self._refreshAzureMenuState()

        # Disabled Kakao Maps placeholder — communicates upstream policy
        # block in the UI itself instead of silently omitting the group.
        self._kakaoPlaceholderMenu = QMenu("카카오 지도")
        self._kakaoPlaceholderMenu.setIcon(QIcon(":/plugins/openlayers/openlayers.png"))
        self._kakaoInfoAction = QAction(
            "사용 불가 — 카카오 정책 차단 (2025-10-20)",
            self.iface.mainWindow(),
        )
        self._kakaoInfoAction.setEnabled(False)
        self._kakaoInfoAction.setToolTip(
            "2025-10-20부터 카카오가 타일 직접 접근을 차단했습니다.\n"
            "복원하려면 QtWebEngine + 공식 카카오맵 JS SDK 임베드가\n"
            "필요하며, 별도 phase로 추후 진행 예정입니다.\n"
            "자세한 내용은 MIGRATION.md를 참고하세요."
        )
        self._kakaoPlaceholderMenu.addAction(self._kakaoInfoAction)
        self._kakaoPlaceholderMenu.setEnabled(False)
        self._olMenu.addMenu(self._kakaoPlaceholderMenu)

        # Create Web menu, if it doesn't exist yet
        self.iface.addPluginToWebMenu("_tmp", self._actionAbout)
        self._menu = self.iface.webMenu()
        self._menu.addMenu(self._olMenu)
        self.iface.removePluginWebMenu("_tmp", self._actionAbout)

        # Register plugin layer type
        self.pluginLayerType = OpenlayersPluginLayerType(
            self.iface, self.setReferenceLayer, self._olLayerTypeRegistry)

        self.pluginLayerRegistry.addPluginLayerType(
            self.pluginLayerType)

        QgsProject.instance().readProject.connect(self.projectLoaded)
        QgsProject.instance().projectSaved.connect(self.projectSaved)

    def unload(self):
        self.iface.webMenu().removeAction(self._olMenu.menuAction())

        # Unregister plugin layer type
        self.pluginLayerRegistry.removePluginLayerType(
            OpenlayersLayer.LAYER_TYPE)

        # Tear down the Naver UA preprocessor so the rewrite is no longer
        # active after the plugin is unloaded.
        network_hooks.uninstall(self._naverUaPreprocessorId)
        self._naverUaPreprocessorId = None

        QgsProject.instance().readProject.disconnect(self.projectLoaded)
        QgsProject.instance().projectSaved.disconnect(self.projectSaved)

    def addLayer(self, layerType):
        # Azure Maps requires a user-supplied subscription key; bail with a
        # friendly message bar entry instead of creating an invalid layer
        # when the key is missing.
        if isinstance(layerType, OlAzureMapsLayer) and not getAzureMapsKey():
            self.iface.messageBar().pushMessage(
                "TMS for Korea",
                "Azure 구독 키가 설정되지 않았습니다. "
                "먼저 '웹 > TMS for Korea > Azure 지도 > Azure 구독 키 설정…'을 실행해 주세요 "
                "(무료 S0 등급: " + AZURE_MAPS_SIGNUP_URL + ").",
                level=Qgis.MessageLevel.Warning,
                duration=10,
            )
            return

        if layerType.hasXYZUrl():
            # create XYZ layer
            layer, url = self.createXYZLayer(layerType,
                                             layerType.displayName)
        else:
            # create OpenlayersLayer
            layer = OpenlayersLayer(self.iface, self._olLayerTypeRegistry)
            layer.setName(layerType.displayName)
            layer.setLayerType(layerType)

            if layer.isValid():
                coordRefSys = layerType.coordRefSys(self.canvasCrs())
                self.setMapCrs(coordRefSys)
                QgsProject.instance().addMapLayer(layer)

                self._ol_layers += [layer]

                # last added layer is new reference
                self.setReferenceLayer(layer)

    def setReferenceLayer(self, layer):
        self.layer = layer

    def removeLayer(self, layerId):
        if self.layer is not None:
            if self.layer.id() == layerId:
                self.layer = None
            # TODO: switch to next available OpenLayers layer?

    def canvasCrs(self):
        mapCanvas = self.iface.mapCanvas()
        crs = mapCanvas.mapSettings().destinationCrs()
        return crs

    def setMapCrs(self, targetCRS):
        mapCanvas = self.iface.mapCanvas()
        mapExtent = mapCanvas.extent()

        sourceCRS = self.canvasCrs()
        QgsProject.instance().setCrs(targetCRS)
        mapCanvas.freeze(False)
        with contextlib.suppress(Exception):
            coordTrans = QgsCoordinateTransform(sourceCRS, targetCRS, QgsProject.instance())
            mapExtent = coordTrans.transform(mapExtent, Qgis.TransformDirection.Forward)
            mapCanvas.setExtent(mapExtent)

    def projectLoaded(self):
        # replace old OpenlayersLayer with XYZ layer(OL plugin <= 1.3.6)
        rootGroup = self.iface.layerTreeView().layerTreeModel().rootGroup()
        for layer in QgsProject.instance().mapLayers().values():
            if layer.type() == Qgis.LayerType.PluginLayer and layer.pluginLayerType() == OpenlayersLayer.LAYER_TYPE:
                # Defensive: readXml may have set layerType=None when the
                # stored ol_layer_type is unregistered and OSM fallback is absent.
                if layer.layerType is None:
                    continue
                if layer.layerType.hasXYZUrl():
                    # replace layer
                    xyzLayer, url = self.createXYZLayer(layer.layerType,
                                                        layer.name())
                    if xyzLayer.isValid():
                        self.replaceLayer(rootGroup, layer, xyzLayer)

    def _hasOlLayer(self):
        for layer in QgsProject.instance().mapLayers().values():
            if layer.customProperty("ol_layer_type"):
                return True
        return False

    def _publicationInfo(self):
        cloud_info_off = QSettings().value("Plugin-OpenLayers/cloud_info_off",
                                           defaultValue=False, type=bool)
        day = 3600*24
        now = time.time()
        lastInfo = QSettings().value("Plugin-OpenLayers/cloud_info_ts",
                                     defaultValue=0.0, type=float)
        if lastInfo == 0.0:
            lastInfo = now-20*day  # Show first time after 10 days
            QSettings().setValue("Plugin-OpenLayers/cloud_info_ts", lastInfo)
        days = (now-lastInfo)/day
        if days >= 30 and not cloud_info_off:
            dlg = self._getAboutDialog()
            dlg.tabWidget.setCurrentWidget(dlg.tab_publishing)
            dlg.show()
            QSettings().setValue("Plugin-OpenLayers/cloud_info_ts", now)

    def _publicationInfoClosed(self):
        QSettings().setValue("Plugin-OpenLayers/cloud_info_off",
                             self.dlgAbout.cb_publishing.isChecked())

    def projectSaved(self):
        if self._hasOlLayer():
            self._publicationInfo()

    @staticmethod
    def _buildXYZUri(xyzUrl, tilePixelRatio):
        # Mirror the URI shape that QGIS's native XYZ connection dialog
        # produces: type=xyz first, raw URL template, then zoom bounds.
        # The URL template MUST stay literal so the wms/xyz provider can
        # substitute {z}/{x}/{y} per-tile.  If the template contains '&'
        # (multi-param query), encode only that character to keep the
        # outer URI parseable.
        safeUrl = xyzUrl.replace('&', '%26')
        uri = "type=xyz&url=" + safeUrl + "&zmin=0&zmax=18"
        if tilePixelRatio and tilePixelRatio > 0:
            uri = uri + "&tilePixelRatio=" + str(tilePixelRatio)
        return uri

    def _logXYZAttempt(self, layerName, xyzUrl, uri, layer):
        # Surface enough information for the user (and for bug reports)
        # to understand exactly what the plugin asked QGIS to fetch and
        # whether QGIS accepted the layer as valid.
        valid = layer.isValid() if layer is not None else False
        msg = (
            "Adding XYZ layer '%s'\n  url template: %s\n  uri: %s\n  valid: %s"
            % (layerName, xyzUrl, uri, valid)
        )
        QgsMessageLog.logMessage(msg, "TMS for Korea", Qgis.MessageLevel.Info)
        if not valid:
            self.iface.messageBar().pushMessage(
                "TMS for Korea",
                "레이어 '%s'를 추가할 수 없습니다. '로그 메시지 > TMS for Korea'에서 상세 내용을 확인하세요." % layerName,
                level=Qgis.MessageLevel.Warning,
            )

    def createXYZLayer(self, layerType, name):
        # create XYZ layer with tms url as uri
        provider = "wms"

        # isinstance(P, (list, tuple, np.ndarray))
        xyzUrls = layerType.xyzUrlConfig()
        layerName = name
        tilePixelRatio = layerType.tilePixelRatio

        coordRefSys = layerType.coordRefSys(self.canvasCrs())
        self.setMapCrs(coordRefSys)

        if isinstance(xyzUrls, (list)):
            # create group layer
            root = QgsProject.instance().layerTreeRoot()
            layer = root.addGroup(layerType.groupName)

            i = 0
            for xyzUrl in xyzUrls:
                tmsLayerName = layerName;

                # URI format matches QGIS's own qgsxyzconnectiondialog.cpp:
                # type=xyz comes first; url= holds the RAW template (the
                # XYZ provider tolerates ?query strings; aggressive
                # percent-encoding hides the URL from the substitutor and
                # breaks providers like Naver that embed ?mt=... params).
                uri = self._buildXYZUri(xyzUrl, tilePixelRatio)

                if i > 0:
                    tmsLayerName = layerName + " Label"

                tmsLayer = QgsRasterLayer(uri, tmsLayerName, provider, QgsRasterLayer.LayerOptions())
                tmsLayer.setCustomProperty("ol_layer_type", tmsLayerName)

                self._logXYZAttempt(tmsLayerName, xyzUrl, uri, tmsLayer)

                layer.insertChildNode(0, QgsLayerTreeLayer(tmsLayer))
                i = i + 1

                if tmsLayer.isValid():
                    QgsProject.instance().addMapLayer(tmsLayer, False)
                    self._ol_layers += [tmsLayer]

                    # last added layer is new reference
                    self.setReferenceLayer(tmsLayer)
                    # add to XYT Tiles
                    self.addToXYZTiles(tmsLayerName, xyzUrl, tilePixelRatio)
        else:
            uri = self._buildXYZUri(xyzUrls, tilePixelRatio)

            layer = QgsRasterLayer(uri, layerName, provider, QgsRasterLayer.LayerOptions())
            layer.setCustomProperty("ol_layer_type", layerName)

            self._logXYZAttempt(layerName, xyzUrls, uri, layer)

            if layer.isValid():
                QgsProject.instance().addMapLayer(layer)
                self._ol_layers += [layer]

                # last added layer is new reference
                self.setReferenceLayer(layer)
                # add to XYT Tiles
                self.addToXYZTiles(layerName, xyzUrls, tilePixelRatio)

        # reload connections to update Browser Panel content
        self.iface.reloadConnections()

        return layer, xyzUrls

    def addToXYZTiles(self, name, url, tilePixelRatio):
        # store xyz config into qgis settings
        settings = QSettings()
        settings.beginGroup("qgis/connections-xyz")
        settings.setValue("%s/authcfg" % (name), "")
        settings.setValue("%s/password" % (name), "")
        settings.setValue("%s/referer" % (name), "")
        settings.setValue("%s/url" % (name), url)
        settings.setValue("%s/username" % (name), "")
        # specify max/min or else only a picture of the map is saved in settings
        settings.setValue("%s/zmax" % (name), "18")
        settings.setValue("%s/zmin" % (name), "0")
        if tilePixelRatio >= 0 and tilePixelRatio <= 2:
            settings.setValue("%s/tilePixelRatio" % (name), str(tilePixelRatio))
        settings.endGroup()

    def replaceLayer(self, group, oldLayer, newLayer):
        index = 0
        for child in group.children():
            if QgsLayerTree.isLayer(child):
                if child.layerId() == oldLayer.id():
                    # insert new layer
                    QgsProject.instance().addMapLayer(newLayer, False)
                    newLayerNode = group.insertLayer(index, newLayer)
                    newLayerNode.setVisible(child.isVisible())

                    # remove old layer
                    QgsProject.instance().removeMapLayer(
                        oldLayer.id())

                    msg = "이전 OpenLayers 플러그인 버전의 레이어 '%s'를 새 형식으로 변환했습니다." % newLayer.name()
                    self.iface.messageBar().pushMessage(
                        "OpenLayers Plugin", msg, level=Qgis.MessageLevel.Info)
                    QgsMessageLog.logMessage(
                        msg, "OpenLayers Plugin", Qgis.MessageLevel.Info)

                    # layer replaced
                    return True
            else:
                if self.replaceLayer(child, oldLayer, newLayer):
                    # layer replaced in child group
                    return True

            index += 1

        # layer not in this group
        return False
