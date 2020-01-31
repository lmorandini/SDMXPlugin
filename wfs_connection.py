from __future__ import absolute_import
from builtins import str
from builtins import object
import requests, lxml, re, base64
from qgis.core import Qgis, QgsMessageLog
from qgis.gui import QgsMessageBar
from qgis.utils import iface
from libpasteurize.fixes import feature_base
from .cube import Cube, Member, Members, Dimension

CONNECTION_SEP = "____"

class WFSConnection(object):

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
        self.dimRe = re.compile("(.+):(.+)__SDMX__DIMENSIONS\Z")
        self.featureTypes = list()
        self.loggerName = loggerNameIn

        # Connects to the WFS server to return feature types
        if self.username:
          self.auth = (self.username, self.password)
        else:
          self.auth = None

    def encode(self):
      """Encode the connection parameters into a single String and returns it"""
      return base64.b64encode(CONNECTION_SEP.join(self.url, self.username, self.password).encode('utf-8').decode('utf-8'))

    def decode(self, connString):
      """Decode the connection parameters from a string and update the connection with them"""
      connList= base64.b64decode(connString.encode('utf-8')).decode('utf-8').split(CONNECTION_SEP)
                
      self.url= connList[0] if len(connList) > 0 else None 
      self.username= connList[1] if len(connList) > 1 else None
      self.password= connList[2] if len(connList) > 2 else None
      
    def connect(self):
        try:
          resp = requests.get(self.url, auth=self.auth,
                            params={"request":"GetCapabilities", "version":"1.1.0", "service":"wfs"})
        except requests.exceptions.RequestException as e:
          msg= "Error connecting to WFS server %s" % str(e)
          QgsMessageLog.logMessage(msg, self.loggerName, Qgis.Critical)
          iface.messageBar().pushMessage("Error", msg, level=Qgis.Critical)
          return

        try:
          self.capabilities = lxml.etree.XML(resp.content)
          self.featureTypes = self.capabilities.findall(
                ".//{http://www.opengis.net/wfs}FeatureType/{http://www.opengis.net/wfs}Name")
        except lxml.etree.XMLSyntaxError as e:
          msg= "Error retrieving metadata from WFS server %s, please check URL and authentication" % str(e)
          QgsMessageLog.logMessage(msg, self.loggerName, Qgis.Critical)
          iface.messageBar().pushMessage("Error", msg, level=Qgis.Critical)
          return

        # Extracts cube feature types
        self.cubes = [Cube(m2.group(1), m2.group(2), m2.group(0)) for m2 in [m for m in [self.cubeRe.search(e.text) for e in self.featureTypes] if m is not None]]

        # Extract cube dimensions
        for cube in self.cubes:
          try:
            resp = requests.get(self.url, auth=self.auth,
                params={"request":"GetFeature", "version":"1.1.0", "service":"wfs", 
                        "typeName":cube.dimFeatureType, "cql_filter":"CODE='ALL'"})
          except requests.exceptions.RequestException as e:
            msg= "Error connecting to WFS server %s" % str(e)
            QgsMessageLog.logMessage(msg, self.loggerName, Qgis.Critical)
            iface.messageBar().pushMessage("Error", msg, level=Qgis.Critical)
            return
            
          try:
            features = lxml.etree.XML(resp.content).find(".//{http://www.opengis.net/gml}featureMembers")

          except lxml.etree.XMLSyntaxError as e:
            msg= "Error retrieving metadata from WFS server %s, please check URL and authentication" % str(e)
            QgsMessageLog.logMessage(msg, self.loggerName, Qgis.Critical)
            iface.messageBar().pushMessage("Error", msg, level=Qgis.Critical)
            return

          if features is None:
            msg="No feature types were returned"
            QgsMessageLog.logMessage(msg, self.loggerName, Qgis.Critical)
            iface.messageBar().pushMessage("Error", msg, level=Qgis.Critical)
            return

          self.dimensions[cube.featureType]= [Dimension(feat[0].text, feat[1].text, cube.name, cube.dimFeatureType) for feat in features]

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
        return self.dimensions[cube.featureType]

    def getDimensionMembers(self, dim):
        # Returns a list of SDMX members for a given dimension
        try:
          resp = requests.get(self.url, auth=self.auth,
              params={"request":"GetFeature", "version":"1.1.0", "service":"wfs", 
                        "typeName":dim.featureType, "cql_filter":"CODE='" + dim.name + "'"})
        except requests.exceptions.RequestException as e:
          msg= "Error connecting to WFS server %s" % str(e)
          QgsMessageLog.logMessage(msg, self.loggerName, Qgis.Critical)
          iface.messageBar().pushMessage("Error", msg, level=Qgis.Critical)
          return
            
        try:
          features = lxml.etree.XML(resp.content).find(".//{http://www.opengis.net/gml}featureMembers")

        except lxml.etree.XMLSyntaxError as e:
          msg= "Error retrieving metadata from WFS server %s, please check URL and authentication" % str(e)
          QgsMessageLog.logMessage(msg, self.loggerName, Qgis.Critical)
          iface.messageBar().pushMessage("Error", msg, level=Qgis.Critical)
          return
        
        m = Members(dim)
        m.members= [Member(dim, feat[0].text, feat[1].text) for feat in features]   
        m.members.sort(key=lambda m: m.value)
        return m

