
from rdflib import Graph, Literal, RDF, URIRef
from rdflib.namespace import XSD

class Val:
    def to_string(self):
        return str(self.value)
    def __str__(self):
        return self.to_string()
    def __repr__(self):
        return self.to_string()
    def get_value(self):
        return self.value
    def get_unit(self):
        return None

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
    def get_unit(self):
        return str(self.unit)

class MonthDay(Val):
    def __init__(self, m, d):
        self.m = m
        self.d = d
    def to_string(self):
        return "--%02d-%02d" % (self.m, self.d)
    def to_rdf(self):
        return Literal(str(self), datatype=XSD.string)
    def to_value(self):
        return self.to_string()

class Duration(Val):
    def __init__(self, value):
        self.value = value
    def to_rdf(self):
        return Literal(str(self), datatype=XSD.duration)
    def to_string(self):
        D = self.value.days
        s = self.value.seconds

        if D > 356:
            Y = int(D / 356)
            D -= Y * 356
        else:
            Y = 0

        if D > 30:
            M = int(D / 30)
            D -= M * 30
        else:
            M = 0

        if s > 3600:
            h = int(s / 3600)
            s -= h * 3600
        else:
            h = 0

        if s > 60:
            m = int(s / 60)
            s -= m * 60
        else:
            m = 0

        ret = "P"
        if Y > 0:
            ret += "%dY" % Y
        if M > 0:
            ret += "%dM" % M
        if D > 0:
            ret += "%dD" % D

        if h > 0 or m > 0 or s > 0:
            ret += "T"

            if h > 0:
                ret += "%dH" % h
            if m > 0:
                ret += "%dM" % m
            if s > 0:
                ret += "%dS" % s

        return ret
    def to_value(self):
        return self.to_string()
