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
from __future__ import absolute_import

from builtins import range
import os, functools, requests, tempfile
from urllib.parse import unquote

from qgis.PyQt.QtWidgets import QDialog, QTreeWidgetItem, QStyle
from qgis.PyQt import uic
from qgis.core import QgsProject, QgsMessageLog, QgsVectorLayer
from .cube import Cube, Member, Members, Dimension
from .wfs_connection import WFSConnection

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/sdmx_dialog_base.ui'))
PLUGIN_NAME = "SDMXPlugin"

class SDMXPluginDialog(QDialog, FORM_CLASS):

    def __init__(self, parent=None):
        """Constructor."""
        self.proj = QgsProject.instance()
        super(SDMXPluginDialog, self).__init__(parent)
        self.setupUi(self)
        # TODO: hard-coded for the time being
        self.activeWfsConn = WFSConnection("", "", "", PLUGIN_NAME)
        
        # Load connection data, if saved in the project
        self.loadSettings()
        
        self.activeCube= None
        self.activeDims= set()
        self.activeMembers= dict()
        
    def cubeItemSelected(self, item, column):
        for i in range(self.treeCubes.invisibleRootItem().childCount()):
          itemI = self.treeCubes.invisibleRootItem().child(i)
          itemI.setIcon(0, self.style().standardIcon(QStyle.SP_ArrowDown))
          itemI.setExpanded(False)
          
        item.setIcon(0, self.style().standardIcon(QStyle.SP_DialogApplyButton))
        item.setExpanded(True)
        self.activeCube=item.data(0, 0) 

        self.fillDimensions(item)
        self.activeDims= set()
        self.activeMembers= dict()

    def dimItemSelected(self, item, column):
        if item.data(0,0 ).__class__.__name__ == "Dimension":
          if item.childCount() == 0:
            self.fillMembers(item)

          if item.isExpanded():
            item.setIcon(0, self.style().standardIcon(QStyle.SP_ArrowDown))
            item.setExpanded(False)
            self.activeDims.remove(item.data(0, 0))
          else:
            item.setIcon(0, self.style().standardIcon(QStyle.SP_ArrowUp))
            item.setExpanded(True)
            self.activeDims.add(item.data(0, 0))
        else:
          if item.isExpanded():
            item.setIcon(0, self.style().standardIcon(QStyle.SP_CustomBase))
            item.setExpanded(False)
            if item.data(0, 0).dim.name in list(self.activeMembers.keys()):
              self.activeMembers[item.data(0, 0).dim.name].remove(item.data(0, 0))
            if len(self.activeMembers[item.data(0, 0).dim.name]) == 0:
              del self.activeMembers[item.data(0, 0).dim.name]
          else:
            item.setIcon(0, self.style().standardIcon(QStyle.SP_DialogApplyButton))
            item.setExpanded(True)
            if item.data(0, 0).dim.name not in list(self.activeMembers.keys()):
              self.activeMembers[item.data(0, 0).dim.name]= set()
            self.activeMembers[item.data(0, 0).dim.name].add(item.data(0, 0))

    def connect(self):
        self.treeCubes.clear()
        self.activeWfsConn= WFSConnection(self.wfsUrlInput.text(), 
           self.usernameInput.text(), self.passwordInput.text(), PLUGIN_NAME)

        self.activeWfsConn.connect()
        for cube in self.activeWfsConn.getCubes():
          item = QTreeWidgetItem(self.treeCubes)
          item.setText(1, cube.name)
          item.setData(0, 0, cube)
          self.treeCubes.insertTopLevelItem(0, item)

    def fillDimensions(self, cubeItem):
        cube = cubeItem.data(0, 0)

        self.treeDimensions.clear()
        for dim in self.activeWfsConn.getCubeDimensions(cube):
          item = QTreeWidgetItem(self.treeDimensions)
          item.setIcon(0, self.style().standardIcon(QStyle.SP_ArrowDown))
          item.setText(1, dim.description)
          item.setText(2, dim.name)
          item.setData(0, 0, dim)
          self.treeDimensions.insertTopLevelItem(0, item)

    def fillMembers(self, subTree):
        dim = subTree.data(0, 0)
        for m in self.activeWfsConn.getDimensionMembers(dim).members:
          item = QTreeWidgetItem(subTree)
          item.setText(1, m.value)
          item.setText(2, m.code)
          item.setData(0, 0, m)
          subTree.addChild(item)

    def selectMember(self, member):
        value = member.data(0, 0)

    def exprShown(self, tabNumber):
        if tabNumber != 2:
          return
        if self.activeCube != None:
          exprDims= list()
          for dim in self.activeDims:
            exprMembers= list()
            if dim.name in list(self.activeMembers.keys()):
              for m in self.activeMembers[dim.name]:
                exprMembers.append("'" + m.code + "'")
              exprDims.append(dim.name + " in (" + ",".join(exprMembers) + ")" )
          cqlExpr= " and ".join(exprDims) 
          self.wfsExpr.setText(unquote(self.activeWfsConn.getFeatureURL(self.activeCube.featureType, cqlExpr)))
          self.sqlExpr.setText(cqlExpr)

    def executeWFSRequest(self):
        msg = "About to ecxcute WFS request %s" % self.wfsExpr.toPlainText()
        QgsMessageLog.logMessage(msg, 'Info')
        response = requests.get(self.wfsExpr.toPlainText())
        response.raise_for_status()
        tmpCsv= tempfile.NamedTemporaryFile(mode = 'w', suffix = '.csv', prefix = 'sdmx-', delete=False)
        tmpCsv.write(response.text)
        tmpCsv.close()
        table = QgsVectorLayer('file://' + tmpCsv.name, 'SDMX:: ' + self.sqlExpr.toPlainText(), 'delimitedtext')
        QgsProject.instance().addMapLayer(table)

    # FIXME: this would be handy to load the WFS URL from QGIS settings, excepts it does not work in QGSI3
    def loadSettings(self):
        self.activeWfsConn.decode(QgsProject.instance().readEntry(PLUGIN_NAME, "connection")[0])
        self.wfsUrlInput.setText(self.activeWfsConn.url)
        self.passwordInput.setText(self.activeWfsConn.username)
        self.passwordInput.setText(self.activeWfsConn.password)

    # FIXME: this would be handy to save the current WFS URL to QGIS settings, excepts it does not work in QGSI3
    def saveSettings(self):
        self.activeWfsConn= WFSConnection(self.wfsUrlInput.text(), 
           self.usernameInput.text(), self.passwordInput.text(), PLUGIN_NAME)
        self.connections= QgsProject.instance().writeEntry (PLUGIN_NAME, "connection", 
           self.activeWfsConn.encode())
