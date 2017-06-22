import requests, lxml, re
from qgis.core import QgsProject , QgsMessageLog

class Cube():
    def __init__(self, nsIn="", nameIn="", featureTypeIn=""):
        """Constructor."""
        self.ns = nsIn
        self.name = nameIn
        self.featureType = featureTypeIn

class Dimension():
    def __init__(self, nsIn="", nameIn="", featureTypeIn="", cubeIn=""):
        """Constructor."""
        self.ns = nsIn
        self.name = nameIn
        self.cube = cubeIn
        self.featureType = featureTypeIn

class WFSConnection():

    def __init__(self, urlIn="", usernameIn="", passwordIn=""):
        """Constructor."""
        self.url = urlIn
        self.username = usernameIn
        self.password = passwordIn
        self.capabilities = None
        self.cubes = None
        self.dimensions = dict()
        self.members = dict()
        self.cubeRe = re.compile("(.+):(.+)__SDMX\Z")
        self.dimRe = re.compile("(.+):(.+)__SDMX__(.+)\Z")
        self.featureTypes = None

        # Connects to the WFS server
        # TODO: exception handling
        if self.username:
           auth = (self.username, self.password)
        else:
           auth = None

        resp = requests.get(self.url, auth=auth,
                            params={"request":"GetCapabilities", "version":"1.0.0", "service":"wfs"})
        self.capabilities = lxml.etree.XML(resp.content)
        self.featureTypes = self.capabilities.findall(
                               ".//{http://www.opengis.net/wfs}FeatureType/{http://www.opengis.net/wfs}Name")

        # Extracts cube feature types
        self.cubes = map(lambda m2: Cube(m2.group(1), m2.group(2), m2.group(0)),
                        filter(lambda m: m is not None,
                          map(lambda e: self.cubeRe.search(e.text), self.featureTypes)))

        # Extract dimension feature types
        allDimensions = map(lambda m2: Dimension(m2.group(1), m2.group(3), m2.group(0), m2.group(2)),
            filter(lambda m: m is not None,
              map(lambda e: self.dimRe.search(e.text), self.featureTypes)))
        self.dimensions = dict()

        for cube in self.cubes:
          self.dimensions[cube.featureType] = filter(lambda m: m.cube == cube.name and m.ns == cube.ns,
              allDimensions)

#        self.dimensions = map(lambda e: e.text, self.capabilities.findall(".//{http://www.opengis.net/wfs}FeatureType/{http://www.opengis.net/wfs}Name"))

    def getCubes(self):
        # Returns a list of SDMX cubes
        return self.cubes

    def getCubeDimensions(self, cubeName):
        # Returns a list of SDMX dimensions for a given cube
        return self.dimensions[cubeName]

    def getDimensionMembers(self, cubeName, dimName):
        # Returns a list of SDMX members for a given dimension of a given cube
        return self.members[cubeName][dimName]
