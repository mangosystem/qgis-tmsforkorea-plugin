# -*- coding: utf-8 -*-
"""
/***************************************************************************
OpenLayers Plugin
A QGIS plugin

                             -------------------
begin                : 2018-11-23
copyright            : (C) 2009 by Minpa Lee, MangoSystem
email                : mapplus at gmail.com
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

from qgis.core import (Qgis, QgsCoordinateReferenceSystem)
from .weblayer import WebLayer


class WebLayerDaum5181(WebLayer):

    # QGIS scale for 72 dpi
    SCALE_ON_MAX_ZOOM = 13540
    
    emitsLoadEnd = False
    
    def __init__(self, groupName, groupIcon, name, html, xyzUrl=None):
        WebLayer.__init__(self, groupName=groupName, groupIcon=groupIcon,
                              name=name, html=html, xyzUrl=xyzUrl)

    def coordRefSys(self, mapCoordSys):
        epsg = self.epsgList[0]
        coordRefSys = QgsCoordinateReferenceSystem()
        if Qgis.QGIS_VERSION_INT >= 10900:
            idEpsgRSGoogle = "EPSG:%d" % epsg
            createCrs = coordRefSys.createFromOgcWmsCrs(idEpsgRSGoogle)
        else:
            idEpsgRSGoogle = epsg
            createCrs = coordRefSys.createFromEpsg(idEpsgRSGoogle)
        if not createCrs:
            proj_def =  "+proj=tmerc +lat_0=38 +lon_0=127 +k=1 +x_0=200000 +y_0=500000 +ellps=GRS80 "
            proj_def += "+towgs84=0,0,0,0,0,0,0 +units=m +no_defs"
            isOk = coordRefSys.createFromProj4(proj_def)
            if not isOk:
                return None
        return coordRefSys


class OlDaumMapsLayer(WebLayerDaum5181):

    # Group in menu
    groupName = 'Daum Maps'
    
    # Group icon in menu
    groupIcon = 'daum_icon.png'
    
    # Supported EPSG projections, ordered by preference
    epsgList = [5181]
    
    # EPSG 5181 bounds
    fullExtent = [-30000, -60000, 494288, 988576]
    
    MIN_ZOOM_LEVEL = 0

    MAX_ZOOM_LEVEL = 14

    def __init__(self, name, html, xyzUrl=None):
        WebLayerDaum5181.__init__(self, groupName=self.groupName, groupIcon=self.groupIcon,
                              name=name, html=html, xyzUrl=xyzUrl)


class OlDaumStreetLayer(OlDaumMapsLayer):

    def __init__(self):
        OlDaumMapsLayer.__init__(self, name='Daum Street', html='daum_street.html', xyzUrl=None)


class OlDaumHybridLayer(OlDaumMapsLayer):

    def __init__(self):
        OlDaumMapsLayer.__init__(self, name='Daum Hybrid', html='daum_hybrid.html', xyzUrl=None)


class OlDaumSatelliteLayer(OlDaumMapsLayer):

    def __init__(self):
        OlDaumMapsLayer.__init__(self, name='Daum Satellite', html='daum_satellite.html', xyzUrl=None)


class OlDaumPhysicalLayer(OlDaumMapsLayer):

    def __init__(self):
        OlDaumMapsLayer.__init__(self, name='Daum Physical', html='daum_physical.html', xyzUrl=None)


class OlDaumCadstralLayer(OlDaumMapsLayer):

    def __init__(self):
        OlDaumMapsLayer.__init__(self, name='Daum Cadstral', html='daum_cadastral.html', xyzUrl=None)
