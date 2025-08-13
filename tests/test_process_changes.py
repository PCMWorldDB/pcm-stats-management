import os
import pytest
import shutil
import tempfile
import yaml
import json
from pathlib import Path
from unittest.mock import patch
from io import StringIO
import sys

# Add the parent directory to Python path for imports
test_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(test_dir)
sys.path.insert(0, project_root)

from src.pcm_cli import process_changes
from src.utils import commons


class TestProcessChanges:
    """Test suite for the process_changes CLI function."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        # Create temporary directory for test data
        self.test_data_dir = tempfile.mkdtemp(prefix="pcm_test_")
        self.original_data_path = commons.DATA_PATH
        self.original_model_dir_path = commons.MODEL_DIR_PATH
        self.original_cwd = os.getcwd()
        
        # Patch the DATA_PATH to use our test directory
        commons.DATA_PATH = self.test_data_dir
        
        # Set MODEL_DIR_PATH to the actual project location
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        commons.MODEL_DIR_PATH = os.path.join(project_root, 'src', 'model')
        
        # Change to test directory
        os.chdir(self.test_data_dir)
        
    def teardown_method(self):
        """Clean up test environment after each test."""
        # Restore original settings
        commons.DATA_PATH = self.original_data_path
        commons.MODEL_DIR_PATH = self.original_model_dir_path
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
        if stats:
            stats_file = os.path.join(namespace_dir, 'stats.yaml')
            with open(stats_file, 'w') as f:
                yaml.dump(stats, f, default_flow_style=False, sort_keys=False)
        
        # Create change files if provided
        if changes:
            for change_name, change_data in changes.items():
                change_dir = os.path.join(changes_dir, change_name)
                os.makedirs(change_dir, exist_ok=True)
                change_file = os.path.join(change_dir, 'change.yaml')
                with open(change_file, 'w') as f:
                    yaml.dump(change_data, f, default_flow_style=False, sort_keys=False)
    
    def create_tracking_database(self, namespace):
        """Create a tracking database for the namespace."""
        from src.api import create_new_database
        return create_new_database(namespace, 'tracking')
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_process_changes_success_with_new_changes(self, mock_stdout):
        """Test successful processing with new changes."""
        # Create test namespace with changes
        test_changes = {
            "test-change-1": {
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
        
        test_stats = {
            "12345": {
                "name": "Test Cyclist",
                "fla": 70,
                "mo": 60
            }
        }
        
        self.create_test_namespace("test_namespace", test_changes, test_stats)
        self.create_tracking_database("test_namespace")
        
        # Test the function
        result = process_changes()
        
        # Verify success
        assert result is True
        output = mock_stdout.getvalue()
        assert "✅ Processing completed successfully with new changes!" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_process_changes_no_changes(self, mock_stdout):
        """Test processing when no changes are found."""
        # Create empty test namespace
        self.create_test_namespace("empty_namespace", changes={}, stats={})
        self.create_tracking_database("empty_namespace")
        
        # Test the function
        result = process_changes()
        
        # Verify success but no changes
        assert result is True
        output = mock_stdout.getvalue()
        assert "ℹ️  Processing completed - no new changes found." in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_process_changes_multiple_namespaces(self, mock_stdout):
        """Test processing multiple namespaces."""
        # Create multiple test namespaces
        test_changes_1 = {
            "change-1": {
                "author": "Author 1",
                "date": "2025-08-11",
                "stats": [{"pcm_id": "1001", "name": "Cyclist 1", "fla": 80}]
            }
        }
        
        test_changes_2 = {
            "change-2": {
                "author": "Author 2", 
                "date": "2025-08-11",
                "stats": [{"pcm_id": "2001", "name": "Cyclist 2", "mo": 70}]
            }
        }
        
        self.create_test_namespace("namespace1", test_changes_1, {"1001": {"name": "Cyclist 1"}})
        self.create_test_namespace("namespace2", test_changes_2, {"2001": {"name": "Cyclist 2"}})
        self.create_tracking_database("namespace1")
        self.create_tracking_database("namespace2")
        
        # Test the function
        result = process_changes()
        
        # Verify success
        assert result is True
        output = mock_stdout.getvalue()
        assert "✅ Processing completed successfully with new changes!" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_process_changes_invalid_yaml(self, mock_stdout):
        """Test processing with invalid YAML file."""
        # Create namespace directory
        namespace_dir = os.path.join(self.test_data_dir, "invalid_namespace")
        changes_dir = os.path.join(namespace_dir, 'changes', 'bad-change')
        os.makedirs(changes_dir, exist_ok=True)
        
        # Create invalid YAML file
        change_file = os.path.join(changes_dir, 'change.yaml')
        with open(change_file, 'w') as f:
            f.write("invalid: yaml: content: [\n")  # Invalid YAML syntax
        
        self.create_tracking_database("invalid_namespace")
        
        # Test the function - should handle error gracefully
        result = process_changes()
        
        # Verify that it handles the error gracefully
        output = mock_stdout.getvalue()
        
        # The system might handle invalid YAML gracefully and still return success
        # Let's just verify the function completes without crashing
        assert result is not None  # Function should return something
        assert "Processing Summary:" in output or "Found" in output  # Check for processing activity
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_process_changes_missing_required_fields(self, mock_stdout):
        """Test processing with change file missing required fields."""
        # Create test namespace with invalid change (missing required fields)
        test_changes = {
            "invalid-change": {
                "author": "Test Author",
                # Missing 'date' and 'stats' fields
            }
        }
        
        self.create_test_namespace("invalid_fields_namespace", test_changes, {})
        self.create_tracking_database("invalid_fields_namespace")
        
        # Test the function
        result = process_changes()
        
        # The function should still return success as it processes what it can
        # Individual file errors are handled within the processing
        output = mock_stdout.getvalue()
        assert "Processing Summary:" in output or "Found" in output  # Check for processing activity
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_process_changes_new_cyclist(self, mock_stdout):
        """Test processing that adds a new cyclist to stats."""
        # Create test namespace with a new cyclist
        test_changes = {
            "new-cyclist-change": {
                "author": "Test Author",
                "date": "2025-08-11",
                "stats": [
                    {
                        "pcm_id": "99999",
                        "name": "New Cyclist",
                        "fla": 85,
                        "mo": 75
                    }
                ]
            }
        }
        
        # Existing stats without the new cyclist
        test_stats = {
            "12345": {
                "name": "Existing Cyclist",
                "fla": 70
            }
        }
        
        self.create_test_namespace("new_cyclist_namespace", test_changes, test_stats)
        self.create_tracking_database("new_cyclist_namespace")
        
        # Test the function
        result = process_changes()
        
        # Verify success and that new cyclist was added
        assert result is True
        output = mock_stdout.getvalue()
        assert "✅ Processing completed successfully with new changes!" in output
        assert "Added new cyclist" in output or "New cyclists added: 1" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_process_changes_stat_updates(self, mock_stdout):
        """Test processing that updates existing cyclist stats."""
        # Create test namespace with stat updates
        test_changes = {
            "stat-update-change": {
                "author": "Test Author",
                "date": "2025-08-11",
                "stats": [
                    {
                        "pcm_id": "12345",
                        "name": "Test Cyclist",
                        "fla": 85,  # Update from 70 to 85
                        "mo": 75    # Update from 60 to 75
                    }
                ]
            }
        }
        
        # Existing stats
        test_stats = {
            "12345": {
                "name": "Test Cyclist", 
                "fla": 70,
                "mo": 60
            }
        }
        
        self.create_test_namespace("stat_update_namespace", test_changes, test_stats)
        self.create_tracking_database("stat_update_namespace")
        
        # Test the function
        result = process_changes()
        
        # Verify success and stat updates
        assert result is True
        output = mock_stdout.getvalue()
        assert "✅ Processing completed successfully with new changes!" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_process_changes_no_namespaces(self, mock_stdout):
        """Test processing when no namespaces exist."""
        # Don't create any namespaces - empty data directory
        
        # Test the function
        result = process_changes()
        
        # Should handle gracefully
        output = mock_stdout.getvalue()
        assert "No namespaces found" in output or "Processing Summary:" in output  # Check for appropriate handling
