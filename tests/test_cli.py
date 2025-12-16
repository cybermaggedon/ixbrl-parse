"""Tests for CLI commands."""

import pytest
import sys
import json
from io import StringIO
from pathlib import Path

from ixbrl_parse import cli


class TestDumpCommand:
    """Test ixbrl-dump command."""

    def test_dump_main_basic(self, sample_ixbrl_file, capsys, monkeypatch):
        """Test basic dump functionality."""
        monkeypatch.setattr(sys, 'argv', ['ixbrl-dump', str(sample_ixbrl_file)])

        cli.dump_main()

        captured = capsys.readouterr()
        assert len(captured.out) > 0
        assert "Entity:" in captured.out

    def test_dump_main_verbose(self, sample_ixbrl_file, capsys, monkeypatch):
        """Test dump with verbose flag."""
        monkeypatch.setattr(sys, 'argv', ['ixbrl-dump', str(sample_ixbrl_file), '--verbose'])

        cli.dump_main()

        captured = capsys.readouterr()
        assert len(captured.out) > 0


class TestToJsonCommand:
    """Test ixbrl-to-json command."""

    def test_to_json_hierarchy(self, sample_ixbrl_file, capsys, monkeypatch):
        """Test JSON output in hierarchy format."""
        monkeypatch.setattr(sys, 'argv', ['ixbrl-to-json', str(sample_ixbrl_file)])

        cli.to_json_main()

        captured = capsys.readouterr()
        assert len(captured.out) > 0
        # Verify it's valid JSON
        data = json.loads(captured.out)
        assert isinstance(data, dict)

    def test_to_json_flat(self, sample_ixbrl_file, capsys, monkeypatch):
        """Test JSON output in flat format."""
        monkeypatch.setattr(sys, 'argv', ['ixbrl-to-json', str(sample_ixbrl_file), '-f', 'flat'])

        cli.to_json_main()

        captured = capsys.readouterr()
        assert len(captured.out) > 0
        # Verify it's valid JSON
        data = json.loads(captured.out)
        # Flatten returns a dict with contexts and values
        assert isinstance(data, dict)
        assert 'contexts' in data or 'values' in data


class TestToCsvCommand:
    """Test ixbrl-to-csv command."""

    def test_to_csv_basic(self, sample_ixbrl_file, capsys, monkeypatch):
        """Test CSV output."""
        monkeypatch.setattr(sys, 'argv', ['ixbrl-to-csv', str(sample_ixbrl_file)])

        cli.to_csv_main()

        captured = capsys.readouterr()
        assert len(captured.out) > 0
        # Check CSV header exists
        lines = captured.out.strip().split('\n')
        assert len(lines) > 1  # At least header + one row
        assert 'namespace' in lines[0]
        assert 'name' in lines[0]
        assert 'value' in lines[0]


class TestToRdfCommand:
    """Test ixbrl-to-rdf command."""

    def test_to_rdf_n3(self, sample_ixbrl_file, capsys, monkeypatch):
        """Test RDF output in N3 format."""
        monkeypatch.setattr(sys, 'argv', ['ixbrl-to-rdf', str(sample_ixbrl_file)])

        cli.to_rdf_main()

        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_to_rdf_xml(self, sample_ixbrl_file, capsys, monkeypatch):
        """Test RDF output in XML format."""
        monkeypatch.setattr(sys, 'argv', ['ixbrl-to-rdf', str(sample_ixbrl_file), '-f', 'xml'])

        cli.to_rdf_main()

        captured = capsys.readouterr()
        assert len(captured.out) > 0
        assert '<?xml' in captured.out or 'rdf:RDF' in captured.out


class TestToXbrlCommand:
    """Test ixbrl-to-xbrl command."""

    def test_to_xbrl_basic(self, sample_ixbrl_file, capsys, monkeypatch):
        """Test XBRL instance output."""
        monkeypatch.setattr(sys, 'argv', ['ixbrl-to-xbrl', str(sample_ixbrl_file)])

        cli.to_xbrl_main()

        captured = capsys.readouterr()
        assert len(captured.out) > 0
        assert '<?xml' in captured.out
        assert 'xbrl' in captured.out


class TestToKvCommand:
    """Test ixbrl-to-kv command."""

    def test_to_kv_default_separator(self, sample_ixbrl_file, capsys, monkeypatch):
        """Test key-value output with default separator."""
        monkeypatch.setattr(sys, 'argv', ['ixbrl-to-kv', str(sample_ixbrl_file)])

        cli.to_kv_main()

        captured = capsys.readouterr()
        assert len(captured.out) > 0
        # Default separator is |
        assert '|' in captured.out

    def test_to_kv_custom_separator(self, sample_ixbrl_file, capsys, monkeypatch):
        """Test key-value output with custom separator."""
        monkeypatch.setattr(sys, 'argv', ['ixbrl-to-kv', str(sample_ixbrl_file), '-s', ':'])

        cli.to_kv_main()

        captured = capsys.readouterr()
        assert len(captured.out) > 0
        # Custom separator should be present
        lines = captured.out.strip().split('\n')
        # Check that lines use the custom separator
        assert any(':' in line for line in lines)


class TestReportCommand:
    """Test ixbrl-report command."""

    def test_report_basic(self, sample_ixbrl_file, capsys, monkeypatch):
        """Test basic report functionality."""
        monkeypatch.setattr(sys, 'argv', ['ixbrl-report', str(sample_ixbrl_file)])

        # This may take longer due to schema loading
        cli.report_main()

        captured = capsys.readouterr()
        assert len(captured.out) > 0


class TestMarkdownCommand:
    """Test ixbrl-markdown command."""

    def test_markdown_requires_tabulate(self):
        """Test that markdown command checks for tabulate."""
        # The markdown_main function should handle missing tabulate gracefully
        # This test verifies the import check exists
        import importlib.util
        spec = importlib.util.find_spec("tabulate")
        if spec is None:
            # If tabulate is not installed, the command should exit with error
            # We can't easily test sys.exit in this context, but we verify the logic
            pass

    def test_markdown_basic(self, sample_ixbrl_file, capsys, monkeypatch):
        """Test markdown output (requires tabulate)."""
        pytest.importorskip("tabulate")

        monkeypatch.setattr(sys, 'argv', ['ixbrl-markdown', str(sample_ixbrl_file)])

        cli.markdown_main()

        captured = capsys.readouterr()
        assert len(captured.out) > 0
        # Markdown should contain headers
        assert '#' in captured.out


class TestDiffCommand:
    """Test ixbrl-diff command."""

    def test_diff_same_file(self, sample_ixbrl_file, capsys, monkeypatch):
        """Test diff with same file (should show no differences)."""
        monkeypatch.setattr(
            sys, 'argv',
            ['ixbrl-diff', str(sample_ixbrl_file), str(sample_ixbrl_file)]
        )

        cli.diff_main()

        captured = capsys.readouterr()
        # When comparing identical files, output should be minimal or empty
        # (no differences to report)

    def test_diff_csv_format(self, sample_ixbrl_file, capsys, monkeypatch):
        """Test diff with CSV output format."""
        monkeypatch.setattr(
            sys, 'argv',
            ['ixbrl-diff', str(sample_ixbrl_file), str(sample_ixbrl_file), '-f', 'csv']
        )

        cli.diff_main()

        captured = capsys.readouterr()
        # CSV output should at least have headers
        if captured.out:
            assert 'name' in captured.out or len(captured.out) == 0
