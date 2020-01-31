# SDMXPlugin

QGIS Plugin to query SDMX data cubes served as WFS feature types.(see the SDMX GeoTools plugin `https://github.com/lmoran/sdmx`) 

This plugin allows to:
* Input (and save in the project) the parameters of the WFS server that contains SDMX cubes
* List all the available SDMX cubes on the WFS server
* Select the members of dimensions to use for a query 
* Compose a WFS request that can be used in a browser to execute the query and return a CSV file 


## Manual Installation

From the git repository:
* Download the code from `https://github.com/lmorandini/SDMXPlugin` by clicking on "releases" and downloading the lastest as a ZIP file
* Decompress the zip file.
* Rename decompressed folder to SDMXPlugin
* Copy the plugin folder to `$HOME/.qgis2/python/plugins/`
* Open a terminal window and move to `$HOME/.qgis2/python/plugins/SDMXPlugin`
* Execute `make install`
* Start QGIS (version 3.0 onwards)
* Load the SDMX Plugin by checking it on the list of plugins that can be accessed by selecting the 
  "Plugins / Manage and install plugins..." nenu item
* Close the plugin dialog 


## Use 

* Start QGIS (version 3.0 onwards) if not started already
* Open the SDMX Plugin (there should be an icon with "SDMX" on it)
* Insert the WFS URL of a GeoServer instance serving SDMX layers (such as `http://<hostname>/geoserver/wfs`) in the URL field
* Add username and password as required
* Click "Connect"
* Select one Cube from the list 
* Switch to the "Dimensions" tab and select one or more member from each dimension
* Switch to the "Expressions" tab
* Click on "Execute" button 
* The plugin should now execute an WFS query and add a geometry-less layer to the list of layers in QGIS
* Provided the query was executed correctly, a right-click, "Open Attribute Table" of the just-added layer shouls show the query response

