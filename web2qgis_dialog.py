# -*- coding: utf-8 -*-
"""
/***************************************************************************
 web2qgisDialog
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

from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QDialogButtonBox

from qgis.PyQt.QtWebKitWidgets import QWebView

from web2qgis.leafletReader import detectLeaflet, getLeafletMap
from web2qgis.openlayersReader import detectOpenlayers, getOpenlayersMap

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'web2qgis_dialog_base.ui'))


class web2qgisDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, iface, parent=None):
        """Constructor."""
        super(web2qgisDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.iface = iface
        self.button_box.button(QDialogButtonBox.Save).setEnabled(False)
        self.loadButton.clicked.connect(self.loadMap)
        self.button_box.accepted.connect(self.getMap)
        self.urlInput.setText(
            "https://leafletjs.com/examples/choropleth/example.html")

    def loadMap(self):
        self.webview = QWebView()
        self.webview.loadFinished.connect(self.mapLoaded)
        self.webview.load(QUrl(self.urlInput.text()))

    def mapLoaded(self):
        webpage = self.webview.page()
        self.mainframe = webpage.mainFrame()
        self.detectMap(self.mainframe)
        for frame in self.mainframe.childFrames():
            self.detectMap(frame)

    def detectMap(self, frame):
        leaflet = detectLeaflet(frame)
        openlayers = detectOpenlayers(frame)
        if leaflet:
            self.feedbackLabel.setText("Leaflet map detected")
            self.button_box.button(QDialogButtonBox.Save).setEnabled(True)
        elif openlayers:
            self.feedbackLabel.setText("OpenLayers map detected")
            self.button_box.button(QDialogButtonBox.Save).setEnabled(True)
        else:
            self.feedbackLabel.setText("No map detected")
            self.button_box.button(QDialogButtonBox.Save).setEnabled(False)

    def getMap(self):
        webpage = self.webview.page()
        self.mainframe = webpage.mainFrame()
        if self.feedbackLabel.text() == "Leaflet map detected":
            getLeafletMap(self.mainframe, self.iface)
            for frame in self.mainframe.childFrames():
                getLeafletMap(frame, self.iface)
        elif self.feedbackLabel.text() == "OpenLayers map detected":
            getOpenlayersMap(self.mainframe, self.iface)
            for frame in self.mainframe.childFrames():
                getOpenlayersMap(frame, self.iface)
        self.feedbackLabel.clear()
