
"""iXBRL parser and parser output objects

Call the parse function to parse an lxml ElementTree, returns an Ixbrl
object.
"""

from lxml import etree as ET
import datetime
import sys
import hashlib
import os

from . import transform
from . value import *
from . schema import Schema

from rdflib import URIRef

RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
RDFS = "http://www.w3.org/2000/01/rdf-schema#"

LOCAL = "http://cyberapocalyp.se/xbrl/"

# Relationships
IS_A = URIRef(RDF + "type")
LABEL = URIRef(RDFS + "label")
RDFS_CLASS = URIRef(RDFS + "Class")
RDFS_PROPERTY = URIRef(RDFS + "Property")

# Properties
CONTAINS = URIRef(LOCAL + "p#contains")
REPORTS = URIRef(LOCAL + "p#reports")
STARTS = URIRef(LOCAL + "p#starts")
ENDS = URIRef(LOCAL + "p#ends")
DATE = URIRef(LOCAL + "p#date")

# Types
CONTEXT = URIRef(LOCAL + "t#context") # Superclass
DIMENSION = URIRef(LOCAL + "t#dimension")
ENTITY = URIRef(LOCAL + "t#entity")
PERIOD = URIRef(LOCAL + "t#period")
INSTANT = URIRef(LOCAL + "t#instant")
ROOT = URIRef(LOCAL + "t#root")

# Instances
EVERYTHING = LOCAL + "root"

# Create a hex hash, short-hand
def create_hash(thing):
    hash = hashlib.sha1(str(thing).encode("utf-8"))
    return hash.hexdigest()

def to_qname(elt, name):
    ns, name = name.split(":", 2)
    ns = elt.nsmap[ns]
    return ET.QName(ns, name)

class Unit:
    """A unit"""
    pass

class Measure(Unit):
    """A simple measurement unit"""
    def __init__(self, measure):
        self.measure = measure
    def __str__(self):
        return str(self.measure.localname)

class Divide(Unit):
    """A unit formed by dividing two measurements"""
    def __init__(self, num, den):
        self.num = num
        self.den = den
    def __str__(self):
        return str(self.num) + "/" + str(self.den)

class Context:
    """An iXBRL context

    Attributes
    ----------
    entity : Entity
        The context's entity (None if not specified).
    period : Period
        The context's date period (None if not specified).
    instant : Period
        The context's instant date (None if not specified).
    dimensions : list<Dimension>
        List of dimensions, empty list if none.
    values : list<Value>
        List of values defined under this context.
    children : map<Relationship, Context>
        Map of relationship to child context.

    Methods
    -------
    to_string()
        Returns a string representation of the context
    get_uri()
        Constructs a URI for the context which is usable in e.g. RDF
        output
    get_triples()
        Converts a context into RDF triples. Returns a list of 3-tuples,
        each describing an RDF arc associated with the context.
        The first two elements of the 3-tuple are URIRef type,
        the second can be URIRef or Literal.

    This module organises contexts as a hierarchy, each context 
    connected to its parent through a Relationship which is a single 
    fragment of the iXBRL context (Entity, Period, Instant, Dimension).

    Example, if there are 3 contexts:
    - C01: entity X, period S - D, dimension D1 = V1
    - C02: entity X, period S - D, dimension D2 = V2
    - C03: entity X, instant I, dimension D3 = V3

    They would be organised:

                                root
                                  |
                                  |  relationship: Entity X
                                  |
                                 C01
                                  |
               ,------------------+---------------.
               |                                  |
               | rel: period S-D                  | rel: instant I
               |                                  |
              C02                                C03

    Navigate from one context to another through the children attribute

    """
    def __init__(self):
        self.entity = None
        self.period = None
        self.instant = None
        self.dimensions = []
        self.values = {}
        self.children = {}
    def copy(self):
        c = Context()
        c.entity = self.entity
        c.period = self.period
        c.instant = self.instant
        c.dimensions = [v for v in self.dimensions]
        return c
    def modify(self, rel):
        if isinstance(rel, Entity):
            self.entity = rel
        elif isinstance(rel, Period):
            self.period = rel
        elif isinstance(rel, Instant):
            self.instant = rel
        elif isinstance(rel, Dimension):
            self.dimensions.append(rel)

    def flatten(self):

        if not hasattr(self, "id") or self.id == None:
            raise RuntimeError("This context has no ID")

        cflat = {
            "id": self.id
        }
        if self.entity:
            cflat["entity"] = {
                "id": self.entity.id,
                "scheme": self.entity.scheme
            }
        if self.period:
            cflat["start"] = str(self.period.start)
            cflat["end"] = str(self.period.end)
        if self.instant:
            cflat["instant"] = str(self.instant.instant)
        if len(self.dimensions) > 0:
            cflat["dimensions"] = {
                dim.dimension.localname: dim.value.localname
                for dim in self.dimensions
            }

        return cflat

    def to_dict(self):

        ret = {}

        for rel, ctxt in self.children.items():

            id = rel.get_id()[:16]

            if isinstance(rel, Entity):
                if "entity" not in ret:
                    ret["entity"] = {}
                id = rel.id
                obj = ctxt.to_dict()
                obj["id"] = rel.id
                obj["scheme"] = rel.scheme
                ret["entity"][id] = obj                
            if isinstance(rel, Period):
                if "period" not in ret:
                    ret["period"] = {}
                id = str(rel.start) + ":" + str(rel.end)
                obj = ctxt.to_dict()
                obj["start"] = str(rel.start)
                obj["end"] = str(rel.end)
                ret["period"][id] = obj
            if isinstance(rel, Instant):
                if "instant" not in ret:
                    ret["instant"] = {}
                id = str(rel.instant)
                obj = ctxt.to_dict()
                obj["date"] = str(rel.instant)
                ret["instant"][id] = obj
            if isinstance(rel, Dimension):
                dim = rel.dimension.localname
                value = rel.value.localname
                if dim not in ret:
                    ret[dim] = {}
                obj = ctxt.to_dict()
                ret[dim][value] = obj

        for name, value in self.values.items():
            ret[name.localname] = value.to_dict()

        return ret

    def to_string(self):
        """Returns a string representation of the context"""
        val = self.to_dict()
        return str(val)
    def __str__(self):
        """Returns a string representation of the context"""
        val = self.to_dict()
        return str(val)
    def __repr__(self):
        return str(self)
    def dump(self):
        print("  Context:")
        if self.entity:
            print("    Entity: %s (%s)" % (self.entity.id, self.entity.scheme))
        if self.period:
            print("    Start:", self.period.start)
            print("    End:", self.period.end)
        if self.instant:
            print("    Instant:", self.instant)
        for d in self.dimensions:
            print("    %s: %s" % (d.dimension, d.value))
    def get_relationships(self):

        rels = []

        if self.entity:
            rels.append(self.entity)
        if self.period:
            rels.append(self.period)
        if self.instant:
            rels.append(self.instant)
        for dim in self.dimensions:
            rels.append(dim)

        return rels

    def get_id(self):
        rels = self.get_relationships()
        rep = "//".join([str(v) for v in rels])
        return create_hash(rep)

    def get_uri(self):
        """Constructs a URI for the context which is usable in e.g. RDF
        output
        """
        rels = self.get_relationships()

        if len(rels) == 0: return EVERYTHING

        url = LOCAL

        for rel in rels:
            url += rel.url_part()

        return url

    def get_triples(self, rel=None, entity_name=None):
        """
        Converts a context into RDF triples. Returns a list of 3-tuples,
        each describing an RDF arc associated with the context.
        The first two elements of the 3-tuple are URIRef type,
        the second can be URIRef or Literal.
        """

        tpl = []

        if rel == None:
            tpl.extend([
                (CONTAINS, LABEL, Literal("contains")),
                (REPORTS, LABEL, Literal("reports")),
                (STARTS, LABEL, Literal("starts")),
                (ENDS, LABEL, Literal("ends")),
                (DATE, LABEL, Literal("date")),

                (CONTAINS, IS_A, RDFS_PROPERTY),
                (REPORTS, IS_A, RDFS_PROPERTY),
                (STARTS, IS_A, RDFS_PROPERTY),
                (ENDS, IS_A, RDFS_PROPERTY),
                (DATE, IS_A, RDFS_PROPERTY),

                (CONTEXT, LABEL, Literal("Context")),
                (DIMENSION, LABEL, Literal("Dimension")),
                (ENTITY, LABEL, Literal("Entity")),
                (PERIOD, LABEL, Literal("Period")),
                (INSTANT, LABEL, Literal("Instant")),
                (ROOT, LABEL, Literal("Root")),

                (CONTEXT, IS_A, RDFS_CLASS),
                (DIMENSION, IS_A, RDFS_CLASS),
                (ENTITY, IS_A, CONTEXT),
                (PERIOD, IS_A, CONTEXT),
                (INSTANT, IS_A, CONTEXT),
                (ROOT, IS_A, CONTEXT),

            ])

        if rel == None:
            tpl.append((
                URIRef(self.get_uri()), IS_A, ROOT
            ))
        elif isinstance(rel, Dimension):
            tpl.append((
                URIRef(self.get_uri()), IS_A, rel.get_type()
            ))
            tpl.append((
                rel.get_type(), IS_A, DIMENSION
            ))
            tpl.append((
                rel.get_type(), LABEL, Literal(rel.dimension.localname)
            ))
        else:
            tpl.append((
                URIRef(self.get_uri()), IS_A, rel.get_type()
            ))

        if rel == None:
            tpl.append((
                URIRef(self.get_uri()),
                LABEL,
                Literal("everything")
            ))
        elif isinstance(rel, Entity) and entity_name != None:
            tpl.append((
                URIRef(self.get_uri()),
                LABEL,
                Literal(entity_name)
            ))
        else:
            tpl.append((
                URIRef(self.get_uri()),
                LABEL,
                Literal(rel.get_description())
            ))

        for rel, c in self.children.items():
            if isinstance(rel, Entity):
                tpl.append((
                    URIRef(self.get_uri()),
                    CONTAINS,
                    URIRef(c.get_uri())
                ))
            elif isinstance(rel, Period):
                tpl.append((
                    URIRef(self.get_uri()),
                    REPORTS,
                    URIRef(c.get_uri())
                ))
                tpl.append((
                    URIRef(c.get_uri()),
                    STARTS,
                    rel.get_start().to_rdf()
                ))
                tpl.append((
                    URIRef(c.get_uri()),
                    ENDS,
                    rel.get_end().to_rdf()
                ))
            elif isinstance(rel, Instant):
                tpl.append((
                    URIRef(self.get_uri()),
                    REPORTS,
                    URIRef(c.get_uri())
                ))
                tpl.append((
                    URIRef(c.get_uri()),
                    DATE,
                    rel.get_date().to_rdf()
                ))
            elif isinstance(rel, Dimension):
                tpl.append((
                    URIRef(self.get_uri()),
                    rel.get_name_uri(),
                    URIRef(c.get_uri())
                ))

            tpl.extend(c.get_triples(rel, entity_name))

        tpl.extend(self.get_value_triples())

        return tpl

    def get_value_triples(self):

        tpl = []

        for name, value in self.values.items():

            if isinstance(value, ET.QName):

                tpl.append((
                    URIRef(self.get_uri()),
                    URIRef("%s#%s" % (name.namespace, name.localname)),
                    URIRef("%s#%s" % (value.namespace, value.localname))
                ))

            else:

                tpl.append((
                    URIRef(self.get_uri()),
                    URIRef("%s#%s" % (name.namespace, name.localname)),
                    value.to_value().to_rdf()
                ))

            tpl.append((
                URIRef("%s#%s" % (name.namespace, name.localname)),
                IS_A,
                RDFS_PROPERTY
            ))

            tpl.append((
                URIRef("%s#%s" % (name.namespace, name.localname)),
                LABEL,
                Literal(name.localname)
            ))

        return tpl

class Value:
    """An iXBRL value"""
    def __init__(self):
        self.value = None
        self.context = None
    def dump(self):
        print("Value:")
        if self.name:
            print("  Name:", self.name)
        if self.context:
            self.context.dump()
        if self.value:
            print("  Value:", self.value)

    @staticmethod
    def recurse_elts(elt, lower=False):
        a = ""
        if elt.text:
            a += elt.text + " "
        for s in elt:
            a += Value.recurse_elts(s, True)
        if lower and elt.tail:
            a += elt.tail
        return a

    def get_raw(self):
        value = ""
        for elt in self.elements:
            value += Value.recurse_elts(elt)
        return value

    def to_string(self):
        """Represent as string"""
        return str(self.to_value())

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return str(self)

class NonNumeric(Value):
    """Represents an iXBRL nonNumeric value"""

    def to_value(self):
        raw = self.get_raw()
        if hasattr(self, "format") and self.format:
            value = transform.transform(self, raw)
        else:
            value = String(raw.strip())
        return value

    def to_dict(self):
        return str(self.to_value().get_value())

    def flatten(self):
        return {
            "name": self.name.localname,
            "context": self.context.id,
            "value": str(self.to_value().get_value())
        }

class NonFraction(Value):
    """Represents an iXBRL nonFraction value"""

    def to_value(self):
        raw = self.get_raw()
        if hasattr(self, "format") and self.format:
            value = transform.transform(self, raw)
        else:
            if raw in { "nil", "None", "none", "", "no", "No" }: raw = 0
            value = Float(float(raw) * self.scale, self.unit)
        return value
    def to_dict(self):
        return self.to_value().get_value()

    def flatten(self):
        return {
            "name": self.name.localname,
            "context": self.context.id,
            "value": self.to_value().get_value()
        }

class Fraction(Value):

    """Represents an iXBRL fraction value: Not implemented"""

    def get_raw(self):
        """Represent as string"""
        raise RuntimeError("Not implemented: Fraction")

class Relationship:
    """Represents a single fragment of the context definition.
    """
    def __repr__(self):
        return str(self)
    def __hash__(self):
        return str(self).__hash__()
    def __eq__(self, other):
        return str(self) == str(other)
    def get_id(self):
        rep = str(self)
        return create_hash(rep)
    def get_description(self):
        return str(self)

class Entity(Relationship):
    """Describes the entity definition of a context."""
    def __init__(self, id, scheme):
        self.id = id
        self.scheme = scheme
        self.name = None
    def __str__(self):
        return("entity(%s,%s)" % (self.id, self.scheme))
    def __repr__(self):
        return str(self)
    def get_description(self):
        if self.name:
            return "%s (%s)" % (
                self.name, self.id
            )
        else:
            return "Entity %s (%s)" % (
                self.id, self.scheme
            )
    def get_type(self):
        return ENTITY
    def url_part(self):
        return create_hash(self.scheme)[0:4] + "/" + self.id + "/"
    def to_dict(self):
        return {
            "id": self.id,
            "scheme": self.scheme
        }

class Period(Relationship):
    """Describes the period definition of a context."""
    def __init__(self, start, end):
        self.start, self.end = start, end
    def __str__(self):
        return("period(%s,%s)" % (self.start, self.end))
    def get_description(self):
        return "%s - %s" % (
            self.start, self.end
        )
    def get_type(self):
        return PERIOD
    def url_part(self):
        return "%s-%s/" % (self.start, self.end)
    def get_start(self):
        return Date(self.start)
    def get_end(self):
        return Date(self.end)

class Instant(Relationship):
    """Describes the period instant definition of a context."""
    def __init__(self, instant):
        self.instant = instant
    def __str__(self):
        return("instant(%s)" % (self.instant))
    def get_description(self):
        return "%s" % self.instant
    def get_type(self):
        return INSTANT
    def url_part(self):
        return "%s/" % (self.instant)
    def get_date(self):
        return Date(self.instant)

class Dimension(Relationship):
    """Describes a single dimension definition of a context."""
    def __init__(self, dimension, value):
        self.dimension = dimension
        self.value = value
    def __str__(self):
        return("dimension(%s,%s)" % (self.dimension, self.value))
    def get_description(self):
        return "%s" % (
            self.value.localname
        )
    def get_type(self):
        return URIRef(self.get_name_uri())
    def url_part(self):
        return "%s=%s/" % (self.dimension.localname, self.value.localname)
    def get_name_uri(self):
        return URIRef("%s#%s" % (
            self.dimension.namespace, self.dimension.localname
        ))
    def get_value_uri(self):
        return URIRef("%s#%s" % (
            self.value.namespace, self.value.localname
        ))

class Ixbrl:
    """
    Attributes
    ----------

    root : Context
        Root context
    contexts : map<id, Context>
        Map of iXBRL context identifier to context
    values : list<Value>
        List of values
    """

    def __init__(self):
        self.root = Context()

    def get_context(self, rels):

        cx = self.root

        for rel in rels:
            cx = self.lookup_context(cx, rel)

        return cx

    def lookup_context(self, cx, rel):

        key = rel

        if key in cx.children:
            return cx.children[key]

        ncx = cx.copy()

        ncx.modify(rel)

        cx.children[key] = ncx

        return ncx

    def context_iter(self):

        context_tree = {}

        for c in self.contexts.values():
            yield c, c

    def get_entity_name(self):

        # Companies House
        ent_legal_name = ET.QName(
            "http://xbrl.frc.org.uk/cd/2019-01-01/business",
            "EntityCurrentLegalOrRegisteredName"
        )

        # SEC
        ent_reg_name = ET.QName(
            "http://xbrl.sec.gov/dei/2020-01-31",
            "EntityRegistrantName"
        )

        # ESEF
        name_of_rep_ent = ET.QName(
            "http://xbrl.ifrs.org/taxonomy/2017-03-09/ifrs-full",
            "NameOfReportingEntityOrOtherMeansOfIdentification"
        )

        for c in self.contexts.values():
            for v in c.values.values():
                if v.name in {ent_legal_name, ent_reg_name, name_of_rep_ent}:
                    return v.to_string()

        return None

    def to_dict(self):
        return self.root.to_dict()

    def flatten(self):
        ret = {
            "contexts": [],
            "values": []
        }

        for c in self.contexts.values():

            ret["contexts"].append(c.flatten())

        for value in self.values.values():
            ret["values"].append(value.flatten())

        return ret

    def get_triples(self):
        """Return a list of RDF triples."""
        return self.root.get_triples(None, self.get_entity_name())

    def load_schema(self, base_url=None):

        s = Schema()

        for uri in self.schemas:
            s.load_uri(uri, base_url)

        return s

# Takes an ElementTree document and extracts a dict mapping iXBRL tag names
# to values.
def parse(doc):
    """ Parses an lxml ElementTree containing an iXBRL document.

    Returns
    -------
    An Ixbrl object.
    """

    i = Ixbrl()

    values = {}

    ns = {
        "ix": "http://www.xbrl.org/2013/inlineXBRL",
        "xbrli": "http://www.xbrl.org/2003/instance",
        "xbrldi": "http://xbrl.org/2006/xbrldi",
        "xlink": "http://www.w3.org/1999/xlink",
        "link": "http://www.xbrl.org/2003/linkbase"
    }

    units = {}

    # FIXME: Delete entity_name from here.
    entity_name = None

    i.schemas = []
    for elt in doc.findall(".//link:schemaRef", ns):
        i.schemas.append(elt.get(ET.QName(ns["xlink"], "href")))

    for elt in doc.findall(".//ix:nonNumeric", ns):

        name = to_qname(elt, elt.get("name"))
        v = NonNumeric()
        v.elements = [elt]

        # Companies House
        ent_legal_name = ET.QName(
            "http://xbrl.frc.org.uk/cd/2019-01-01/business",
            "EntityCurrentLegalOrRegisteredName"
        )

        # SEC
        ent_reg_name = ET.QName(
            "http://xbrl.sec.gov/dei/2020-01-31",
            "EntityRegistrantName"
        )

        # ESEF
        name_of_rep_ent = ET.QName(
            "http://xbrl.ifrs.org/taxonomy/2017-03-09/ifrs-full",
            "NameOfReportingEntityOrOtherMeansOfIdentification"
        )

        if entity_name == None:
            if name == ent_legal_name:
                entity_name = v.to_string()
            if name == ent_reg_name:
                entity_name = v.to_string()
            if name == name_of_rep_ent:
                entity_name = v.to_string()

    for unit_elt in doc.findall(".//xbrli:unit", ns):

        id = unit_elt.get("id")

        try:
            div_elt = unit_elt.find("xbrli:divide", ns)
            num_elt = div_elt.find(
                "./xbrli:unitNumerator/xbrli:measure", ns
            )
            den_elt = div_elt.find(
                "./xbrli:unitDenominator/xbrli:measure", ns
            )

            unit = Divide(
                Measure(to_qname(num_elt, num_elt.text)),
                Measure(to_qname(den_elt, den_elt.text))
            )
            unit.id = id

            units[id] = unit

            continue

        except:
            pass

        meas_elt = unit_elt.find("xbrli:measure", ns)
        units[id] = Measure(to_qname(meas_elt, meas_elt.text))
        units[id].id = id

    contexts = {}

    for ctxt_elt in doc.findall(".//xbrli:context", ns):

        rels = []

        id = ctxt_elt.get("id")

        for ent_elt in ctxt_elt.findall(".//xbrli:entity", ns):
            for id_elt in ent_elt.findall(".//xbrli:identifier", ns):
                rels.append(Entity(id_elt.text, id_elt.get("scheme")))

        for ent_elt in ctxt_elt.findall(".//xbrli:period", ns):
            try:
                sd = ent_elt.find(".//xbrli:startDate", ns).text
                sd = datetime.datetime.fromisoformat(sd).date()
                ed = ent_elt.find(".//xbrli:endDate", ns).text
                ed = datetime.datetime.fromisoformat(ed).date()
                rels.append(Period(sd, ed))
            except:
                pass

            try:
                inst = ent_elt.find(".//xbrli:instant", ns).text
                inst = datetime.datetime.fromisoformat(inst).date()
                rels.append(Instant(inst))
            except:
                pass

        for seg_elt in ctxt_elt.findall(".//xbrli:segment", ns):
            for em_elt in seg_elt.findall(".//xbrldi:explicitMember", ns):

                dimension = to_qname(em_elt, em_elt.get("dimension"))
                value = to_qname(em_elt, em_elt.text.strip())

                rels.append(Dimension(dimension, value))

        ctxt = i.get_context(rels)

        # This might relable another context.
        ctxt.id = id

        contexts[id] = ctxt

    continuation = {}

    for elt in doc.findall(".//ix:continuation", ns):
        cid = elt.get("id")
        continuation[cid] = elt

    for elt in doc.findall(".//ix:nonNumeric", ns):
        name = to_qname(elt, elt.get("name"))
        cont = elt.get("continuedAt")
        ctxt = contexts[elt.get("contextRef")]
        key = (ctxt, name)
        v = NonNumeric()
        v.name = name
        v.context = ctxt
        v.elements = [elt]

        format = elt.get("format")
        if format:
            v.format = to_qname(elt, format)

        ctxt.values[name] = v
        values[key] = v

        while cont != None:
            contelt = continuation[cont]
            for s in contelt:
                v.elements.append(s)
            cont = contelt.get("continuedAt")

    for elt in doc.findall(".//ix:nonFraction", ns):
        name = to_qname(elt, elt.get("name"))
        ctxt = contexts[elt.get("contextRef")]
        cont = elt.get("continuedAt")
        key = (ctxt, name)

        try:
            scale = elt.get("scale")
            scale = 10 ** int(scale)
        except:
            scale = 1

        v = NonFraction()
        v.name = name
        v.context = ctxt

        v.decimals = elt.get("decimals")

        format = elt.get("format")
        if format:
            v.format = to_qname(elt, format)
        else:
            v.format = None

        v.scale = scale
        v.elements = [elt]
        v.unit = units[elt.get("unitRef")]
        ctxt.values[name] = v
        values[key] = v

        while cont != None:
            contelt = continuation[cont]
            for s in contelt:
                v.elements.append(s)
            cont = contelt.get("continuedAt")

    i.units = units
    i.values = values
    i.contexts = contexts

    return i
