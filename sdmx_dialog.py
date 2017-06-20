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
from qgis.core import QgsProject
from conn_dialog import SDMXConnectionDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/sdmx_dialog_base.ui'))

class SDMXPluginDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        self.proj = QgsProject.instance()
        super(SDMXPluginDialog, self).__init__(parent)
        self.setupUi(self)
        self.wfsExpr.setText(self.readSetting("test"))

        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect

    def newConnection(self):
        SDMXConnectionDialog(self).show()
        self.wfsExpr.setText(self.readSetting("test") + self.readSetting("test"))

    def readSetting(self, propName):
        return self.proj.readEntry("SDMXPlugin", propName)[0]

    def writeSetting(self, propName, propValue):
        self.proj.writeEntry("SDMXPlugin", propName, propValue)
