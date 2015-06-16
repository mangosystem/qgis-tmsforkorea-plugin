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

from weblayer import WebLayer3857


class OlVWorldMapsLayer(WebLayer3857):

    emitsLoadEnd = False

    fullExtent = [124.41714675, 33.0022776231, 131.971482078, 38.6568782776]
    """WGS84 bounds"""

    def __init__(self, name, html):
        WebLayer3857.__init__(self, groupName="VWorld Maps", groupIcon="vworld_icon.png",
                              name=name, html=html)


class OlVWorldStreetLayer(OlVWorldMapsLayer):

    def __init__(self):
        OlVWorldMapsLayer.__init__(self, name='VWorld Street', html='vworld_street.html')


class OlVWorldHybridLayer(OlVWorldMapsLayer):

    def __init__(self):
        OlVWorldMapsLayer.__init__(self, name='VWorld Hybrid', html='vworld_hybrid.html')


class OlVWorldSatelliteLayer(OlVWorldMapsLayer):

    def __init__(self):
        OlVWorldMapsLayer.__init__(self, name='VWorld Satellite', html='vworld_satellite.html')


class OlVWorldGrayLayer(OlVWorldMapsLayer):

    def __init__(self):
        OlVWorldMapsLayer.__init__(self, name='VWorld Gray', html='vworld_gray.html')
