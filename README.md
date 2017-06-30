# SDMXPlugin

QGIS Plugin to query SDMX data cubes served as WFS feature types.(see the SDMX GeoTools plugin `https://github.com/lmoran/sdmx`) 

This plugin allows to:
* Input (and save in the project) the parameters of the WFS server that contains SDMX cubes
* List all the available SDMX cubes on the WFS server
* Select the members of dimensions to use for a query 
* Compose a WFS request that can be used in a browser to execute the query and return a CSV file 


## Manual Installation

From the git repository:
* Download the code from `https://github.com/lmoran/SDMXPlugin/archive/v0.1.2.zip`
* Decompress the zip file.
* Rename decompressed folder to SDMXPlugin
* Copy the plugin folder to `$HOME/.qgis2/python/plugins/`
* Open a terminal window and move to `$HOME/.qgis2/python/plugins/`
* Execute `make install`
* Start QGIS (version 2.0 onwards)
* Load the SDMX Plugin by checking it on the list of plugins that can be accessed by selecting the 
  "Plugins / Manage and install plugins..." nenu item
* Close the plugin dialog 
* Close QGIS 


## Use 

* Start QGIS (version 2.0 onwards) if not started already
* Open the SDMX Plugin (there should be an icon with a power plug on it)
* Insert the URL `http://130.56.253.19/geoserver/wfs` (blank username and password) in the URL field
* Click "Connect"
* Select one Cube from the list in the first tab
* Switch to the second tab and select one or more member from each dimension
* Switch to the third tab and copy the WFS expression (to use it, paste it in the address bar of a browser)
* Optionally, clieck `Save` on the first tab to save the connection parameters to the project file, and save the project