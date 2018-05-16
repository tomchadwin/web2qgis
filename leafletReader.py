# -*- coding: utf-8 -*-
"""
/***************************************************************************
 leaflet
                                 A QGIS plugin
 Load a webmap directly into QGIS
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2018-05-11
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Tom Chadwin
        email                : tom.chadwin@nnpa.org.uk
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

import os

from web2qgis.utils import getTempDir, getScript
from web2qgis.qgisWriter import addWMS, addXYZ, addVector, setExtent

def detectLeaflet(mainframe):
    detectResult = mainframe.evaluateJavaScript("L.version")
    if detectResult is None:
        result = False
    else:
        result = True
    return result

def getLeafletMap(mainframe, iface):
    tempDir = getTempDir()
    scriptFolder = os.path.join(os.path.dirname(__file__), "js")

    getMapScript = getScript(scriptFolder, "getLeafletMap.js")
    lyrs = mainframe.evaluateJavaScript(getMapScript)
    for count, lyr in enumerate(lyrs):
        if lyr[0] == "wms":
            addWMS(lyr[1], lyr[2], lyr[3], iface)
        elif lyr[0] == "xyz":
            addXYZ(lyr[1], lyr[2], iface)
        elif lyr[0] == "vector":
            addVector(lyr[1], count, tempDir)
        else:
            print("Unsupported layer type")

    getLeafletView(scriptFolder, mainframe, iface)

def getLeafletView(scriptFolder, mainframe, iface):
    getExtentScript = getScript(scriptFolder, "getLeafletView.js")
    extent = mainframe.evaluateJavaScript(getExtentScript)
    xMin, yMin, xMax, yMax = extent.split(",")
    setExtent(xMin, yMin, xMax, yMax, iface)
