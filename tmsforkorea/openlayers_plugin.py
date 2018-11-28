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
from qgis.PyQt.QtCore import (QSettings, QTranslator, QCoreApplication, qVersion)
from qgis.PyQt.QtWidgets import (QApplication, QLineEdit, QInputDialog,
                                 QAction, QMenu)
from qgis.PyQt.QtGui import QIcon
from qgis.core import (QgsCoordinateTransform, Qgis, QgsProject,
                       QgsPluginLayerRegistry, QgsLayerTree, QgsMapLayer,
                       QgsRasterLayer, QgsMessageLog)

from . import resources_rc
from .about_dialog import AboutDialog
from .openlayers_overview import OLOverview
from .openlayers_layer import OpenlayersLayer
from .openlayers_plugin_layer_type import OpenlayersPluginLayerType
from .weblayers.weblayer_registry import WebLayerTypeRegistry

from .weblayers.vworld_maps import (OlVWorldStreetLayer,
                                    OlVWorldSatelliteLayer,
                                    OlVWorldGrayLayer,
                                    OlVWorldHybridLayer)

from .weblayers.daum_maps import (OlDaumStreetLayer,
                                  OlDaumHybridLayer,
                                  OlDaumSatelliteLayer,
                                  OlDaumPhysicalLayer,
                                  OlDaumCadstralLayer)

from .weblayers.naver_maps import (OlNaverStreetLayer,
                                   OlNaverHybridLayer,
                                   OlNaverSatelliteLayer,
                                   OlNaverPhysicalLayer,
                                   OlNaverCadastralLayer)

from .weblayers.ngii_maps import (OlNgiiStreetLayer,
                                  OlNgiiBlankLayer,
                                  OlNgiiEnglishLayer,
                                  OlNgiiHighDensityLayer,
                                  OlNgiiColorBlindLayer)

from .weblayers.mango_maps import (OlMangoBaseMapLayer,
                                   OlMangoBaseMapGrayLayer,
                                   OlMangoHiDPIMapLayer,
                                   OlMangoHiDPIMapGrayLayer)
                                    
import os.path
import time


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
            
            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        self._olLayerTypeRegistry = WebLayerTypeRegistry(self)
        self.olOverview = OLOverview(iface, self._olLayerTypeRegistry)
        self.dlgAbout = AboutDialog()
        self.pluginLayerRegistry = QgsPluginLayerRegistry()

    def initGui(self):
        self._olMenu = QMenu("TMS for Korea")
        self._olMenu.setIcon(QIcon(":/plugins/openlayers/openlayers.png"))

        # Overview
        self.overviewAddAction = QAction(QApplication.translate("OpenlayersPlugin", "OpenLayers Overview"), self.iface.mainWindow())
        self.overviewAddAction.setCheckable(True)
        self.overviewAddAction.setChecked(False)
        self.overviewAddAction.toggled.connect(self.olOverview.setVisible)
        self._olMenu.addAction(self.overviewAddAction)

        self._actionAbout = QAction(QApplication.translate("dlgAbout", "About OpenLayers Plugin"), self.iface.mainWindow())
        self._actionAbout.triggered.connect(self.dlgAbout.show)
        self._olMenu.addAction(self._actionAbout)
        self.dlgAbout.finished.connect(self._publicationInfoClosed)
        
        # Daum
        self._olLayerTypeRegistry.register(OlDaumStreetLayer())
        self._olLayerTypeRegistry.register(OlDaumHybridLayer())
        self._olLayerTypeRegistry.register(OlDaumSatelliteLayer())
        self._olLayerTypeRegistry.register(OlDaumPhysicalLayer())
        self._olLayerTypeRegistry.register(OlDaumCadstralLayer())
        
        # Naver
        self._olLayerTypeRegistry.register(OlNaverStreetLayer())
        self._olLayerTypeRegistry.register(OlNaverHybridLayer())
        self._olLayerTypeRegistry.register(OlNaverSatelliteLayer())
        self._olLayerTypeRegistry.register(OlNaverPhysicalLayer())
        self._olLayerTypeRegistry.register(OlNaverCadastralLayer())
        
        # VWorld
        self._olLayerTypeRegistry.register(OlVWorldStreetLayer())
        self._olLayerTypeRegistry.register(OlVWorldSatelliteLayer())
        self._olLayerTypeRegistry.register(OlVWorldGrayLayer())
        self._olLayerTypeRegistry.register(OlVWorldHybridLayer())
        
        # NGII
        self._olLayerTypeRegistry.register(OlNgiiStreetLayer())
        self._olLayerTypeRegistry.register(OlNgiiBlankLayer())
        self._olLayerTypeRegistry.register(OlNgiiEnglishLayer())
        self._olLayerTypeRegistry.register(OlNgiiHighDensityLayer())
        self._olLayerTypeRegistry.register(OlNgiiColorBlindLayer())
        
        # Mango
        self._olLayerTypeRegistry.register(OlMangoBaseMapLayer())
        self._olLayerTypeRegistry.register(OlMangoBaseMapGrayLayer())
        self._olLayerTypeRegistry.register(OlMangoHiDPIMapLayer())
        self._olLayerTypeRegistry.register(OlMangoHiDPIMapGrayLayer())
        
        for group in self._olLayerTypeRegistry.groups():
            groupMenu = group.menu()
            for layer in self._olLayerTypeRegistry.groupLayerTypes(group):
                layer.addMenuEntry(groupMenu, self.iface.mainWindow())
            self._olMenu.addMenu(groupMenu)
            
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

        self.olOverview.setVisible(False)
        del self.olOverview

        # Unregister plugin layer type
        self.pluginLayerRegistry.removePluginLayerType(
            OpenlayersLayer.LAYER_TYPE)

        QgsProject.instance().readProject.disconnect(self.projectLoaded)
        QgsProject.instance().projectSaved.disconnect(self.projectSaved)

    def addLayer(self, layerType):
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

            # store xyz config into qgis settings
            if layerType.hasXYZUrl():
                settings = QSettings()
                settings.beginGroup('qgis/connections-xyz')
                settings.setValue("%s/authcfg" % (layer.name()), '')
                settings.setValue("%s/password" % (layer.name()), '')
                settings.setValue("%s/referer" % (layer.name()), '')
                settings.setValue("%s/url" % (layer.name()), url)
                settings.setValue("%s/username" % (layer.name()), '')
                # specify max/min or else only a picture of the map is saved
                # in settings
                settings.setValue("%s/zmax" % (layer.name()), '18')
                settings.setValue("%s/zmin" % (layer.name()), '0')
                settings.endGroup()
                # reload connections to update Browser Panel content
                self.iface.reloadConnections()

            self._ol_layers += [layer]

            # last added layer is new reference
            self.setReferenceLayer(layer)

            if not layerType.hasXYZUrl():
                msg = "Printing and rotating of Javascript API " \
                      "based layers is currently not supported!"
                self.iface.messageBar().pushMessage(
                    "OpenLayers Plugin", msg, level=Qgis.MessageLevel(1),
                    duration=5)

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
        try:
            coordTrans = QgsCoordinateTransform(sourceCRS, targetCRS, QgsProject.instance())
            mapExtent = coordTrans.transform(mapExtent, QgsCoordinateTransform.ForwardTransform)
            mapCanvas.setExtent(mapExtent)
        except:
            pass

    def projectLoaded(self):
        # replace old OpenlayersLayer with XYZ layer(OL plugin <= 1.3.6)
        rootGroup = self.iface.layerTreeView().layerTreeModel().rootGroup()
        for layer in QgsProject.instance().mapLayers().values():
            if layer.type() == QgsMapLayer.PluginLayer and layer.pluginLayerType() == OpenlayersLayer.LAYER_TYPE:
                if layer.layerType.hasXYZUrl():
                    # replace layer
                    xyzLayer, url = self.createXYZLayer(layer.layerType,
                                                        layer.name())
                    if xyzLayer.isValid():
                        self.replaceLayer(rootGroup, layer, xyzLayer)

    def _hasOlLayer(self):
        for layer in QgsProject.instance().mapLayers().values():
            if layer.customProperty('ol_layer_type'):
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
            self.dlgAbout.tabWidget.setCurrentWidget(
                self.dlgAbout.tab_publishing)
            self.dlgAbout.show()
            QSettings().setValue("Plugin-OpenLayers/cloud_info_ts", now)

    def _publicationInfoClosed(self):
        QSettings().setValue("Plugin-OpenLayers/cloud_info_off",
                             self.dlgAbout.cb_publishing.isChecked())

    def projectSaved(self):
        if self._hasOlLayer():
            self._publicationInfo()

    def createXYZLayer(self, layerType, name):
        # create XYZ layer with tms url as uri
        provider = 'wms'
        url = "type=xyz&url=" + layerType.xyzUrlConfig()
        layer = QgsRasterLayer(url, name, provider,
                               QgsRasterLayer.LayerOptions())
        layer.setCustomProperty('ol_layer_type', layerType.layerTypeName)
        return layer, layerType.xyzUrlConfig()

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

                    msg = "Updated layer '%s' from old \
                     OpenLayers Plugin version" % newLayer.name()
                    self.iface.messageBar().pushMessage(
                        "OpenLayers Plugin", msg, level=Qgis.MessageLevel(0))
                    QgsMessageLog.logMessage(
                        msg, "OpenLayers Plugin", QgsMessageLog.INFO)

                    # layer replaced
                    return True
            else:
                if self.replaceLayer(child, oldLayer, newLayer):
                    # layer replaced in child group
                    return True

            index += 1

        # layer not in this group
        return False
