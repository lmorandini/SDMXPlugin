import requests, lxml, re, base64
from qgis.core import QgsMessageLog
from qgis.gui import QgsMessageBar
from qgis.utils import iface
from libpasteurize.fixes import feature_base
from cube import Cube, Member, Members, Dimension

CONNECTION_SEP = "____"

class WFSConnection():

    def __init__(self, urlIn="", usernameIn="", passwordIn="", loggerNameIn="UnknownPlugin"):
        """Constructor."""
        self.url = urlIn
        self.username = usernameIn
        self.password = passwordIn
        self.capabilities = None
        self.cubes = list()
        self.dimensions = dict()
        self.members = dict()
        self.cubeRe = re.compile("(.+):(.+)__SDMX\Z")
        self.dimRe = re.compile("(.+):(.+)__SDMX__(.+)\Z")
        self.featureTypes = list()
        self.loggerName = loggerNameIn

        # Connects to the WFS server to return feature types
        if self.username:
          self.auth = (self.username, self.password)
        else:
          self.auth = None

    def encode(self):
      """Encode the connection parameters into a single String and returns it"""
      return base64.b64encode(CONNECTION_SEP.join((self.url, self.username, self.password)))

    def decode(self, connString):
      """Decode the connection parameters from a string and update the connection with them"""
      connList= base64.b64decode(connString).split(CONNECTION_SEP)
                
      self.url= connList[0] if len(connList) > 0 else None 
      self.username= connList[1] if len(connList) > 1 else None
      self.password= connList[2] if len(connList) > 2 else None
      
    def connect(self):
        try:
          resp = requests.get(self.url, auth=self.auth,
                            params={"request":"GetCapabilities", "version":"1.0.0", "service":"wfs"})
        except requests.exceptions.RequestException as e:
          msg= "Error connecting to WFS server %s" % str(e)
          QgsMessageLog.logMessage(msg, self.loggerName, QgsMessageLog.CRITICAL)
          iface.messageBar().pushMessage("Error", msg, level=QgsMessageBar.CRITICAL)
          return

        try:
          self.capabilities = lxml.etree.XML(resp.content)
          self.featureTypes = self.capabilities.findall(
                ".//{http://www.opengis.net/wfs}FeatureType/{http://www.opengis.net/wfs}Name")
        except lxml.etree.XMLSyntaxError as e:
          msg= "Error retrieving metadata from WFS server %s, please check URL and authentication" % str(e)
          QgsMessageLog.logMessage(msg, self.loggerName, QgsMessageLog.CRITICAL)
          iface.messageBar().pushMessage("Error", msg, level=QgsMessageBar.CRITICAL)
          return

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

    def getFeatureURL(self, featureType, cqlExpr):
        """ Returns an URL to get data (in CSV format) from the given feature type using the given CQL expression"""
        req = requests.Request("GET", self.url, params={"request":"GetFeature", "version":"1.1.0",
                                                      "service":"wfs", "outputFormat":"csv", "typeName":featureType, "cql_filter": cqlExpr})
        proxies = dict()
        proxies[self.url.split("://")[0]] = self.url.split("//")[1]
        return requests.adapters.HTTPAdapter().request_url(requests.Session().prepare_request(req), proxies)

    def getCubes(self):
        # Returns a list of SDMX cubes
        return self.cubes

    def getCubeDimensions(self, cube):
        # Returns a list of SDMX dimensions for a given cube
        return self.dimensions[cube.featureType]

    def getDimensionMembers(self, dim):
        # Returns a list of SDMX members for a given dimension
        resp = requests.get(self.url, auth=self.auth,
                params={"request":"GetFeature", "version":"1.1.0", "service":"wfs", "typeName":dim.featureType})
        features = lxml.etree.XML(resp.content).find(".//{http://www.opengis.net/gml}featureMembers")
        m = Members(dim)
        for feat in features:
          m.members.append(Member(dim, feat[0].text, feat[1].text))

        m.members.sort(key=lambda m: m.value)
        return m

