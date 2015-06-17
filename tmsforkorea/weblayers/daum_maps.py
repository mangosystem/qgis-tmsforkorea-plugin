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


class WebLayerDaum5181(WebLayer):

    epsgList = [5181]
    
    fullExtent = [-30000, -60000, 494288, 988576]

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
            proj_def =  "+proj=tmerc +lat_0=38 +lon_0=127 +k=1 +x_0=200000 +y_0=500000 +ellps=GRS80 "
            proj_def += "+towgs84=0,0,0,0,0,0,0 +units=m +no_defs"
            isOk = coordRefSys.createFromProj4(proj_def)
            if not isOk:
                return None
        return coordRefSys


class OlDaumMapsLayer(WebLayerDaum5181):

    emitsLoadEnd = False

    def __init__(self, name, html):
        WebLayerDaum5181.__init__(self, groupName="Daum Maps", groupIcon="daum_icon.png",
                              name=name, html=html)


class OlDaumStreetLayer(OlDaumMapsLayer):

    def __init__(self):
        OlDaumMapsLayer.__init__(self, name='Daum Street', html='daum_street.html')


class OlDaumHybridLayer(OlDaumMapsLayer):

    def __init__(self):
        OlDaumMapsLayer.__init__(self, name='Daum Hybrid', html='daum_hybrid.html')


class OlDaumSatelliteLayer(OlDaumMapsLayer):

    def __init__(self):
        OlDaumMapsLayer.__init__(self, name='Daum Satellite', html='daum_satellite.html')


class OlDaumPhysicalLayer(OlDaumMapsLayer):

    def __init__(self):
        OlDaumMapsLayer.__init__(self, name='Daum Physical', html='daum_physical.html')
