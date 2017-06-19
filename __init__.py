# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SDMXPlugin
                                 A QGIS plugin
 Plugin to query SDMX data cubes as WFS feature types
                             -------------------
        begin                : 2017-06-14
        copyright            : (C) 2017 by Luca Morandini - The AURIN Project
        email                : luca.morandini@unimelb.edu.au
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load SDMXPlugin class from file SDMXPlugin.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .sdmx import SDMXPlugin
    return SDMXPlugin(iface)
