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


class OlVWorldMapsLayer(WebLayer3857):

    # Group in menu
    groupName = 'VWorld Maps'

    # Group icon in menu
    groupIcon = 'vworld_icon.png'

    # Supported EPSG projections, ordered by preference
    epsgList = [3857]

    # WGS84 bounds
    fullExtent = [124.41714675, 33.0022776231, 131.971482078, 38.6568782776]

    MIN_ZOOM_LEVEL = 7

    MAX_ZOOM_LEVEL = 18

    # QGIS scale for 72 dpi
    SCALE_ON_MAX_ZOOM = 13540

    emitsLoadEnd = False

    def __init__(self, name, html, xyzUrl, tilePixelRatio=0):
        WebLayer3857.__init__(self, groupName=self.groupName, groupIcon=self.groupIcon,
                              name=name, html=html, xyzUrl=xyzUrl, tilePixelRatio=0) # Temporary


class OlVWorldStreetLayer(OlVWorldMapsLayer):

    def __init__(self):
        tmsUrl = 'https://xdworld.vworld.kr/2d/Base/service/{z}/{x}/{y}.png'
        OlVWorldMapsLayer.__init__(self, name='VWorld Street', html='vworld_street.html', xyzUrl=tmsUrl, tilePixelRatio=1)


class OlVWorldHybridLayer(OlVWorldMapsLayer):

    def __init__(self):
        tmsUrl = ['https://xdworld.vworld.kr/2d/Satellite/service/{z}/{x}/{y}.jpeg', 'https://xdworld.vworld.kr/2d/Hybrid/service/{z}/{x}/{y}.png']
        OlVWorldMapsLayer.__init__(self, name='VWorld Hybrid', html='vworld_hybrid.html', xyzUrl=tmsUrl, tilePixelRatio=1)


class OlVWorldSatelliteLayer(OlVWorldMapsLayer):

    def __init__(self):
        tmsUrl = 'https://xdworld.vworld.kr/2d/Satellite/service/{z}/{x}/{y}.jpeg'
        OlVWorldMapsLayer.__init__(self, name='VWorld Satellite', html='vworld_satellite.html', xyzUrl=tmsUrl, tilePixelRatio=1)


class OlVWorldGrayLayer(OlVWorldMapsLayer):

    def __init__(self):
        tmsUrl = 'https://xdworld.vworld.kr/2d/gray/service/{z}/{x}/{y}.png'
        OlVWorldMapsLayer.__init__(self, name='VWorld Gray', html='vworld_gray.html', xyzUrl=tmsUrl, tilePixelRatio=1)
