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

import random

from qgis.core import (QgsVectorLayer,
                       QgsPointXY,
                       QgsFeature,
                       QgsGeometry,
                       QgsProject)

def detectLeaflet(mainframe):
    detectResult = mainframe.evaluateJavaScript("L.version")
    if detectResult is None:
        result = False
    else:
        result = True
    return result

def getLeafletMap(mainframe, iface):
    lyrs = None
    lyrs = mainframe.evaluateJavaScript("""
        (function (){
          lyrs = []
          for(var key in window) {
            var value = window[key];
            if (value instanceof L.Map) {
              for(var lyr in value._layers) {
                if (value._layers[lyr] instanceof L.TileLayer) {
				  xyzLyr = getXYZ(value._layers[lyr]);
                  lyrs.push(['xyz', xyzLyr[0], xyzLyr[1]]);
                }
                if (value._layers[lyr] instanceof L.Marker) {
                  lyrs.push(['marker', getMarker(value._layers[lyr])]);
                }
              }
            }
          }
          return lyrs;
        }());
        
        function getXYZ(lyr) {
            return [lyr._url, lyr.options];
        }
        
        function getMarker(lyr) {
            return lyr._latlng;
        }
    """)
    while lyrs is None:
        pass
    for lyr in lyrs:
        if lyr[0] == "xyz":
            print("xyz")
            xyzUrl = lyr[1].replace("{s}", random.choice("abc")).replace("{r}",
                                                                         "")
            for opt, val in lyr[2].items():
                # print(opt, val)
                try:
                    xyzUrl = xyzUrl.replace("{" + opt + "}", val)
                except:
                    pass
            iface.addRasterLayer("type=xyz&url=" + xyzUrl, xyzUrl, "wms")
        elif lyr[0] == "marker":
            print("marker")
            markerLayer = QgsVectorLayer('Point?crs=epsg:4326',
                                         'point' ,
                                         'memory')
 
            # Set the provider to accept the data source
            prov = markerLayer.dataProvider()
            point = QgsPointXY(lyr[1]["lng"], lyr[1]["lat"])
             
            # Add a new feature and assign the geometry
            feat = QgsFeature()
            feat.setGeometry(QgsGeometry.fromPointXY(point))
            prov.addFeatures([feat])
             
            # Update extent of the layer
            markerLayer.updateExtents()
             
            # Add the layer to the Layers panel
            QgsProject.instance().addMapLayers([markerLayer])
        else:
            print("Unsupported layer type")
