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

import os, functools
from PyQt4 import QtGui, uic
from qgis.core import QgsProject, QgsMessageLog
from conn_dialog import SDMXConnectionDialog
from cube import Cube, Member, Members, Dimension
from wfs_connection import WFSConnection

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
        self.activeWfsConn = WFSConnection("", "", "", PLUGIN_NAME)
        
        # Load connection data, if saved in the project
        self.loadSettings()
        
        self.activeCube= None
        self.activeDims= set()
        self.activeMembers= dict()
        
    def cubeItemSelected(self, item, column):
        # TODO: all non-selected cubes must have the icon changed
        if item.isExpanded():
          item.setIcon(0, self.style().standardIcon(QtGui.QStyle.SP_FileIcon))
          item.setExpanded(False)
          self.activeCube= None 
        else:
          item.setIcon(0, self.style().standardIcon(QtGui.QStyle.SP_DialogApplyButton))
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
            item.setIcon(0, self.style().standardIcon(QtGui.QStyle.SP_DirClosedIcon))
            item.setExpanded(False)
            self.activeDims.remove(item.data(0, 0))
          else:
            item.setIcon(0, self.style().standardIcon(QtGui.QStyle.SP_FileDialogStart))
            item.setExpanded(True)
            self.activeDims.add(item.data(0, 0))
        else:
          if item.isExpanded():
            item.setIcon(0, self.style().standardIcon(QtGui.QStyle.SP_CustomBase))
            item.setExpanded(False)
            if item.data(0, 0).dim.name in self.activeMembers.keys():
              self.activeMembers[item.data(0, 0).dim.name].remove(item.data(0, 0))
            if len(self.activeMembers[item.data(0, 0).dim.name]) == 0:
              del self.activeMembers[item.data(0, 0).dim.name]
          else:
            item.setIcon(0, self.style().standardIcon(QtGui.QStyle.SP_DialogApplyButton))
            item.setExpanded(True)
            if item.data(0, 0).dim.name not in self.activeMembers.keys():
              self.activeMembers[item.data(0, 0).dim.name]= set()
            self.activeMembers[item.data(0, 0).dim.name].add(item.data(0, 0))

    def connect(self):
        self.treeCubes.clear()
        self.activeWfsConn= WFSConnection(self.wfsUrlInput.text(), 
           self.usernameInput.text(), self.passwordInput.text(), PLUGIN_NAME)

        self.activeWfsConn.connect()
        for cube in self.activeWfsConn.getCubes():
          item = QtGui.QTreeWidgetItem(self.treeCubes)
          item.setText(1, cube.name)
          item.setData(0, 0, cube)
          self.treeCubes.insertTopLevelItem(0, item)

    def fillDimensions(self, cubeItem):
        cube = cubeItem.data(0, 0)

        self.treeDimensions.clear()
        for dim in self.activeWfsConn.getCubeDimensions(cube):
          item = QtGui.QTreeWidgetItem(self.treeDimensions)
          item.setIcon(0, self.style().standardIcon(QtGui.QStyle.SP_DirClosedIcon))
          item.setText(1, dim.name)
          item.setData(0, 0, dim)
          self.treeDimensions.insertTopLevelItem(0, item)

    def fillMembers(self, subTree):
        dim = subTree.data(0, 0)
        for m in self.activeWfsConn.getDimensionMembers(dim).members:
          item = QtGui.QTreeWidgetItem(subTree)
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
            if dim.name in self.activeMembers.keys():
              for m in self.activeMembers[dim.name]:
                exprMembers.append("'" + m.code + "'")
              exprDims.append(dim.name + " in (" + ",".join(exprMembers) + ")" )
          cqlExpr= " and ".join(exprDims) 
          self.wfsExpr.setText(self.activeWfsConn.getFeatureURL(self.activeCube.featureType, cqlExpr))
          self.sqlExpr.setText(cqlExpr)

    def loadSettings(self):
        self.activeWfsConn.decode(QgsProject.instance().readEntry(PLUGIN_NAME, "connection")[0])
        self.wfsUrlInput.setText(self.activeWfsConn.url)
        self.passwordInput.setText(self.activeWfsConn.username)
        self.passwordInput.setText(self.activeWfsConn.password)

    def saveSettings(self):
        self.activeWfsConn= WFSConnection(self.wfsUrlInput.text(), 
           self.usernameInput.text(), self.passwordInput.text(), PLUGIN_NAME)
        self.connections= QgsProject.instance().writeEntry (PLUGIN_NAME, "connection", 
           self.activeWfsConn.encode())
