# Test Suite for ixbrl-parse

This directory contains the pytest test suite for the ixbrl-parse project.

## Running Tests

### Install test dependencies

```bash
pip install -e ".[dev]"
```

Or install individually:

```bash
pip install pytest pytest-cov
```

### Run all tests

```bash
pytest
```

### Run with verbose output

```bash
pytest -v
```

### Run with coverage report

```bash
pytest --cov=ixbrl_parse --cov-report=term-missing
```

### Run specific test file

```bash
pytest tests/test_ixbrl.py
```

### Run specific test class or function

```bash
pytest tests/test_ixbrl.py::TestParsing::test_parse_returns_ixbrl_object
```

## Test Organization

- **test_ixbrl.py** - Tests for core iXBRL parsing functionality
  - Unit tests
  - Context handling
  - Output formats (flatten, to_dict, RDF triples)
  - Relationship classes

- **test_cli.py** - Tests for CLI commands
  - All 9 command-line tools
  - Argument parsing
  - Output format verification

- **test_value.py** - Tests for value types
  - String, Boolean, Date, Float values
  - MonthDay and Duration types
  - Unit handling

- **conftest.py** - Shared pytest fixtures
  - Sample iXBRL file fixtures
  - Test data directory access

## Test Coverage

Current coverage: **74%**

- ixbrl_parse/cli.py: 84%
- ixbrl_parse/ixbrl.py: 88%
- ixbrl_parse/value.py: 96%
- ixbrl_parse/schema.py: 83%
- ixbrl_parse/transform.py: 38% (complex transformations, less critical path)
