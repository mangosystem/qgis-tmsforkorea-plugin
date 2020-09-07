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

from .weblayer import WebLayer3857


class OlMangoMapsLayer(WebLayer3857):

    # Group in menu
    groupName = 'Mango Maps'
    
    # Group icon in menu
    groupIcon = 'mango_icon.png'
    
    # Supported EPSG projections, ordered by preference
    epsgList = [3857]
    
    # WGS84 bounds
    fullExtent = [124.41714675, 33.0022776231, 131.971482078, 38.6568782776]
    
    MIN_ZOOM_LEVEL = 6

    MAX_ZOOM_LEVEL = 17
    
    # QGIS scale for 72 dpi
    SCALE_ON_MAX_ZOOM = 13540
    
    emitsLoadEnd = False
    
    def __init__(self, name, html, xyzUrl, tilePixelRatio=0):
        WebLayer3857.__init__(self, groupName=self.groupName, groupIcon=self.groupIcon,
                              name=name, html=html, xyzUrl=xyzUrl, tilePixelRatio=0)  # Temporary


class OlMangoBaseMapLayer(OlMangoMapsLayer):

    def __init__(self):
        tmsUrl = 'http://mango.iptime.org:8995/v.1.0.0/{z}/{x}/{y}.png?gray=false'
        OlMangoMapsLayer.__init__(self, name='Mango BaseMap', html='mango_base.html', xyzUrl=tmsUrl, tilePixelRatio=1)


class OlMangoBaseMapGrayLayer(OlMangoMapsLayer):

    def __init__(self):
        tmsUrl = 'http://mango.iptime.org:8995/v.1.0.0/{z}/{x}/{y}.png?gray=true'
        OlMangoMapsLayer.__init__(self, name='Mango BaseMap Gray', html='mango_base_gray.html', xyzUrl=tmsUrl, tilePixelRatio=1)


class OlMangoHiDPIMapLayer(OlMangoMapsLayer):

    def __init__(self):
        tmsUrl = 'http://mango.iptime.org:8996/v.1.0.0/{z}/{x}/{y}.png?gray=false'
        OlMangoMapsLayer.__init__(self, name='Mango BaseMap HiDPI', html='mango_hidpi.html', xyzUrl=tmsUrl, tilePixelRatio=2)


class OlMangoHiDPIMapGrayLayer(OlMangoMapsLayer):

    def __init__(self):
        tmsUrl = 'http://mango.iptime.org:8996/v.1.0.0/{z}/{x}/{y}.png?gray=true'
        OlMangoMapsLayer.__init__(self, name='Mango BaseMap HiDPI Gray', html='mango_hidpi_gray.html', xyzUrl=tmsUrl, tilePixelRatio=2)
