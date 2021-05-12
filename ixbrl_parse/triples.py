
"""
RDF triple placeholders.
"""
maxsize=200

class Uri:
    """Represents a RDF URI"""
    def __init__(self, uri):
        self.uri = uri
    def __str__(self):
        return "<" + self.uri + ">"

class String:
    """Represents an RDF string"""
    def __init__(self, value):
        self.value = value
    def __str__(self):

        val = self.value
        val = val.strip()
        val = val.replace("\t", " ")
        val = val.replace("  ", " ")

        # truncate
        val = val[:maxsize]

        return '"' + val + '"'

