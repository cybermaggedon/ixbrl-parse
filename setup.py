import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ixbrl-parse",
    version="0.9.1",
    author="Cybermaggedon",
    author_email="mark@cyberapocalypse.co.uk",
    description="Parse iXBRL files, can present in RDF",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cybermaggedon/ixbrl-parse",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    download_url = "https://github.com/cybermaggedon/ixbrl-parse/archive/refs/tags/v0.9.1.tar.gz",
    install_requires=[
        "number_parser",
        "requests",
        "lxml"
    ],
    scripts=[
        "scripts/ixbrl-dump",
        "scripts/ixbrl-report",
        "scripts/ixbrl-to-rdf",
        "scripts/ixbrl-to-csv",
        "scripts/ixbrl-to-json",
        "scripts/ixbrl-to-xbrl",
        "scripts/ixbrl-to-kv",
        "scripts/ixbrl-diff"
    ]
)
