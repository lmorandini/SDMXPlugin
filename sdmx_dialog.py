# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SDMXPluginDialog
                                 A QGIS plugin
 Plugin to query SDMX data cubes as WFS feature types
                             -------------------
        begin                : 2017-06-14
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Luca Morandini - The AURIN Project
        email                : luca.morandini@unimelb.edu.au
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

from PyQt4 import QtGui, uic
from qgis.core import QgsProject , QgsMessageLog
from conn_dialog import SDMXConnectionDialog
from wfs_conn import WFSConnection

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/sdmx_dialog_base.ui'))
PLUGIN_NAME = "SDMXPlugin"

class SDMXPluginDialog(QtGui.QDialog, FORM_CLASS):

    def __init__(self, parent=None):
        """Constructor."""
        self.proj = QgsProject.instance()
        super(SDMXPluginDialog, self).__init__(parent)
        self.setupUi(self)
        # TODO: hard-coded for the time being
        self.activeWfsConn = WFSConnection("http://130.56.253.19/geoserver/wfs" , "", "")

        # Load connections data, if saved in the project
        # TODO
        """
        for i in range(0, self.cmbConnections.count()):
          self.cmbServers.itemText(i)
          
        self.readSetting("test")
        """

    def newConnection(self):
        SDMXConnectionDialog(self).show()

    def connect(self):
        self.treeCubes.clear()
        for cube in self.activeWfsConn.getCubes():
          self.treeCubes.insertTopLevelItem(0,
            QtGui.QTreeWidgetItem(self.treeCubes, (cube.ns, cube.name, cube.featureType)))

    def fillDimensions(self):
        cubeName= self.treeCubes.selectedItems()[0].text(2)
        QgsMessageLog.logMessage(cubeName, PLUGIN_NAME, QgsMessageLog.INFO)
        self.treeDimensions.clear()
        for dim in self.activeWfsConn.getCubeDimensions(cubeName):
          QgsMessageLog.logMessage(dim.name, PLUGIN_NAME, QgsMessageLog.INFO)
          self.treeDimensions.insertTopLevelItem(0,
            QtGui.QTreeWidgetItem(self.treeDimensions, (dim.ns, dim.name, dim.featureType)))

    def readSetting(self, propName):
        return self.proj.readEntry(PLUGIN_NAME, propName)[0]

    def writeSetting(self, propName, propValue):
        self.proj.writeEntry(PLUGIN_NAME, propName, propValue)
