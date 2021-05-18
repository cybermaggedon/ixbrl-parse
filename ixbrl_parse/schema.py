
import urllib
import os
import requests
import hashlib
from lxml import etree as ET

cache_directory = ".xbrl-cache"

# Create a hex hash, short-hand
def create_hash(thing):
    hash = hashlib.sha1(str(thing).encode("utf-8"))
    return hash.hexdigest()

class Schema:

    """Minimal XBRL schema processing in order to get hold of labels.
    This class downloads XML schema resources behind-the-scenes and
    caches in a local .xbrl-cache directory.  The load_uri method is used
    to load resources beginning with the base taxonomy schema, and the base_url
    parameter is used to help resolve URLs.
    """

    def __init__(self):
        self.simple = {}
        self.complex = {}
        self.attribute_group = {}
        self.element = {}
        self.element_id = {}
        self.labels = {}
        self.label_arcs = {}
        self.label_loc = {}

    @staticmethod
    def load(uri):

        s = Schema()
        s.load_uri(uri)

    def get_label(self, name):

        try:

            loc = self.element_id[name]
            id = self.label_loc[loc]
            lbl_id = self.label_arcs[id]

            LABEL = "http://www.xbrl.org/2003/role/label"
            lbl = self.labels[(lbl_id, LABEL)]
            return lbl

        except Exception as e:
            return None

    def fetch_cached_resource(self, uri):

        try:
            os.mkdir(cache_directory + "/")
        except Exception as e:
            pass

        localname = "%s/%s" % (cache_directory, create_hash(uri))

        try:
            return open(localname, "rb").read()
        except:
            pass

#        sys.stderr.write(str("%s...\n" % uri))

        resp = requests.get(uri)
        if resp.status_code != 200:
            raise RuntimeError("Response code: %d" % resp.status_code)

        with open(localname, "wb") as f:
            for chunk in resp.iter_content(16384):
                f.write(chunk)

        return open(localname, "rb").read()

    def load_labels(self, uri):
        rsrc = self.fetch_cached_resource(uri)
        tree = ET.fromstring(rsrc)

        nsmap = {
            "xmls": "http://www.w3.org/2001/XMLSchema",
            None: "http://www.xbrl.org/2003/linkbase",
            "xlink": "http://www.w3.org/1999/xlink"
        }

        for elt in tree.findall("labelLink/loc", nsmap):
            src = elt.get("{%s}href" % nsmap["xlink"])
            src = urllib.parse.urljoin(uri, src)
            label = elt.get("{%s}label" % nsmap["xlink"])
            self.label_loc[src] = label

        for elt in tree.findall("labelLink/labelArc", nsmap):
            f = elt.get("{%s}from" % nsmap["xlink"])
            t = elt.get("{%s}to" % nsmap["xlink"])
            self.label_arcs[f] = t

        for elt in tree.findall("labelLink/label", nsmap):
            lbl = elt.get("{%s}label" % nsmap["xlink"])
            role = elt.get("{%s}role" % nsmap["xlink"])
            self.labels[(lbl, role)] = elt.text

    def load_uri(self, uri, base_uri=None):

        if base_uri != None:
            uri = urllib.parse.urljoin(base_uri, uri)

        nsmap = {
            None: "http://www.w3.org/2001/XMLSchema",
            "link": "http://www.xbrl.org/2003/linkbase",
            "xlink": "http://www.w3.org/1999/xlink"
        }

        rsrc = self.fetch_cached_resource(uri)

        tree = ET.fromstring(rsrc)

        tns = tree.get("targetNamespace")

        # Process imports
        for elt in tree.findall("import", nsmap):
            ns = elt.get("namespace")
            loc = elt.get("schemaLocation")
            loc = urllib.parse.urljoin(uri, loc)
            self.load_uri(loc, base_uri)

        for elt in tree.findall("simpleType", nsmap):
            name = ET.QName(nsmap[None], elt.get("name"))
            self.simple[name] = elt

        for elt in tree.findall("complexType", nsmap):
            name = ET.QName(nsmap[None], elt.get("name"))
            self.complex[name] = elt

        for elt in tree.findall("attributeGroup", nsmap):
            name = ET.QName(nsmap[None], elt.get("name"))
            self.attribute_group[name] = elt

        for elt in tree.findall("element", nsmap):
            name = ET.QName(tns, elt.get("name"))
            try:
                id = elt.get("id")
                id = urllib.parse.urljoin(uri, "#" + id)
            except:
                id = None

            self.element[name] = elt

            if id != None:
                self.element_id[name] = id

        for elt in tree.findall("annotation/appinfo", nsmap):

            for elt2 in elt.findall("link:linkbaseRef", nsmap):
                role = elt2.get("{%s}role" % nsmap["xlink"])

                if role == "http://www.xbrl.org/2003/role/labelLinkbaseRef":

                    loc = elt2.get("{%s}href" % nsmap["xlink"])
                    loc = urllib.parse.urljoin(uri, loc)
                    self.load_labels(loc)
