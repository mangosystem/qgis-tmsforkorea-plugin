# -*- coding: utf-8 -*-
"""
/***************************************************************************
OpenLayers Plugin
A QGIS plugin

                             -------------------
begin                : 2009-11-30
copyright            : (C) 2009 by Pirmin Kalberer, Sourcepole
email                : pka at sourcepole.ch
modified             : 2014-09-19 by Minpa Lee, mapplus at gmail.com
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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import resources_rc
from about_dialog import AboutDialog
from openlayers_overview import OLOverview
from openlayers_layer import OpenlayersLayer
from openlayers_plugin_layer_type import OpenlayersPluginLayerType
from weblayers.weblayer_registry import WebLayerTypeRegistry
# from weblayers.google_maps import OlGooglePhysicalLayer, OlGoogleStreetsLayer, OlGoogleHybridLayer, OlGoogleSatelliteLayer
# from weblayers.osm import OlOpenStreetMapLayer, OlOpenCycleMapLayer, OlOCMLandscapeLayer, OlOCMPublicTransportLayer
# from weblayers.yahoo_maps import OlYahooStreetLayer, OlYahooHybridLayer, OlYahooSatelliteLayer
# from weblayers.bing_maps import OlBingRoadLayer, OlBingAerialLayer, OlBingAerialLabelledLayer
# from weblayers.apple_maps import OlAppleiPhotoMapLayer
# from weblayers.osm_stamen import OlOSMStamenTonerLayer, OlOSMStamenWatercolorLayer, OlOSMStamenTerrainLayer
import os.path

# TMS for Korea 2014-09-19
from weblayers.vworld_maps import OlVWorldStreetLayer, OlVWorldGrayLayer, OlVWorldHybridLayer, OlVWorldSatelliteLayer
from weblayers.daum_maps import OlDaumStreetLayer, OlDaumHybridLayer, OlDaumSatelliteLayer, OlDaumPhysicalLayer
from weblayers.naver_maps import OlNaverStreetLayer, OlNaverHybridLayer, OlNaverSatelliteLayer, OlNaverPhysicalLayer, OlNaverCadastralLayer
from weblayers.olleh_maps import OlOllehStreetLayer, OlOllehHybridLayer, OlOllehSatelliteLayer, OlOllehPhysicalLayer


class OpenlayersPlugin:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
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

    def initGui(self):
        self._olMenu = QMenu("TMS for Korea")
        self._olMenu.setIcon(QIcon(":/plugins/tmsforkorea/openlayers.png"))

        # Overview
        self.overviewAddAction = QAction(QApplication.translate("OpenlayersPlugin", "OpenLayers Overview"), self.iface.mainWindow())
        self.overviewAddAction.setCheckable(True)
        self.overviewAddAction.setChecked(False)
        QObject.connect(self.overviewAddAction, SIGNAL("toggled(bool)"), self.olOverview.setVisible)
        self._olMenu.addAction(self.overviewAddAction)

        # Terms of Service
        self._actionAbout = QAction(QApplication.translate("OpenlayersPlugin", "Terms of Service / About"), self.iface.mainWindow())
        QObject.connect(self._actionAbout, SIGNAL("triggered()"), self.dlgAbout, SLOT("show()"))
        #? self._actionAbout.triggered.connect(self.dlgAbout, SLOT("show()"))
        self._olMenu.addAction(self._actionAbout)

        # OpenLayers plugin layers
        """
        self._olLayerTypeRegistry.register(OlGooglePhysicalLayer())
        self._olLayerTypeRegistry.register(OlGoogleStreetsLayer())
        self._olLayerTypeRegistry.register(OlGoogleHybridLayer())
        self._olLayerTypeRegistry.register(OlGoogleSatelliteLayer())

        self._olLayerTypeRegistry.register(OlOpenStreetMapLayer())
        self._olLayerTypeRegistry.register(OlOpenCycleMapLayer())
        self._olLayerTypeRegistry.register(OlOCMLandscapeLayer())
        self._olLayerTypeRegistry.register(OlOCMPublicTransportLayer())

        self._olLayerTypeRegistry.register(OlYahooStreetLayer())
        self._olLayerTypeRegistry.register(OlYahooHybridLayer())
        self._olLayerTypeRegistry.register(OlYahooSatelliteLayer())

        self._olLayerTypeRegistry.register(OlBingRoadLayer())
        self._olLayerTypeRegistry.register(OlBingAerialLayer())
        self._olLayerTypeRegistry.register(OlBingAerialLabelledLayer())

        self._olLayerTypeRegistry.register(OlOSMStamenTonerLayer())
        self._olLayerTypeRegistry.register(OlOSMStamenWatercolorLayer())
        self._olLayerTypeRegistry.register(OlOSMStamenTerrainLayer())

        self._olLayerTypeRegistry.register(OlAppleiPhotoMapLayer())
        """
        
        # TMS for Korea 2014-09-19
        self._olLayerTypeRegistry.register(OlDaumStreetLayer())
        self._olLayerTypeRegistry.register(OlDaumHybridLayer())
        self._olLayerTypeRegistry.register(OlDaumSatelliteLayer())
        self._olLayerTypeRegistry.register(OlDaumPhysicalLayer())
        
        self._olLayerTypeRegistry.register(OlNaverStreetLayer())
        self._olLayerTypeRegistry.register(OlNaverHybridLayer())
        self._olLayerTypeRegistry.register(OlNaverSatelliteLayer())
        self._olLayerTypeRegistry.register(OlNaverPhysicalLayer())
        self._olLayerTypeRegistry.register(OlNaverCadastralLayer())
        
        self._olLayerTypeRegistry.register(OlOllehStreetLayer())
        self._olLayerTypeRegistry.register(OlOllehHybridLayer())
        self._olLayerTypeRegistry.register(OlOllehSatelliteLayer())
        self._olLayerTypeRegistry.register(OlOllehPhysicalLayer())
        
        self._olLayerTypeRegistry.register(OlVWorldStreetLayer())
        self._olLayerTypeRegistry.register(OlVWorldGrayLayer())
        self._olLayerTypeRegistry.register(OlVWorldHybridLayer())
        self._olLayerTypeRegistry.register(OlVWorldSatelliteLayer())

        for group in self._olLayerTypeRegistry.groups():
            groupMenu = group.menu()
            for layer in self._olLayerTypeRegistry.groupLayerTypes(group):
                layer.addMenuEntry(groupMenu, self.iface.mainWindow())
            self._olMenu.addMenu(groupMenu)

        #Create Web menu, if it doesn't exist yet
        self.iface.addPluginToWebMenu("_tmp", self._actionAbout)
        self._menu = self.iface.webMenu()
        self._menu.addMenu(self._olMenu)
        self.iface.removePluginWebMenu("_tmp", self._actionAbout)

        # Register plugin layer type
        pluginLayerType = OpenlayersPluginLayerType(self.iface, self.setReferenceLayer,
                                                    self._olLayerTypeRegistry)
        QgsPluginLayerRegistry.instance().addPluginLayerType(pluginLayerType)

    def unload(self):
        self.iface.webMenu().removeAction(self._olMenu.menuAction())

        self.olOverview.setVisible(False)
        del self.olOverview

        # Unregister plugin layer type
        QgsPluginLayerRegistry.instance().removePluginLayerType(OpenlayersLayer.LAYER_TYPE)

    def addLayer(self, layerType):
        layer = OpenlayersLayer(self.iface, self._olLayerTypeRegistry)
        layer.setLayerName(layerType.displayName)
        layer.setLayerType(layerType)
        if layer.isValid():
            coordRefSys = layerType.coordRefSys(self.canvasCrs())
            self.setMapCrs(coordRefSys)
            QgsMapLayerRegistry.instance().addMapLayer(layer)

            # last added layer is new reference
            self.setReferenceLayer(layer)

    def setReferenceLayer(self, layer):
        self.layer = layer

    def removeLayer(self, layerId):
        if self.layer is not None:
            if QGis.QGIS_VERSION_INT >= 10900:
                if self.layer.id() == layerId:
                    self.layer = None
            else:
                if self.layer.getLayerID() == layerId:
                    self.layer = None
            # TODO: switch to next available OpenLayers layer?

    def canvasCrs(self):
        mapCanvas = self.iface.mapCanvas()
        if QGis.QGIS_VERSION_INT >= 20300:
            #crs = mapCanvas.mapRenderer().destinationCrs()
            crs = mapCanvas.mapSettings().destinationCrs()
        elif QGis.QGIS_VERSION_INT >= 10900:
            crs = mapCanvas.mapRenderer().destinationCrs()
        else:
            crs = mapCanvas.mapRenderer().destinationSrs()
        return crs

    def setMapCrs(self, coordRefSys):
        mapCanvas = self.iface.mapCanvas()
        # On the fly
        if QGis.QGIS_VERSION_INT >= 20300:
            mapCanvas.mapSettings().setCrsTransformEnabled(True)
        else:
            mapCanvas.mapRenderer().setProjectionsEnabled(True)
        canvasCrs = self.canvasCrs()
        if canvasCrs != coordRefSys:
            if QGis.QGIS_VERSION_INT >= 20300:
                mapCanvas.setDestinationCrs(coordRefSys)
            elif QGis.QGIS_VERSION_INT >= 10900:
                mapCanvas.mapRenderer().setDestinationCrs(coordRefSys)
            else:
                mapCanvas.mapRenderer().setDestinationSrs(coordRefSys)
            mapCanvas.freeze(False)
            mapCanvas.setMapUnits(coordRefSys.mapUnits())
            try:
                coodTrans = QgsCoordinateTransform(canvasCrs, coordRefSys)
                extMap = mapCanvas.extent()
                extMap = coodTrans.transform(extMap, QgsCoordinateTransform.ForwardTransform)
                mapCanvas.setExtent(extMap)
            except:
                pass