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
        self.activeCube= None
        self.activeDims= set()
        self.activeMembers= dict()
        
    def cubeItemSelected(self, item, column):
        QgsMessageLog.logMessage("*** cubeItemSelected " + item.data(0,0 ).__class__.__name__, PLUGIN_NAME, QgsMessageLog.INFO)  # XXX
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
            QgsMessageLog.logMessage("*** dimItemSelected1 " + item.data(0,0 ).__class__.__name__, PLUGIN_NAME, QgsMessageLog.INFO)  # XXX
        else:
          if item.isExpanded():
            item.setIcon(0, self.style().standardIcon(QtGui.QStyle.SP_CustomBase))
            item.setExpanded(False)
            if item.data(0, 0).dim.name in self.activeMembers.keys():
              self.activeMembers[item.data(0, 0).dim.name].remove(item.data(0, 0))
            QgsMessageLog.logMessage("*** dimItemSelected3 " + item.data(0,0 ).__class__.__name__ + " " + str(len(self.activeMembers[item.data(0, 0).dim.name])), PLUGIN_NAME, QgsMessageLog.INFO)  # XXX
            if len(self.activeMembers[item.data(0, 0).dim.name]) == 0:
              del self.activeMembers[item.data(0, 0).dim.name]
          else:
            item.setIcon(0, self.style().standardIcon(QtGui.QStyle.SP_DialogApplyButton))
            item.setExpanded(True)
            QgsMessageLog.logMessage("*** dimItemSelected2 " + item.data(0, 0).dim.name + " " + item.data(0, 0).__class__.__name__ + " " + str(self.activeMembers.keys()) , PLUGIN_NAME, QgsMessageLog.INFO)  # XXX
            if item.data(0, 0).dim.name not in self.activeMembers.keys():
              self.activeMembers[item.data(0, 0).dim.name]= set()
            self.activeMembers[item.data(0, 0).dim.name].add(item.data(0, 0))

    def newConnection(self):
        QgsMessageLog.logMessage("*** newConnection ", PLUGIN_NAME, QgsMessageLog.INFO)  # XXX
        SDMXConnectionDialog(self).show()

    def connect(self):
        self.treeCubes.clear()
        for cube in self.activeWfsConn.getCubes():
          QgsMessageLog.logMessage("*** connect " + str(cube), PLUGIN_NAME, QgsMessageLog.INFO)  # XXX
          item = QtGui.QTreeWidgetItem(self.treeCubes)
          item.setText(1, cube.name)
          item.setData(0, 0, cube)
          self.treeCubes.insertTopLevelItem(0, item)

    def fillDimensions(self, cubeItem):
        cube = cubeItem.data(0, 0)
        QgsMessageLog.logMessage("*** fillDimensions " + cube.__class__.__name__, PLUGIN_NAME, QgsMessageLog.INFO)  # XXX

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
          QgsMessageLog.logMessage("*** fillMembers " + str(m), PLUGIN_NAME, QgsMessageLog.INFO)  # XXX
          item = QtGui.QTreeWidgetItem(subTree)
          item.setText(1, m.value)
          item.setText(2, m.code)
          item.setData(0, 0, m)
          subTree.addChild(item)

    def selectMember(self, member):
        value = member.data(0, 0)
        QgsMessageLog.logMessage("*** selectMember " + str(value), PLUGIN_NAME, QgsMessageLog.INFO)  # XXX

    def exprShown(self, tabNumber):
        if tabNumber != 2:
          return
        QgsMessageLog.logMessage("*** exprShown " + str(tabNumber), PLUGIN_NAME, QgsMessageLog.INFO)  # XXX
        if self.activeCube != None:
          exprDims= list()
          for dim in self.activeDims:
            exprMembers= list()
            if dim.name in self.activeMembers.keys():
              for m in self.activeMembers[dim.name]:
                exprMembers.append("'" + m.code + "'")
              exprDims.append(dim.name + " in (" + ",".join(exprMembers) + ")" )
          cqlExpr= " and ".join(exprDims) 
          QgsMessageLog.logMessage("*** exprShown " + cqlExpr, PLUGIN_NAME, QgsMessageLog.INFO)  # XXX
          self.wfsExpr.setText(self.activeWfsConn.getFeatureURL(self.activeCube.featureType, cqlExpr))
          self.sqlExpr.setText(cqlExpr)

    def readSetting(self, propName):
        return self.proj.readEntry(PLUGIN_NAME, propName)[0]

    def writeSetting(self, propName, propValue):
        self.proj.writeEntry(PLUGIN_NAME, propName, propValue)
