"""Tests for core iXBRL parsing functionality."""

import pytest
from lxml import etree as ET

from ixbrl_parse.ixbrl import (
    parse, Entity, Period, Instant, Dimension,
    Measure, Divide, NoUnit, Context
)


class TestParsing:
    """Test basic parsing functionality."""

    def test_parse_returns_ixbrl_object(self, sample_ixbrl_tree):
        """Test that parse() returns an Ixbrl object."""
        result = parse(sample_ixbrl_tree)
        assert result is not None
        assert hasattr(result, 'root')
        assert hasattr(result, 'contexts')
        assert hasattr(result, 'values')

    def test_parse_extracts_contexts(self, sample_ixbrl_tree):
        """Test that contexts are extracted from the document."""
        result = parse(sample_ixbrl_tree)
        assert len(result.contexts) > 0
        # Check that contexts have expected attributes
        for ctx in result.contexts.values():
            assert isinstance(ctx, Context)

    def test_parse_extracts_values(self, sample_ixbrl_tree):
        """Test that values are extracted from the document."""
        result = parse(sample_ixbrl_tree)
        assert len(result.values) > 0

    def test_parse_extracts_units(self, sample_ixbrl_tree):
        """Test that units are extracted from the document."""
        result = parse(sample_ixbrl_tree)
        assert len(result.units) > 0


class TestUnits:
    """Test unit classes."""

    def test_no_unit(self):
        """Test NoUnit class."""
        unit = NoUnit()
        assert str(unit) == ""
        assert not bool(unit)

    def test_measure_unit(self):
        """Test Measure unit class."""
        qname = ET.QName("http://www.xbrl.org/2003/iso4217", "GBP")
        measure = Measure(qname)
        assert str(measure) == "GBP"
        assert bool(measure)

    def test_divide_unit(self):
        """Test Divide unit class."""
        qname1 = ET.QName("http://www.xbrl.org/2003/iso4217", "GBP")
        qname2 = ET.QName("http://example.com", "share")
        num = Measure(qname1)
        den = Measure(qname2)
        divide = Divide(num, den)
        assert str(divide) == "GBP/share"
        assert bool(divide)


class TestContext:
    """Test Context class."""

    def test_context_creation(self):
        """Test creating a context."""
        ctx = Context()
        assert ctx.entity is None
        assert ctx.period is None
        assert ctx.instant is None
        assert ctx.values == {}
        assert ctx.children == {}

    def test_context_with_entity(self):
        """Test context with entity."""
        entity = Entity("12345", "http://example.com")
        ctx = Context()
        ctx.entity = entity
        assert ctx.entity == entity
        assert ctx.entity.id == "12345"
        assert ctx.entity.scheme == "http://example.com"


class TestOutputFormats:
    """Test various output format methods."""

    def test_flatten(self, sample_ixbrl_tree):
        """Test flatten() output format."""
        result = parse(sample_ixbrl_tree)
        flattened = result.flatten()
        assert isinstance(flattened, dict)
        assert 'contexts' in flattened
        assert 'values' in flattened

    def test_to_dict(self, sample_ixbrl_tree):
        """Test to_dict() output format."""
        result = parse(sample_ixbrl_tree)
        dict_output = result.to_dict()
        assert isinstance(dict_output, dict)

    def test_get_triples(self, sample_ixbrl_tree):
        """Test get_triples() RDF output."""
        result = parse(sample_ixbrl_tree)
        triples = result.get_triples()
        assert isinstance(triples, list)
        assert len(triples) > 0
        # Each triple should have 3 elements
        for triple in triples:
            assert len(triple) == 3


class TestRelationships:
    """Test relationship classes."""

    def test_entity_representation(self):
        """Test Entity class."""
        entity = Entity("ABC123", "http://companies.example.com")
        assert entity.id == "ABC123"
        assert entity.scheme == "http://companies.example.com"
        # Test that it's hashable (for use as dict key)
        test_dict = {entity: "test"}
        assert test_dict[entity] == "test"

    def test_period_representation(self):
        """Test Period class."""
        period = Period("2020-01-01", "2020-12-31")
        assert period.start == "2020-01-01"
        assert period.end == "2020-12-31"

    def test_instant_representation(self):
        """Test Instant class."""
        instant = Instant("2020-12-31")
        assert instant.instant == "2020-12-31"

    def test_dimension_representation(self):
        """Test Dimension class."""
        dim_name = ET.QName("http://example.com", "Sector")
        dim_value = ET.QName("http://example.com", "Technology")
        dimension = Dimension(dim_name, dim_value)
        assert dimension.dimension == dim_name
        assert dimension.value == dim_value
