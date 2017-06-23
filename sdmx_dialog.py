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
        self.activeWfsConn = WFSConnection("http://130.56.253.19/geoserver/wfs" , "", "", PLUGIN_NAME)
        # Load connections data, if saved in the project
        # TODO
        """
        for i in range(0, self.cmbConnections.count()):
          self.cmbServers.itemText(i)
          
        self.readSetting("test")
        """

    def cubeItemSelected(self, item, column):
          QgsMessageLog.logMessage("*** 100 " + str(item), PLUGIN_NAME, QgsMessageLog.INFO)  # XXX

    def dimItemSelected(self):
          QgsMessageLog.logMessage("*** 100 " + str(item), PLUGIN_NAME, QgsMessageLog.INFO)  # XXX
      
    def newConnection(self):
        SDMXConnectionDialog(self).show()

        # SP_TitleBarCloseButton
        # SP_TitleBarMinButton

    def connect(self):
        self.treeCubes.clear()
        for cube in self.activeWfsConn.getCubes():
          QgsMessageLog.logMessage("*** 100 " + str(cube), PLUGIN_NAME, QgsMessageLog.INFO)  # XXX
          item = QtGui.QTreeWidgetItem(self.treeCubes)
          item.setIcon(0, self.style().standardIcon(QtGui.QStyle.SP_ArrowRight))
          item.setText(1, cube.name)
          item.setData(0, 0, cube)
          self.treeCubes.insertTopLevelItem(0, item)

    def fillDimensions(self):
      
        if len(self.treeCubes.selectedItems()) < 1:
          return

        # TODO: Change icon of de-selected cubes
        cubeItem = self.treeCubes.selectedItems()[0]
        cubeItem.setIcon(0, self.style().standardIcon(QtGui.QStyle.SP_ArrowDown))

        cube = cubeItem.data(0, 0)
        QgsMessageLog.logMessage("*** " + cube.__class__.__name__, PLUGIN_NAME, QgsMessageLog.INFO)  # XXX

        self.treeDimensions.clear()
        for dim in self.activeWfsConn.getCubeDimensions(cube):
          item = QtGui.QTreeWidgetItem(self.treeDimensions)
          item.setIcon(0, self.style().standardIcon(QtGui.QStyle.SP_ArrowRight))
          item.setText(1, dim.name)
          item.setData(0, 0, dim)
          self.treeDimensions.insertTopLevelItem(0, item)

    def fillMembers(self):

        if len(self.treeDimensions.selectedItems()) < 1:
          return

        subTree = self.treeDimensions.selectedItems()[0]
        # TODO: Change icon of de-selected dimension
        subTree.setIcon(0, self.style().standardIcon(QtGui.QStyle.SP_ArrowDown))

        if subTree.childCount() > 0:
          subTree.setExpanded(True)
          return

        dim = subTree.data(0, 0)
        for m in self.activeWfsConn.getDimensionMembers(dim).members:
          QgsMessageLog.logMessage("*** 500 " + str(m), PLUGIN_NAME, QgsMessageLog.INFO)  # XXX
          item = QtGui.QTreeWidgetItem(subTree)
          item.setText(2, m.value)
          item.setData(0, 0, m)
          subTree.addChild(item)
          
        subTree.setExpanded(True)

    def readSetting(self, propName):
        return self.proj.readEntry(PLUGIN_NAME, propName)[0]

    def writeSetting(self, propName, propValue):
        self.proj.writeEntry(PLUGIN_NAME, propName, propValue)
