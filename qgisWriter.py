# -*- coding: utf-8 -*-
"""
/***************************************************************************
 qgisWriter
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

import os, random

from qgis.core import (QgsVectorLayer,
                       QgsProject,
                       QgsRectangle,
                       QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsFillSymbol)

from web2qgis.utils import getTempDir, getScript

def addVector(geoJSON, count, tempDir):
    vectorPath = os.path.join(tempDir, "vector%d.geojson" % count)
    with open(vectorPath, 'w') as vectorFile:
        vectorFile.write(geoJSON)
    vectorLayer = QgsVectorLayer(vectorPath, "vector%d" % count, "ogr")
    vectorLayer.triggerRepaint()
    vectorLayer.updateExtents()
    QgsProject.instance().addMapLayer(vectorLayer)
    return vectorLayer

def addXYZ(url, options, iface):
    xyzUrl = url.replace("{s}", random.choice("abc")).replace("{r}", "")
    for opt, val in options.items():
        try:
            xyzUrl = xyzUrl.replace("{%s}" % opt, val)
        except:
            pass
    iface.addRasterLayer("type=xyz&url=" + xyzUrl, xyzUrl, "wms")

def addWMS(url, options, crs, iface):
    try:
        wmsLayers = options["layers"]
    except:
        wmsLayers = options["LAYERS"]
    try:
        format = options["format"]
    except:
        format = "image/png"
    iface.addRasterLayer(
        "format=%s&crs=%s&styles=&layers=%s&url=%s" % (format, crs, wmsLayers,
                                                       url), wmsLayers, "wms")

def setExtent(xMin, yMin, xMax, yMax, iface):
    canvas = iface.mapCanvas()
    xform = QgsCoordinateTransform(QgsCoordinateReferenceSystem(4326),
                                   canvas.mapSettings().destinationCrs(),
                                   QgsProject.instance())
    srcExtent = QgsRectangle(float(xMin), float(yMin),
                             float(xMax), float(yMax))
    dstExtent = xform.transformBoundingBox(srcExtent)
    canvas.setExtent(dstExtent)
    canvas.refresh()
