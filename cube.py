"""
  Clases used tro hold data baout the SDMX data cube
"""

""" Cube data holder"""
class Cube():
    def __init__(self, nsIn="", nameIn="", featureTypeIn=""):
        """Constructor."""
        self.ns = nsIn
        self.name = nameIn
        self.featureType = featureTypeIn

    def __str__(self):
        return "Cube NS: " + self.ns + " Name: " + self.name + " featureType: " + self.featureType

""" Dimension data holder"""
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

""" Dimension Member list data holder"""
class Members():
    def __init__(self, dimIn=""):
        """Constructor."""
        self.dim = dimIn
        self.members = list()

""" Member data holder"""
class Member():
    def __init__(self, dimIn="", codeIn="", valueIn=""):
        """Constructor."""
        self.dim = dimIn
        self.code = codeIn
        self.value = valueIn

    def __str__(self):
        return "Member Code: " + self.code + " Value: " + self.value

