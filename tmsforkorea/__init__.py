# -*- coding: utf-8 -*-
"""
/***************************************************************************
OpenLayers Plugin
A QGIS plugin

                             -------------------
begin                : 2010-02-03
copyright            : (C) 2009 by Pirmin Kalberer, Sourcepole
email                : pka at sourcepole.ch
modified             : (C) 2013 by Minpa Lee, mapplus@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

##lines for eclipse debug. Comment me when publishing.
##Use DEBUG Perspective and Start the pydev server
#import os, sys
#sys.path.append(r"C:\eclipse\plugins\org.python.pydev.debug_1.6.5.2011022818\pysrc")
#import pydevd
#pydevd.settrace()
##end of eclipse debug

def name():
    return "TMS for Korea"
  
def description():
    return "Daum, Naver, Olleh, VWorld Map Layers for Korean users"
  
def version():
    return "0.5.1"
  
def qgisMinimumVersion():
    return "2.0"
  
def authorName():
    return "Minpa Lee"
  
def icon():
    return "openlayers.png"

def homepage():
    return "http://onspatial.com"
  
def classFactory(iface):
    from openlayers_plugin import OpenlayersPlugin
    return OpenlayersPlugin(iface)
