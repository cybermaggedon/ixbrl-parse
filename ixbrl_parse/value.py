
from rdflib import Graph, Literal, RDF, URIRef
from rdflib.namespace import XSD

class Val:
    def to_string(self):
        return str(self.value)
    def __str__(self):
        return self.to_string()
    def __repr__(self):
        return self.to_string()

class Boolean(Val):
    def __init__(self, value):
        self.value = value
    def to_rdf(self):
        return Literal(self.value, datatype=XSD.boolean)

class Date(Val):
    def __init__(self, value):
        self.value = value
    def to_rdf(self):
        return Literal(self.value, datatype=XSD.date)

class String(Val):
    def __init__(self, value):
        self.value = value
    def to_rdf(self):
        return Literal(self.value, datatype=XSD.string)

class Float(Val):
    def __init__(self, value, unit=None):
        self.value = value
        self.unit = unit
    def to_string(self):
        if self.unit:
            return "%s (%s)" % (str(self.value), str(self.unit))
        else:
            return str(self.value)
    def to_rdf(self):
        return Literal(self.value, datatype=XSD.float)

class MonthDay(Val):
    def __init__(self, m, d):
        self.m = m
        self.d = d
    def to_string(self):
        return "--%02d-%02d" % (self.m, self.d)
    def to_rdf(self):
        return Literal(str(self), datatype=XSD.string)

class Duration(Val):
    def __init__(self, value):
        self.value = value
    def to_rdf(self):
        return Literal(str(self.value), datatype=XSD.duration)

