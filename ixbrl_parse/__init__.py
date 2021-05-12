"""iXBRL parsing

Example usage:

  from ixbrl_parse.ixbrl import parse
  from lxml import etree as ET

  tree = ET.parse("myfile.ixbrl")
  ix = parse(tree)

  for c in ix.contexts.values():
      for v in c.values.values():
          print(v)

"""
