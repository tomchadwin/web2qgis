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

from qgis.PyQt.QtWebKitWidgets import QWebView

from web2qgis.leaflet import detectLeaflet, getLeafletMap

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
        self.loadButton.clicked.connect(self.loadMap)
        self.urlInput.setPlainText(
            "https://leafletjs.com/examples/choropleth/example.html")

    def loadMap(self):
        self.webview = QWebView()
        self.webview.loadFinished.connect(self.mapLoaded)
        self.webview.load(QUrl(self.urlInput.toPlainText()))

    def mapLoaded(self):
        webpage = self.webview.page()
        self.mainframe = webpage.mainFrame()
        self.detectMap(self.mainframe)
        for frame in self.mainframe.childFrames():
            self.detectMap(frame)

    def detectMap(self, frame):
        leaflet = detectLeaflet(frame)
        if leaflet:
            self.feedbackLabel.setText("Leaflet map detected")
            getLeafletMap(frame, self.iface)
        else:
            self.feedbackLabel.setText("No map detected")
