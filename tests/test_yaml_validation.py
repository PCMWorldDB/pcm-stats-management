import os
import pytest
import shutil
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch
from io import StringIO
import sys

# Add the parent directory to Python path for imports
test_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(test_dir)
sys.path.insert(0, project_root)

from src.pcm_cli import validate_yaml_files
from src.utils import commons


class TestYamlValidation:
    """Test suite for the validate_yaml_files CLI function."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        # Create temporary directory for test data
        self.test_data_dir = tempfile.mkdtemp(prefix="pcm_validation_test_")
        self.original_data_path = commons.DATA_PATH
        self.original_cwd = os.getcwd()
        
        # Patch the DATA_PATH to use our test directory
        commons.DATA_PATH = self.test_data_dir
        
        # Change to test directory
        os.chdir(self.test_data_dir)
        
    def teardown_method(self):
        """Clean up test environment after each test."""
        # Restore original settings
        commons.DATA_PATH = self.original_data_path
        os.chdir(self.original_cwd)
        
        # Remove test directory
        if os.path.exists(self.test_data_dir):
            shutil.rmtree(self.test_data_dir)
    
    def create_test_namespace(self, namespace, changes=None, stats=None):
        """Create a test namespace with optional changes and stats."""
        namespace_dir = os.path.join(self.test_data_dir, namespace)
        changes_dir = os.path.join(namespace_dir, 'changes')
        os.makedirs(changes_dir, exist_ok=True)
        
        # Create stats file if provided
        if stats is not None:
            stats_file = os.path.join(namespace_dir, 'stats.yaml')
            with open(stats_file, 'w') as f:
                if isinstance(stats, str):
                    f.write(stats)  # Write raw string for invalid YAML tests
                else:
                    yaml.dump(stats, f, default_flow_style=False, sort_keys=False)
        
        # Create change files if provided
        if changes:
            for change_name, change_data in changes.items():
                change_dir = os.path.join(changes_dir, change_name)
                os.makedirs(change_dir, exist_ok=True)
                change_file = os.path.join(change_dir, 'change.yaml')
                with open(change_file, 'w') as f:
                    if isinstance(change_data, str):
                        f.write(change_data)  # Write raw string for invalid YAML tests
                    else:
                        yaml.dump(change_data, f, default_flow_style=False, sort_keys=False)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_validate_yaml_files_success(self, mock_stdout):
        """Test successful validation of valid YAML files."""
        # Create valid test data
        valid_changes = {
            "valid-change": {
                "author": "Test Author",
                "date": "2025-08-11",
                "stats": [
                    {
                        "pcm_id": "12345",
                        "name": "Test Cyclist",
                        "fla": 75,
                        "mo": 65
                    }
                ]
            }
        }
        
        valid_stats = {
            "12345": {
                "name": "Test Cyclist",
                "fla": 70,
                "mo": 60
            }
        }
        
        self.create_test_namespace("valid_namespace", valid_changes, valid_stats)
        
        # Test validation
        result = validate_yaml_files()
        
        # Verify success
        assert result is True
        output = mock_stdout.getvalue()
        assert "🎉 All YAML files passed validation!" in output
        assert "✅" in output  # Should have success checkmarks
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_validate_yaml_files_invalid_syntax(self, mock_stdout):
        """Test validation with invalid YAML syntax."""
        # Create invalid YAML content
        invalid_change_yaml = "invalid: yaml: content: [\nbroken syntax"
        
        invalid_changes = {
            "invalid-syntax-change": invalid_change_yaml
        }
        
        self.create_test_namespace("invalid_syntax_namespace", invalid_changes, {})
        
        # Test validation
        result = validate_yaml_files()
        
        # Verify failure
        assert result is False
        output = mock_stdout.getvalue()
        assert "❌" in output  # Should have error markers
        assert "YAML syntax error" in output or "validation failed" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_validate_yaml_files_missing_required_fields_change(self, mock_stdout):
        """Test validation with change file missing required fields."""
        # Create change file missing required fields
        invalid_changes = {
            "missing-fields-change": {
                "author": "Test Author",
                # Missing 'date' and 'stats' fields
            }
        }
        
        self.create_test_namespace("missing_fields_namespace", invalid_changes, {})
        
        # Test validation
        result = validate_yaml_files()
        
        # Verify failure
        assert result is False
        output = mock_stdout.getvalue()
        assert "❌" in output
        assert "Missing required fields" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_validate_yaml_files_missing_required_fields_stats(self, mock_stdout):
        """Test validation with stats file missing required fields."""
        # Create valid change but invalid stats
        valid_changes = {
            "valid-change": {
                "author": "Test Author",
                "date": "2025-08-11",
                "stats": [{"pcm_id": "12345", "name": "Test Cyclist"}]
            }
        }
        
        # Stats with missing required fields
        invalid_stats = {
            "12345": {
                # Missing 'name' field
                "fla": 70
            }
        }
        
        self.create_test_namespace("invalid_stats_namespace", valid_changes, invalid_stats)
        
        # Test validation
        result = validate_yaml_files()
        
        # Verify failure
        assert result is False
        output = mock_stdout.getvalue()
        assert "❌" in output
        assert "Missing required fields" in output or "validation failed" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_validate_yaml_files_empty_stats_list(self, mock_stdout):
        """Test validation with empty stats list in change file."""
        # Create change file with empty stats list
        invalid_changes = {
            "empty-stats-change": {
                "author": "Test Author",
                "date": "2025-08-11",
                "stats": []  # Empty list should be invalid
            }
        }
        
        self.create_test_namespace("empty_stats_namespace", invalid_changes, {})
        
        # Test validation
        result = validate_yaml_files()
        
        # Verify failure
        assert result is False
        output = mock_stdout.getvalue()
        assert "❌" in output
        assert "stats cannot be empty" in output or "validation failed" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_validate_yaml_files_invalid_cyclist_id(self, mock_stdout):
        """Test validation with non-numeric cyclist ID in stats file."""
        # Create stats with invalid cyclist ID
        invalid_stats = {
            "not_a_number": {  # Invalid cyclist ID
                "name": "Test Cyclist",
                "fla": 70
            }
        }
        
        self.create_test_namespace("invalid_id_namespace", {}, invalid_stats)
        
        # Test validation
        result = validate_yaml_files()
        
        # Verify failure
        assert result is False
        output = mock_stdout.getvalue()
        assert "❌" in output
        assert "must be numeric" in output or "validation failed" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_validate_yaml_files_stats_not_list(self, mock_stdout):
        """Test validation with stats field that is not a list."""
        # Create change file with stats as dict instead of list
        invalid_changes = {
            "stats-not-list-change": {
                "author": "Test Author",
                "date": "2025-08-11",
                "stats": {"pcm_id": "12345", "name": "Test"}  # Should be list, not dict
            }
        }
        
        self.create_test_namespace("stats_not_list_namespace", invalid_changes, {})
        
        # Test validation
        result = validate_yaml_files()
        
        # Verify failure
        assert result is False
        output = mock_stdout.getvalue()
        assert "❌" in output
        assert "stats must be a list" in output or "validation failed" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_validate_yaml_files_multiple_namespaces_mixed(self, mock_stdout):
        """Test validation with multiple namespaces, some valid and some invalid."""
        # Create valid namespace
        valid_changes = {
            "valid-change": {
                "author": "Test Author",
                "date": "2025-08-11",
                "stats": [{"pcm_id": "12345", "name": "Test Cyclist"}]
            }
        }
        valid_stats = {"12345": {"name": "Test Cyclist"}}
        self.create_test_namespace("valid_namespace", valid_changes, valid_stats)
        
        # Create invalid namespace
        invalid_changes = {
            "invalid-change": {
                "author": "Test Author",
                # Missing required fields
            }
        }
        self.create_test_namespace("invalid_namespace", invalid_changes, {})
        
        # Test validation
        result = validate_yaml_files()
        
        # Verify failure due to invalid namespace
        assert result is False
        output = mock_stdout.getvalue()
        assert "❌" in output
        assert "validation failed" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_validate_yaml_files_no_files_to_validate(self, mock_stdout):
        """Test validation when no YAML files exist."""
        # Create empty namespace directory structure
        namespace_dir = os.path.join(self.test_data_dir, "empty_namespace")
        changes_dir = os.path.join(namespace_dir, 'changes')
        os.makedirs(changes_dir, exist_ok=True)
        # Don't create any YAML files
        
        # Test validation
        result = validate_yaml_files()
        
        # Should succeed when no files to validate
        assert result is True
        output = mock_stdout.getvalue()
        assert "No change files found to validate" in output or "No stats files found to validate" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_validate_yaml_files_valid_stat_update_structure(self, mock_stdout):
        """Test validation with properly structured stat update entries."""
        # Create change with multiple stat updates
        valid_changes = {
            "multi-stat-change": {
                "author": "Test Author",
                "date": "2025-08-11",
                "stats": [
                    {
                        "pcm_id": "12345",
                        "name": "Cyclist One",
                        "fla": 75,
                        "mo": 65
                    },
                    {
                        "pcm_id": "67890",
                        "name": "Cyclist Two",
                        "tt": 80,
                        "spr": 70
                    }
                ]
            }
        }
        
        valid_stats = {
            "12345": {"name": "Cyclist One", "fla": 70},
            "67890": {"name": "Cyclist Two", "tt": 75}
        }
        
        self.create_test_namespace("multi_stat_namespace", valid_changes, valid_stats)
        
        # Test validation
        result = validate_yaml_files()
        
        # Verify success
        assert result is True
        output = mock_stdout.getvalue()
        assert "🎉 All YAML files passed validation!" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_validate_yaml_files_stat_entry_missing_fields(self, mock_stdout):
        """Test validation with stat entry missing required fields."""
        # Create change with stat entry missing pcm_id
        invalid_changes = {
            "missing-stat-fields-change": {
                "author": "Test Author",
                "date": "2025-08-11",
                "stats": [
                    {
                        # Missing "pcm_id" field
                        "name": "Test Cyclist",
                        "fla": 75
                    }
                ]
            }
        }
        
        self.create_test_namespace("missing_stat_fields_namespace", invalid_changes, {})
        
        # Test validation
        result = validate_yaml_files()
        
        # Verify failure
        assert result is False
        output = mock_stdout.getvalue()
        assert "❌" in output
        assert "missing required fields" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_validate_yaml_files_comprehensive_valid_data(self, mock_stdout):
        """Test validation with comprehensive valid data including all stat types."""
        # Create comprehensive valid test data
        comprehensive_changes = {
            "comprehensive-change": {
                "author": "Comprehensive Test Author",
                "date": "2025-08-11",
                "stats": [
                    {
                        "pcm_id": "12345",
                        "name": "Complete Cyclist",
                        "fla": 75, "mo": 65, "mm": 70, "dh": 80,
                        "cob": 60, "tt": 85, "prl": 55, "spr": 90,
                        "acc": 75, "end": 80, "res": 70, "rec": 85,
                        "hil": 78, "att": 82
                    }
                ]
            }
        }
        
        comprehensive_stats = {
            "12345": {
                "name": "Complete Cyclist",
                "fla": 70, "mo": 60, "mm": 65, "dh": 75,
                "cob": 55, "tt": 80, "prl": 50, "spr": 85,
                "acc": 70, "end": 75, "res": 65, "rec": 80,
                "hil": 73, "att": 77
            }
        }
        
        self.create_test_namespace("comprehensive_namespace", comprehensive_changes, comprehensive_stats)
        
        # Test validation
        result = validate_yaml_files()
        
        # Verify success
        assert result is True
        output = mock_stdout.getvalue()
        assert "🎉 All YAML files passed validation!" in output
        assert "✅" in output
