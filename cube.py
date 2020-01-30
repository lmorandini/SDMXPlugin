"""
  Clases used tro hold data baout the SDMX data cube
"""

from builtins import object
DIMENSIONS_SUFFIX = "__DIMENSIONS"

""" Cube data holder"""
class Cube(object):
    def __init__(self, nsIn="", nameIn="", featureTypeIn=""):
        """Constructor."""
        self.ns = nsIn
        self.name = nameIn
        self.featureType = featureTypeIn
        self.dimFeatureType = self.featureType + DIMENSIONS_SUFFIX

    def __str__(self):
        return "Cube NS: " + self.ns + " Name: " + self.name + " featureType: " + self.featureType

""" Dimension data holder"""
class Dimension(object):
    def __init__(self, nameIn="", descrIn="", cubeNameIn="", featureTypeIn= ""):
        """Constructor."""
        self.name = nameIn
        self.description = descrIn
        self.cubeName = cubeNameIn
        self.featureType = featureTypeIn

    def __str__(self):
        return "Dimension NS: " + self.ns + " Name: " + self.name + " featureType: " + self.featureType + " cubeName: " + self.cubeName

""" Dimension Member list data holder"""
class Members(object):
    def __init__(self, dimIn=""):
        """Constructor."""
        self.dim = dimIn
        self.members = list()

""" Member data holder"""
class Member(object):
    def __init__(self, dimIn="", codeIn="", valueIn=""):
        """Constructor."""
        self.dim = dimIn
        self.code = codeIn
        self.value = valueIn

    def __str__(self):
        return "Member Code: " + self.code + " Value: " + self.value

