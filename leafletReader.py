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

from qgis.core import (QgsSingleSymbolRenderer,
                       QgsCategorizedSymbolRenderer,
                       QgsRendererCategory,
                       QgsGraduatedSymbolRenderer,
                       QgsRendererRange,
                       QgsFillSymbol)

from web2qgis.utils import getTempDir, getScript, getRGBA
from web2qgis.qgisWriter import addWMS, addXYZ, addVector, setExtent

L2Q_STYLES = {
    "weight": "outline_width",
    "color": "color_border",
    "fillColor": "color"
}

L2Q_TYPES = {
    "weight": "float",
    "color": "rgba",
    "fillColor": "rgba"
}

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

    parserScript = getScript(scriptFolder, "esprima.js")
    mainframe.evaluateJavaScript(parserScript)
    getMapScript = getScript(scriptFolder, "getLeafletMap.js")
    lyrs = mainframe.evaluateJavaScript(getMapScript)
    for count, lyr in enumerate(lyrs):
        if lyr[0] == "wms":
            addWMS(lyr[1], lyr[2], lyr[3], iface)
        elif lyr[0] == "xyz":
            addXYZ(lyr[1], lyr[2], iface)
        elif lyr[0] == "vector":
            renderer = getRenderer(lyr[2])
            addVector(lyr[1], renderer, count, tempDir)
        else:
            print("Unsupported layer type")

    getLeafletView(scriptFolder, mainframe, iface)

def getRenderer(leafletStyle):
    if "body" in leafletStyle:
        styleJSON = leafletStyle["body"][0]["body"]["body"]
        if styleJSON[0]["type"] == "SwitchStatement":
            renderer = getCategorizedRenderer(styleJSON[0])
        elif styleJSON[0]["type"] == "IfStatement":
            renderer = getGraduatedRenderer(styleJSON)
        else:
            renderer = getSingleSymbolRenderer(styleJSON[0])
    else:
        renderer = getSingleSymbolRenderer(leafletStyle)
    return renderer

def getSingleSymbolRenderer(styleJSON):
    if "argument" in styleJSON:
        style = getFunctionStyle(styleJSON)
    else:
        style = styleJSON
    symbol = getSymbol(style)
    renderer = QgsSingleSymbolRenderer(symbol)
    return renderer

def getCategorizedRenderer(styleJSON):
    categories = []
    attrName = styleJSON["discriminant"]["arguments"][0]["property"]["value"]
    for case in styleJSON["cases"]:
        try:
            value = case["test"]["value"]
        except:
            value = "web2qgis_ELSE"
        style = getFunctionStyle(case)
        symbol = getSymbol(style)
        category = QgsRendererCategory(value, symbol, value, True)
        categories.append(category)
    renderer = QgsCategorizedSymbolRenderer(attrName, categories)
    return renderer

def getGraduatedRenderer(styleJSON):
    ranges = []
    attrName = styleJSON[0]["test"]["left"]["left"]["property"]["value"]
    print(attrName)
    for case in styleJSON:
        low = case["test"]["left"]["right"]["value"]
        high = case["test"]["right"]["right"]["value"]
        label = "%s-%s" % (low, high)
        style = getFunctionStyle(case)
        symbol = getSymbol(style)
        range = QgsRendererRange(low, high, symbol, label, True)
        ranges.append(range)
    renderer = QgsGraduatedSymbolRenderer(attrName, ranges)
    return renderer

def getFunctionStyle(styleJSON):
    style = walkAST(styleJSON, {})
    return style

def getSymbol(leafletStyle):
    style = {}
    for k, v in leafletStyle.items():
        if k in L2Q_STYLES:
            if L2Q_TYPES[k] == "rgba":
                value = getRGBA(v)
            else:
                value = str(v)
            style[L2Q_STYLES[k]] = value
    style["size_unit"] = "Pixel"
    style["line_width_unit"] = "Pixel"
    style["outline_width_unit"] = "Pixel"
    symbol = QgsFillSymbol.createSimple(style)
    return symbol

def getLeafletView(scriptFolder, mainframe, iface):
    getExtentScript = getScript(scriptFolder, "getLeafletView.js")
    extent = mainframe.evaluateJavaScript(getExtentScript)
    xMin, yMin, xMax, yMax = extent.split(",")
    setExtent(xMin, yMin, xMax, yMax, iface)

def walkAST(node, returnVal):
    if type(node) is list:
        for child in node:
            returnVal = walkAST(child, returnVal)
    elif type(node) is dict:
        if node["type"] == "ReturnStatement":
            for k in node["argument"]["properties"]:
                returnVal[k["key"]["name"]] = k["value"]["value"]
        else:
            for k, v in node.items():
                returnVal = walkAST(v, returnVal)
    return returnVal
