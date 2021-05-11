
# `ixbrl-parse`

## Introduction

- Python library code, parses iXBRL files.
- Script `ixbrl-to-csv` outputs iXBRL tagged data in a CSV format.
- Script `ixbrl-to-rdf` emits iXBRL tagged data in RDF.

## Development

There's a bunch of sample iXBRL files grabbed from various places in
the `ixbrl` directory: US 10-K and 10-Q filings, a few random things
from UK companies house, and a couple of sample ESEF filings.  This is the
data I've tested with.

Also, `accts.html` is a sample file created using
[`gnucash-ixbrl`](https://github.com/cybermaggedon/gnucash-ixbrl).

## Installation

```
pip3 install git+https://github.com/cybermaggedon/ixbrl-parse
```

## Usage

Parse iXBRL and output in RDF (default n3 format):
```
ixbrl-to-rdf -i accts.html
```

Parse iXBRL and output in RDF/XML:
```
ixbrl-to-rdf -i accts.html --format xml
```

Parse iXBRL and output in CSV:
```
ixbrl-to-csv -i accts.html
```

Dump iXBRL values:
```
ixbrl-dump -i accts.html
```

## API

The `ixbrl-to-csv` file is a good starting point if you want to see how
the API works.

FIXME: Document the API.
