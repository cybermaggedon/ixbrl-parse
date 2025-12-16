#!/usr/bin/env python3

"""Command-line interface entry points for ixbrl-parse tools."""

import sys
import argparse
import csv
import json
import datetime
from lxml import etree as ET

from ixbrl_parse.ixbrl import parse, Entity, Period, Instant, Dimension, Measure, Divide
from rdflib import Graph


def dump_main():
    """Reads an iXBRL file on input, and dumps the structure, semi-human-readable."""

    maxwidth = 40

    parser = argparse.ArgumentParser(description=dump_main.__doc__)
    parser.add_argument('input', metavar='input', nargs=1,
                        help='Input iXBRL file')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Turn on verbose output.')

    args = parser.parse_args(sys.argv[1:])

    tree = ET.parse(args.input[0])
    i = parse(tree)

    if args.verbose:
        sys.stderr.write("Read %s.\n" % args.input)

    def qname_repr(qname):
        nsmap = {
            "http://fasb.org/us-gaap/2019-01-31": "us-gaap",
            "http://fasb.org/us-gaap/2020-01-31": "us-gaap",
            "http://fasb.org/srt/2019-01-31": "us-srt",
            "http://fasb.org/srt/2020-01-31": "us-srt",
            "http://xbrl.sec.gov/dei/2020-01-31": "sec",
            "http://xbrl.sec.gov/dei/2019-01-31": "sec",
            "http://xbrl.sec.gov/country/2020-01-31": "country",
            "http://xbrl.frc.org.uk/cd/2019-01-01/business": "uk-bus",
            "http://xbrl.frc.org.uk/fr/2019-01-01/core": "uk-core",
            "http://xbrl.frc.org.uk/reports/2019-01-01/direp": "uk-direp",
            "http://xbrl.frc.org.uk/reports/2019-01-01/aurep": "uk-aurep",
            "http://xbrl.frc.org.uk/cd/2019-01-01/currencies": "currencies",
            "http://xbrl.frc.org.uk/cd/2019-01-01/countries": "countries",
            "http://xbrl.frc.org.uk/cd/2014-09-01/countries": "countries",
            "http://xbrl.frc.org.uk/fr/2014-09-01/core": "uk-core",
            "http://xbrl.frc.org.uk/cd/2014-09-01/business": "uk-bus",
            "http://xbrl.frc.org.uk/char/2019-01-01": "char",
            "http://xbrl.frc.org.uk/reports/2014-09-01/direp": "uk-direp",
            "http://xbrl.frc.org.uk/reports/2014-09-01/aurep": "uk-aurep",
            "http://xbrl.frc.org.uk/reports/2014-09-01/accrep": "uk-accrep",
            "http://xbrl.frc.org.uk/reports/2019-01-01/accrep": "uk-accrep",
            "http://www.hmrc.gov.uk/schemas/ct/comp/2020-04-01": "ct-comp",
            "http://www.hmrc.gov.uk/schemas/ct/dpl/2019-01-01": "ct-dpl",
            "http://xbrl.ifrs.org/taxonomy/2017-03-09/ifrs-full": "ifrs-full",
        }

        if qname.namespace in nsmap:
            return nsmap[qname.namespace] + ":" + qname.localname

        return str(qname)

    def cdump(ctxt, level=0):
        indent = "    " * level
        for rel, c in ctxt.children.items():
            if isinstance(rel, Entity):
                print("%sEntity: %s (%s)" % (indent, rel.id, rel.scheme))
            if isinstance(rel, Period):
                print("%sPeriod: %s - %s" % (indent, rel.start, rel.end))
            if isinstance(rel, Instant):
                print("%sInstant: %s" % (indent, rel.instant))
            if isinstance(rel, Dimension):
                print("%sDimension: %s = %s" % (
                    indent, qname_repr(rel.dimension), qname_repr(rel.value)
                ))
            for name, value in c.values.items():
                if value.unit:
                    print("%s- %s: %s" % (indent, qname_repr(name), value))
                else:
                    if len(str(value)) > maxwidth:
                        print("%s- %s: %s..." % (
                            indent, qname_repr(name), str(value)[:40]
                        ))
                    else:
                        print("%s- %s: %s" % (indent, qname_repr(name), str(value)))
            cdump(c, level + 1)

    cdump(i.root)


def report_main():
    """Reads an iXBRL file on input, and dumps the structure with schema labels."""

    maxwidth = 40

    parser = argparse.ArgumentParser(description=report_main.__doc__)
    parser.add_argument('input', metavar='input', nargs=1,
                        help='Input iXBRL file')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Turn on verbose output.')
    parser.add_argument('--base-url', '-base', '-u',
                        help='Base URL for further schema fetches')
    parser.add_argument('--lang', '-l', dest='lang_prefs',
                        help='Comma-separated list of preferred language codes (e.g., "en,en-GB,cy"). Default: "en,en-GB,en-US,cy,cy-GB"')

    args = parser.parse_args(sys.argv[1:])

    lang_prefs = None
    if args.lang_prefs:
        lang_prefs = [lang.strip() for lang in args.lang_prefs.split(',')]

    tree = ET.parse(args.input[0])
    i = parse(tree)

    if args.verbose:
        sys.stderr.write("Read %s.\n" % args.input)

    def qname_repr(qname):
        nsmap = {
            "http://fasb.org/us-gaap/2019-01-31": "us-gaap",
            "http://fasb.org/us-gaap/2020-01-31": "us-gaap",
            "http://fasb.org/srt/2019-01-31": "us-srt",
            "http://fasb.org/srt/2020-01-31": "us-srt",
            "http://xbrl.sec.gov/dei/2020-01-31": "sec",
            "http://xbrl.sec.gov/dei/2019-01-31": "sec",
            "http://xbrl.sec.gov/country/2020-01-31": "country",
            "http://xbrl.frc.org.uk/cd/2019-01-01/business": "uk-bus",
            "http://xbrl.frc.org.uk/fr/2019-01-01/core": "uk-core",
            "http://xbrl.frc.org.uk/reports/2019-01-01/direp": "uk-direp",
            "http://xbrl.frc.org.uk/reports/2019-01-01/aurep": "uk-aurep",
            "http://xbrl.frc.org.uk/cd/2019-01-01/currencies": "currencies",
            "http://xbrl.frc.org.uk/cd/2019-01-01/countries": "countries",
            "http://xbrl.frc.org.uk/cd/2014-09-01/countries": "countries",
            "http://xbrl.frc.org.uk/fr/2014-09-01/core": "uk-core",
            "http://xbrl.frc.org.uk/cd/2014-09-01/business": "uk-bus",
            "http://xbrl.frc.org.uk/char/2019-01-01": "char",
            "http://xbrl.frc.org.uk/reports/2014-09-01/direp": "uk-direp",
            "http://xbrl.frc.org.uk/reports/2014-09-01/aurep": "uk-aurep",
            "http://xbrl.frc.org.uk/reports/2014-09-01/accrep": "uk-accrep",
            "http://xbrl.frc.org.uk/reports/2019-01-01/accrep": "uk-accrep",
            "http://www.hmrc.gov.uk/schemas/ct/comp/2020-04-01": "ct-comp",
            "http://www.hmrc.gov.uk/schemas/ct/dpl/2019-01-01": "ct-dpl",
            "http://xbrl.ifrs.org/taxonomy/2017-03-09/ifrs-full": "ifrs-full",
        }

        if qname.namespace in nsmap:
            return nsmap[qname.namespace] + ":" + qname.localname

        return str(qname)

    schema = i.load_schema(args.base_url, lang_prefs=lang_prefs)

    def get_label(name):
        lbl = schema.get_label(name)
        if lbl:
            return lbl
        return qname_repr(name)

    def cdump(ctxt, level=0):
        indent = "    " * level
        for rel, c in ctxt.children.items():
            if isinstance(rel, Entity):
                print("%sEntity: %s (%s)" % (indent, rel.id, rel.scheme))
            if isinstance(rel, Period):
                print("%sPeriod: %s - %s" % (indent, rel.start, rel.end))
            if isinstance(rel, Instant):
                print("%sInstant: %s" % (indent, rel.instant))
            if isinstance(rel, Dimension):
                dim_lbl = get_label(rel.dimension)
                seg_lbl = get_label(rel.value)
                print("%sDimension: %s = %s" % (indent, dim_lbl, seg_lbl))

            for name, value in c.values.items():
                label = get_label(name)
                if value.unit:
                    print("%s- %s: %s" % (indent, label, value))
                else:
                    if len(str(value)) > maxwidth:
                        print("%s- %s: %s..." % (indent, label, str(value)[:40]))
                    else:
                        print("%s- %s: %s" % (indent, label, str(value)))

            cdump(c, level + 1)

    cdump(i.root)


def markdown_main():
    """Reads an iXBRL file on input, and outputs a markdown report."""

    try:
        from tabulate import tabulate
    except ImportError:
        sys.stderr.write("Error: tabulate module required. Install with: pip install tabulate\n")
        sys.exit(1)

    parser = argparse.ArgumentParser(description=markdown_main.__doc__)
    parser.add_argument('input', metavar='input', nargs=1,
                        help='Input iXBRL file')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Turn on verbose output.')
    parser.add_argument('--base-url', '-base', '-u',
                        help='Base URL for further schema fetches')

    args = parser.parse_args(sys.argv[1:])

    tree = ET.parse(args.input[0])
    i = parse(tree)

    if args.verbose:
        sys.stderr.write("Read %s.\n" % args.input)

    def qname_repr(qname):
        return str(qname)

    schema = i.load_schema(args.base_url)

    def get_label(name):
        lbl = schema.get_label(name)
        if lbl:
            return lbl
        return qname_repr(name)

    def cdump(ctxt, level=0):
        for rel, c in ctxt.children.items():
            title = ""

            if isinstance(rel, Entity):
                title += "Entity: %s (%s) " % (rel.id, rel.scheme)
            if isinstance(rel, Period):
                title += "Period: %s - %s " % (rel.start, rel.end)
            if isinstance(rel, Instant):
                title += "Instant: %s " % rel.instant
            if isinstance(rel, Dimension):
                dim_lbl = get_label(rel.dimension)
                seg_lbl = get_label(rel.value)
                title += "Dimension: %s = %s " % (dim_lbl, seg_lbl)

            print(("#" * (level + 1)) + " " + title)
            print()

            rows = []
            if len(c.values) > 0:
                for name, value in c.values.items():
                    label = get_label(name)
                    value = str(value)
                    rows.append((label[:50], value[:30]))

                print(tabulate(rows, tablefmt="github"))
                print()

            cdump(c, level + 1)

    print()
    cdump(i.root)
    print()


def to_rdf_main():
    """Reads an iXBRL file on input, and outputs an RDF representation."""

    parser = argparse.ArgumentParser(description=to_rdf_main.__doc__)
    parser.add_argument('input', metavar='input', nargs=1,
                        help='Input iXBRL file')
    parser.add_argument('--format', '-f', default="n3",
                        help='Output format (default: n3)')

    args = parser.parse_args(sys.argv[1:])

    tree = ET.parse(args.input[0])
    i = parse(tree)

    rels = i.get_triples()
    g = Graph()

    for rel in rels:
        g.add((rel[0], rel[1], rel[2]))

    result = g.serialize(format=args.format)
    # Handle both old (bytes) and new (str) rdflib versions
    if isinstance(result, bytes):
        print(result.decode("utf-8"))
    else:
        print(result)


def to_csv_main():
    """Reads an iXBRL file on input, and outputs a CSV representation."""

    maxwidth = 200

    parser = argparse.ArgumentParser(description=to_csv_main.__doc__)
    parser.add_argument('input', metavar='input', nargs=1,
                        help='Input iXBRL file')

    args = parser.parse_args(sys.argv[1:])

    tree = ET.parse(args.input[0])
    i = parse(tree)

    fields = [
        "namespace", "name", "value", "unit", "entity", "scheme", "start", "end",
        "instant"
    ]
    fieldset = set(fields)
    rows = []

    for c in i.contexts.values():
        for v in c.values.values():
            row = {
                "namespace": v.name.namespace,
                "name": v.name.localname,
                "value": str(v.to_value().get_value())[:maxwidth],
                "unit": v.to_value().get_unit(),
            }

            if c.entity:
                row["entity"] = c.entity.id
                row["scheme"] = c.entity.scheme

            if c.period:
                row["start"] = c.period.start
                row["end"] = c.period.end

            if c.instant:
                row["instant"] = c.instant.instant

            for dim in c.dimensions:
                d = dim.dimension.localname
                v = dim.value.localname

                if d not in fieldset:
                    fields.append(d)
                    fieldset.add(d)

                row[d] = v

            rows.append(row)

    writer = csv.DictWriter(sys.stdout, fields)
    writer.writeheader()

    for row in rows:
        writer.writerow(row)


def to_json_main():
    """Reads an iXBRL file on input, and outputs a JSON representation."""

    parser = argparse.ArgumentParser(description=to_json_main.__doc__)
    parser.add_argument('input', metavar='input', nargs=1,
                        help='Input iXBRL file')
    parser.add_argument('--format', '-f', default="hierarchy",
                        help="Output format, one of: flat, hierarchy, labels (default: hierarchy)")
    parser.add_argument('--base-url', '-base', '-u',
                        help='Base URL for further schema fetches')

    args = parser.parse_args(sys.argv[1:])

    tree = ET.parse(args.input[0])
    i = parse(tree)

    if args.format == "flat":
        rels = i.flatten()
    elif args.format == "hierarchy":
        rels = i.to_dict()
    elif args.format == "labeled":
        rels = i.to_dict(i.load_schema(args.base_url))
    else:
        raise RuntimeError("Format %s not known" % args.format)

    print(json.dumps(rels, indent=4))


def to_xbrl_main():
    """Reads an iXBRL file on input, and outputs an XBRL instance."""

    XBRLI_NS = "http://www.xbrl.org/2003/instance"
    XBRLDI_NS = "http://xbrl.org/2006/xbrldi"
    XLINK_NS = "http://www.w3.org/1999/xlink"
    LINK_NS = "http://www.xbrl.org/2003/linkbase"

    parser = argparse.ArgumentParser(description=to_xbrl_main.__doc__)
    parser.add_argument('input', metavar='input', nargs=1,
                        help='Input iXBRL file')

    args = parser.parse_args(sys.argv[1:])

    tree = ET.parse(args.input[0])
    i = parse(tree)

    nsmap = {
        "xbrli": XBRLI_NS,
        "xbrldi": XBRLDI_NS,
        "xlink": XLINK_NS,
        "link": LINK_NS,
    }

    nsmap_set = set([v for v in nsmap.values()])
    nscount = [0]

    def maybe_add_namespace(q):
        if q.namespace not in nsmap_set:
            nsmap["ns%d" % nscount[0]] = q.namespace
            nscount[0] += 1
            nsmap_set.add(q.namespace)

    def maybe_add_measure(m):
        if isinstance(m, Measure):
            maybe_add_namespace(m.measure)
        elif isinstance(m, Divide):
            maybe_add_measure(m.num)
            maybe_add_measure(m.den)

    for c in i.contexts.values():
        for dim in c.dimensions:
            maybe_add_namespace(dim.dimension)
            maybe_add_namespace(dim.value)

    for v in i.values.values():
        maybe_add_namespace(v.name)

    for v in i.units.values():
        maybe_add_measure(v)

    root_elt = ET.Element("{%s}xbrl" % XBRLI_NS, nsmap=nsmap)

    for schema in i.schemas:
        ref_elt = ET.SubElement(root_elt, "{%s}schemaRef" % LINK_NS)
        ref_elt.set(ET.QName(XLINK_NS, "href"), schema)
        ref_elt.set(ET.QName(XLINK_NS, "type"), "simple")

    for cid, c in i.contexts.items():
        c_elt = ET.SubElement(root_elt, "{%s}context" % XBRLI_NS)

        if c.entity:
            e_elt = ET.SubElement(c_elt, "{%s}entity" % XBRLI_NS)
            i_elt = ET.SubElement(e_elt, "{%s}identifier" % XBRLI_NS)
            i_elt.set("scheme", c.entity.scheme)
            i_elt.text = str(c.entity.id)

            if len(c.dimensions) > 0:
                seg_elt = ET.SubElement(e_elt, "{%s}segment" % XBRLI_NS)
                for dim in c.dimensions:
                    mem_elt = ET.SubElement(seg_elt, "{%s}explicitMember" % XBRLDI_NS)
                    mem_elt.set("dimension", dim.dimension)
                    mem_elt.text = dim.value

        if c.instant:
            p_elt = ET.SubElement(c_elt, "{%s}period" % XBRLI_NS)
            inst_elt = ET.SubElement(p_elt, "{%s}instant" % XBRLI_NS)
            inst_elt.text = str(c.instant.instant)

        if c.period:
            p_elt = ET.SubElement(c_elt, "{%s}period" % XBRLI_NS)
            ET.SubElement(p_elt, "{%s}startDate" % XBRLI_NS).text = str(c.period.start)
            ET.SubElement(p_elt, "{%s}endDate" % XBRLI_NS).text = str(c.period.end)

        c_elt.set("id", cid)

    for u in i.units.values():
        u_elt = ET.SubElement(root_elt, "{%s}unit" % XBRLI_NS)
        u_elt.set("id", u.id)
        if isinstance(u, Measure):
            ET.SubElement(u_elt, "{%s}measure" % XBRLI_NS).text = u.measure
        elif isinstance(u, Divide):
            div_elt = ET.SubElement(u_elt, "{%s}divide" % XBRLI_NS)
            ET.SubElement(
                ET.SubElement(div_elt, "{%s}unitNumerator" % XBRLI_NS), "measure"
            ).text = u.num.measure
            ET.SubElement(
                ET.SubElement(div_elt, "{%s}unitDenominator" % XBRLI_NS), "measure"
            ).text = u.den.measure

    for v in i.values.values():
        v_elt = ET.SubElement(root_elt, v.name)
        v_elt.set("contextRef", v.context.id)
        v_elt.text = str(v.to_value().get_value())

        if hasattr(v, "decimals") and v.decimals:
            v_elt.set("decimals", str(v.decimals))

        if v.unit:
            v_elt.set("unitRef", v.unit.id)

    enc = ET.tostring(root_elt, pretty_print=True, xml_declaration=True,
                      encoding="utf-8")
    print(enc.decode("utf-8"))


def to_kv_main():
    """Reads an iXBRL file on input, and outputs a key-value representation."""

    parser = argparse.ArgumentParser(description=to_kv_main.__doc__)
    parser.add_argument('input', metavar='input', nargs=1,
                        help='Input iXBRL file')
    parser.add_argument('--separator', '-s', default="|",
                        help="Output field separator, (default: |)")

    args = parser.parse_args(sys.argv[1:])

    tree = ET.parse(args.input[0])
    i = parse(tree)

    def dump(d, prefix=[]):
        for k, v in d.items():
            key = prefix + [k]
            if isinstance(v, dict):
                dump(v, key)
            else:
                print("%s%s%s" % (".".join(key), args.separator, str(v)[:40]))

    rels = i.to_dict()
    dump(rels)


def diff_main():
    """Outputs differences between two iXBRL documents."""

    parser = argparse.ArgumentParser(description=diff_main.__doc__)
    parser.add_argument('input', metavar='input', nargs=2,
                        help='Input files to compare')
    parser.add_argument('--format', '-f', default="text",
                        help="Output format, one of 'text', 'csv' (default: text)")

    args = parser.parse_args(sys.argv[1:])

    tree1 = ET.parse(args.input[0])
    tree2 = ET.parse(args.input[1])

    i1 = parse(tree1)
    i2 = parse(tree2)

    def compare(a, b, path=[], csv_mode=False):
        ret = []

        b_map = {k.localname: v for k, v in b.values.items()}

        for name, value in a.values.items():
            if name.localname in b_map:
                vala = str(value.to_value().get_value())[:50]
                valb = str(b_map[name.localname].to_value().get_value())[:50]
                if vala != valb:
                    ret.append({
                        "path": path,
                        "name": name.localname,
                        "a": vala,
                        "b": valb,
                    })

        for rel, ctxt in a.children.items():
            if rel in b.children:
                ret.extend(compare(a.children[rel], b.children[rel], path + [rel]))

        return ret

    diffs = compare(i1.root, i2.root, [], args.format == "csv")

    if args.format == "csv":
        fields = ["entity", "scheme", "start", "end", "instant", "name", "a", "b"]
        fieldset = set(fields)

        for diff in diffs:
            for p in diff["path"]:
                if isinstance(p, Dimension):
                    if p.dimension.localname not in fieldset:
                        fields.append(p.dimension.localname)
                        fieldset.add(p.dimension.localname)

        writer = csv.DictWriter(sys.stdout, fields)
        writer.writeheader()

        for diff in diffs:
            row = {
                "name": diff["name"],
                "a": diff["a"],
                "b": diff["b"]
            }
            for p in diff["path"]:
                if isinstance(p, Entity):
                    row["entity"] = p.id
                if isinstance(p, Period):
                    row["start"] = str(p.start)
                    row["end"] = str(p.end)
                if isinstance(p, Instant):
                    row["instant"] = str(p.instant)
                if isinstance(p, Dimension):
                    row[p.dimension.localname] = p.value.localname
            writer.writerow(row)

    else:
        for diff in diffs:
            print("At:")

            for p in diff["path"]:
                if isinstance(p, Entity):
                    print("  Entity %s (%s)" % (p.id, p.scheme))
                elif isinstance(p, Period):
                    print("  Period %s - %s" % (p.start, p.end))
                elif isinstance(p, Instant):
                    print("  Instant %s" % p.instant)
                elif isinstance(p, Dimension):
                    print("  Dimension %s: %s" % (p.dimension, p.value))
            print("Fact %s:" % diff["name"])
            print("  A: %s" % diff["a"])
            print("  B: %s" % diff["b"])
            print()


if __name__ == '__main__':
    print("This module provides CLI entry points. Use the installed commands instead.")
    sys.exit(1)
