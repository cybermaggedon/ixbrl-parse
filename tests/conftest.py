"""Pytest configuration and fixtures for ixbrl-parse tests."""

import pytest
from pathlib import Path
from lxml import etree as ET


@pytest.fixture
def test_data_dir():
    """Return the path to the test data directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def sample_ixbrl_file(test_data_dir):
    """Return the path to a sample iXBRL file."""
    return test_data_dir / "accts.html"


@pytest.fixture
def sample_ixbrl_tree(sample_ixbrl_file):
    """Return a parsed ElementTree from the sample iXBRL file."""
    return ET.parse(str(sample_ixbrl_file))
