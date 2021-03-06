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
                       QgsMarkerSymbol,
                       QgsLineSymbol,
                       QgsFillSymbol,
                       QgsSimpleMarkerSymbolLayer,
                       QgsWkbTypes)

from web2qgis.utils import getTempDir, getScript, getRGBA
from web2qgis.qgisWriter import addWMS, addXYZ, addVector, setExtent

L2Q_STYLES = {
    "radius": "size",
    "weight": "outline_width",
    "color": "color_border",
    "fillColor": "color"
}

L2Q_LINE_STYLES = {
    "radius": "size",
    "weight": "outline_width",
    "color": "line_color"
}

L2Q_TYPES = {
    "radius": "float",
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
            print("vector")
            vectorLayer = addVector(lyr[1], count, tempDir)
            geom = vectorLayer.geometryType()
            print(geom)
            renderer = getRenderer(lyr[2], geom, mainframe)
            vectorLayer.setRenderer(renderer)            
        else:
            print("Unsupported layer type")

    getLeafletView(scriptFolder, mainframe, iface)

def getRenderer(leafletStyle, geom, mainframe):
    print(leafletStyle)
    if "body" in leafletStyle:
        try:
            styleJSON = leafletStyle["body"][0]["body"]["body"]
        except:
            styleJSON = leafletStyle["body"][0]["declarations"]
        if styleJSON[0]["type"] == "SwitchStatement":
            renderer = getCategorizedRenderer(styleJSON[0], geom, mainframe)
        elif styleJSON[0]["type"] == "IfStatement":
            renderer = getGraduatedRenderer(styleJSON, geom, mainframe)
        else:
            renderer = getSingleSymbolRenderer(styleJSON[0], geom, mainframe)
    else:
        renderer = getSingleSymbolRenderer(leafletStyle, geom, mainframe)
    return renderer

def getSingleSymbolRenderer(styleJSON, geom, mainframe):
    if "argument" in styleJSON or styleJSON["id"]["name"] == "w2q_style":
        style = getFunctionStyle(styleJSON, mainframe)
    else:
        style = styleJSON
    symbol = getSymbol(style, geom)
    renderer = QgsSingleSymbolRenderer(symbol)
    return renderer

def getCategorizedRenderer(styleJSON, geom, mainframe):
    categories = []
    attrName = styleJSON["discriminant"]["arguments"][0]["property"]["value"]
    for case in styleJSON["cases"]:
        try:
            value = case["test"]["value"]
        except:
            value = "web2qgis_ELSE"
        style = getFunctionStyle(case, mainframe)
        symbol = getSymbol(style, geom)
        category = QgsRendererCategory(value, symbol, value, True)
        categories.append(category)
    renderer = QgsCategorizedSymbolRenderer(attrName, categories)
    return renderer

def getGraduatedRenderer(styleJSON, geom, mainframe):
    ranges = []
    attrName = styleJSON[0]["test"]["left"]["left"]["property"]["value"]
    for case in styleJSON:
        low = case["test"]["left"]["right"]["value"]
        high = case["test"]["right"]["right"]["value"]
        label = "%s-%s" % (low, high)
        style = getFunctionStyle(case, mainframe)
        symbol = getSymbol(style, geom)
        range = QgsRendererRange(low, high, symbol, label, True)
        ranges.append(range)
    renderer = QgsGraduatedSymbolRenderer(attrName, ranges)
    return renderer

def getFunctionStyle(styleJSON, mainframe):
    style = walkAST(styleJSON, {}, mainframe)
    return style

def getSymbol(leafletStyle, geom):
    style = {}
    if geom == QgsWkbTypes.LineGeometry:
        styles = L2Q_LINE_STYLES
    else:
        styles = L2Q_STYLES
    for k, v in leafletStyle.items():
        if k in styles:
            if k == "radius":
                v = v * 2
            if L2Q_TYPES[k] == "rgba":
                value = getRGBA(v)
            else:
                value = str(v)
            style[styles[k]] = value
    style["size_unit"] = "Pixel"
    style["line_width_unit"] = "Pixel"
    style["outline_width_unit"] = "Pixel"
    if geom == QgsWkbTypes.PointGeometry:
        symbol = QgsMarkerSymbol.createSimple(style)
    elif geom == QgsWkbTypes.LineGeometry:
        symbol = QgsLineSymbol.createSimple(style)
    else:
        symbol = QgsFillSymbol.createSimple(style)
    return symbol

def getLeafletView(scriptFolder, mainframe, iface):
    getExtentScript = getScript(scriptFolder, "getLeafletView.js")
    extent = mainframe.evaluateJavaScript(getExtentScript)
    try:
        xMin, yMin, xMax, yMax = extent.split(",")
        setExtent(xMin, yMin, xMax, yMax, iface)
    except:
        pass

def walkAST(node, returnVal, mainframe):
    if type(node) is list:
        for child in node:
            returnVal = walkAST(child, returnVal, mainframe)
    elif type(node) is dict:
        if node["type"] == "ReturnStatement":
            try:
                for k in node["argument"]["properties"]:
                    returnVal[k["key"]["name"]] = k["value"]["value"]
            except:
                returnVal = walkAST(node["argument"], returnVal, mainframe)
        elif node["type"] == "CallExpression":
            if node["callee"]["object"]["name"] != "L":
                js = "esprima.parse(window.%s.toString());" % node["callee"]["name"]
                f = mainframe.evaluateJavaScript(js)
                returnVal = walkAST(f, returnVal, mainframe)
        else:
            for k, v in node.items():
                returnVal = walkAST(v, returnVal, mainframe)
    return returnVal
