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

from qgis.core import QGis, QgsCoordinateReferenceSystem
from weblayer import WebLayer


class WebLayerOlleh5179(WebLayer):

    epsgList = [5179] 
    
    fullExtent = [171162, 1214781, 1744026, 2787645]

    MAX_ZOOM_LEVEL = 14
    SCALE_ON_MAX_ZOOM = 13540  # QGIS scale for 72 dpi

    def coordRefSys(self, mapCoordSys):
        epsg = self.epsgList[0]
        coordRefSys = QgsCoordinateReferenceSystem()
        if QGis.QGIS_VERSION_INT >= 10900:
            idEpsgRSGoogle = "EPSG:%d" % epsg
            createCrs = coordRefSys.createFromOgcWmsCrs(idEpsgRSGoogle)
        else:
            idEpsgRSGoogle = epsg
            createCrs = coordRefSys.createFromEpsg(idEpsgRSGoogle)
        if not createCrs:
            proj_def =  "+proj=tmerc +lat_0=38 +lon_0=127.5 +k=0.9996 +x_0=1000000 +y_0=2000000 +ellps=GRS80 "
            proj_def += "+towgs84=0,0,0,0,0,0,0 +units=m +no_defs"
            isOk = coordRefSys.createFromProj4(proj_def)
            if not isOk:
                return None
        return coordRefSys


class OlOllehMapsLayer(WebLayerOlleh5179):

    emitsLoadEnd = False

    def __init__(self, name, html):
        WebLayerOlleh5179.__init__(self, groupName="Olleh Maps", groupIcon="olleh_icon.png",
                              name=name, html=html)


class OlOllehStreetLayer(OlOllehMapsLayer):

    def __init__(self):
        OlOllehMapsLayer.__init__(self, name='Olleh Street', html='olleh_street.html')


class OlOllehHybridLayer(OlOllehMapsLayer):

    def __init__(self):
        OlOllehMapsLayer.__init__(self, name='Olleh Hybrid', html='olleh_hybrid.html')


class OlOllehSatelliteLayer(OlOllehMapsLayer):

    def __init__(self):
        OlOllehMapsLayer.__init__(self, name='Olleh Satellite', html='olleh_satellite.html')


class OlOllehPhysicalLayer(OlOllehMapsLayer):

    def __init__(self):
        OlOllehMapsLayer.__init__(self, name='Olleh Physical', html='olleh_physical.html')


class OlOllehCadstralLayer(OlOllehMapsLayer):

    def __init__(self):
        OlOllehMapsLayer.__init__(self, name='Olleh Cadstral', html='olleh_cadastral.html')
