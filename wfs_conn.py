import requests, lxml, re
from qgis.core import QgsProject , QgsMessageLog
from libpasteurize.fixes import feature_base

class Cube():
    def __init__(self, nsIn="", nameIn="", featureTypeIn=""):
        """Constructor."""
        self.ns = nsIn
        self.name = nameIn
        self.featureType = featureTypeIn

    def __str__(self):
        return "Cube NS: " + self.ns + " Name: " + self.name + " featureType: " + self.featureType

class Dimension():
    def __init__(self, nsIn="", nameIn="", featureTypeIn="", cubeNameIn=""):
        """Constructor."""
        self.ns = nsIn
        self.name = nameIn
        self.featureTypeNoNS = featureTypeIn.split(":")[1]
        self.featureType = featureTypeIn
        self.cubeName = cubeNameIn

    def __str__(self):
        return "Dimension NS: " + self.ns + " Name: " + self.name + " featureType: " + self.featureType + " cubeName: " + self.cubeName

class Members():
    def __init__(self, dimIn=""):
        """Constructor."""
        self.dim = dimIn
        self.members = list()

class Member():
    def __init__(self, dimIn="", codeIn="", valueIn=""):
        """Constructor."""
        self.dim = dimIn
        self.code = codeIn
        self.value = valueIn

    def __str__(self):
        return "Member Code: " + self.code + " Value: " + self.value

class WFSConnection():

    def __init__(self, urlIn="", usernameIn="", passwordIn="", loggerNameIn="UnknownPlugin"):
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
        self.loggerName = loggerNameIn

        # Connects to the WFS server
        # TODO: exception handling
        if self.username:
           self.auth = (self.username, self.password)
        else:
           self.auth = None

        resp = requests.get(self.url, auth=self.auth,
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
          self.dimensions[cube.featureType] = filter(lambda m: m.cubeName == cube.name and m.ns == cube.ns,
              allDimensions)

    def getCubes(self):
        # Returns a list of SDMX cubes
        return self.cubes

    def getCubeDimensions(self, cube):
        # Returns a list of SDMX dimensions for a given cube
        QgsMessageLog.logMessage("*** 250 " + str(cube), self.loggerName, QgsMessageLog.INFO)  # XXX
        return self.dimensions[cube.featureType]

    def getDimensionMembers(self, dim):
        # Returns a list of SDMX members for a given dimension 
        resp = requests.get(self.url, auth=self.auth,
                params={"request":"GetFeature", "version":"1.1.0", "service":"wfs", "typeName":dim.featureType})
        features = lxml.etree.XML(resp.content).find(".//{http://www.opengis.net/gml}featureMembers")
        m = Members(dim)
        for feat in features:
          m.members.append(Member(dim, feat[0].text, feat[1].text))

        return m

