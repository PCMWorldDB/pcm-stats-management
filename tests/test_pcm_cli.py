#!/usr/bin/env python3
"""
Test suite for PCM CLI functionality.

This module tests the command-line interface functions for PCM stats management,
including the new automated change request processing commands.
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import patch, mock_open, MagicMock
from io import StringIO

# Add parent directory to path to import src modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from src import pcm_cli


class TestPCMCLI(unittest.TestCase):
    """Test cases for PCM CLI functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_issue_body = """### Change Name
Tour of Panama

### Date
2025-08-06

### Author
Test Author

### Race URL
https://firstcycling.com/race.php?r=12345&pcm=1

### Description
Adding cyclists from Tour of Panama

### Namespace
procyclingstats"""

        self.expected_form_data = {
            'change_name': 'Tour of Panama',
            'date': '2025-08-06',
            'author': 'Test Author',
            'race_url': 'https://firstcycling.com/race.php?r=12345&pcm=1',
            'description': 'Adding cyclists from Tour of Panama',
            'namespace': 'procyclingstats',
            'branch_name': 'change/tour-of-panama'
        }

    @patch('src.pcm_cli.model_api.process_all_namespaces')
    def test_process_changes(self, mock_process):
        """Test process_changes CLI function."""
        # Mock successful processing
        mock_process.return_value = {
            'total_changes': 2,
            'overall_success': True,
            'processed_namespaces': 1
        }
        
        # Call function
        result = pcm_cli.process_changes()
        
        # Assertions
        assert result is True
        mock_process.assert_called_once()

    @patch('src.pcm_cli.model_api.process_all_namespaces')
    def test_process_changes_no_new_changes(self, mock_process):
        """Test process_changes with no new changes."""
        # Mock no changes found
        mock_process.return_value = {
            'total_changes': 0,
            'overall_success': True,
            'processed_namespaces': 1
        }
        
        # Call function
        result = pcm_cli.process_changes()
        
        # Assertions
        assert result is True
        mock_process.assert_called_once()

    @patch('src.pcm_cli.model_api.process_all_namespaces')
    def test_process_changes_failure(self, mock_process):
        """Test process_changes with processing failure."""
        # Mock processing failure
        mock_process.side_effect = Exception("Processing failed")
        
        # Call function
        result = pcm_cli.process_changes()
        
        # Assertions
        assert result is False
        mock_process.assert_called_once()

    @patch('src.pcm_cli.model_api.validate_yaml_files')
    def test_validate_yaml_files(self, mock_validate):
        """Test validate_yaml_files CLI function."""
        # Mock successful validation
        mock_validate.return_value = True
        
        # Call function
        result = pcm_cli.validate_yaml_files()
        
        # Assertions
        assert result is True
        mock_validate.assert_called_once()

    @patch('src.pcm_cli.model_api.import_cyclists_from_db')
    def test_import_from_db(self, mock_import):
        """Test import_from_db CLI function."""
        # Mock successful import
        mock_import.return_value = True
        
        # Call function
        result = pcm_cli.import_from_db('test_namespace', '/path/to/db.sqlite')
        
        # Assertions
        assert result is True
        mock_import.assert_called_once_with('test_namespace', '/path/to/db.sqlite')

    @patch('src.pcm_cli.model_api.process_uat_changes')
    def test_process_uat(self, mock_process):
        """Test process_uat CLI function."""
        # Mock successful UAT processing
        mock_process.return_value = {
            'total_changes_executed': 3,
            'overall_success': True,
            'processed_namespaces': 1
        }
        
        # Call function
        result = pcm_cli.process_uat()
        
        # Assertions
        assert result is True
        mock_process.assert_called_once()

    @patch.dict('os.environ', {'GITHUB_OUTPUT': '/tmp/github_output'})
    @patch('builtins.open', new_callable=mock_open)
    @patch('src.pcm_cli.model_api.parse_github_issue_form')
    def test_parse_github_issue_success(self, mock_parse, mock_file):
        """Test parse_github_issue CLI function with GitHub Actions output."""
        # Mock successful parsing
        mock_parse.return_value = self.expected_form_data
        
        # Call function
        result = pcm_cli.parse_github_issue(self.sample_issue_body)
        
        # Assertions
        assert result is True
        mock_parse.assert_called_once_with(self.sample_issue_body, None)
        
        # Check that GitHub output file was written
        mock_file.assert_called_with('/tmp/github_output', 'a')
        handle = mock_file()
        
        # Verify all form data was written to output file
        written_lines = [call.args[0] for call in handle.write.call_args_list]
        expected_lines = [f"{key}={value}\n" for key, value in self.expected_form_data.items()]
        
        for expected_line in expected_lines:
            assert expected_line in written_lines

    @patch('src.pcm_cli.model_api.parse_github_issue_form')
    def test_parse_github_issue_no_github_output(self, mock_parse):
        """Test parse_github_issue without GitHub Actions environment."""
        # Mock successful parsing
        mock_parse.return_value = self.expected_form_data
        
        # Call function (no GITHUB_OUTPUT env var)
        result = pcm_cli.parse_github_issue(self.sample_issue_body)
        
        # Assertions
        assert result is True
        mock_parse.assert_called_once_with(self.sample_issue_body, None)

    @patch('src.pcm_cli.model_api.parse_github_issue_form')
    def test_parse_github_issue_failure(self, mock_parse):
        """Test parse_github_issue with parsing failure."""
        # Mock parsing failure
        mock_parse.side_effect = Exception("Parsing failed")
        
        # Call function
        result = pcm_cli.parse_github_issue(self.sample_issue_body)
        
        # Assertions
        assert result is False
        mock_parse.assert_called_once_with(self.sample_issue_body, None)

    @patch.dict('os.environ', {'GITHUB_OUTPUT': '/tmp/github_output'})
    @patch('builtins.open', new_callable=mock_open)
    @patch('src.pcm_cli.model_api.parse_github_issue_form')
    @patch('src.pcm_cli.model_api.process_automated_change_request')
    def test_process_automated_change_success(self, mock_process, mock_parse, mock_file):
        """Test process_automated_change CLI function with successful processing."""
        # Mock successful parsing and processing
        mock_parse.return_value = self.expected_form_data
        mock_result = {
            'success': True,
            'cyclists_found': 5,
            'change_file_path': '/test/changes/tour-of-panama/change.yaml',
            'error': None
        }
        mock_process.return_value = mock_result
        
        # Call function
        result = pcm_cli.process_automated_change(self.sample_issue_body)
        
        # Assertions
        assert result is True
        mock_parse.assert_called_once_with(self.sample_issue_body, None)
        mock_process.assert_called_once_with(self.sample_issue_body, author_override=None, issue_title=None)
        
        # Check that GitHub output file was written
        mock_file.assert_called_with('/tmp/github_output', 'a')
        handle = mock_file()
        
        # Verify all form data and processing results were written
        written_lines = [call.args[0] for call in handle.write.call_args_list]
        
        # Should include form data
        expected_form_lines = [f"{key}={value}\n" for key, value in self.expected_form_data.items()]
        for expected_line in expected_form_lines:
            assert expected_line in written_lines
        
        # Should include processing results
        expected_result_lines = [
            'success=true\n',
            'cyclists_found=5\n',
            'change_file_path=/test/changes/tour-of-panama/change.yaml\n'
        ]
        for expected_line in expected_result_lines:
            assert expected_line in written_lines

    @patch.dict('os.environ', {'GITHUB_OUTPUT': '/tmp/github_output'})
    @patch('builtins.open', new_callable=mock_open)
    @patch('src.pcm_cli.model_api.parse_github_issue_form')
    @patch('src.pcm_cli.model_api.process_automated_change_request')
    def test_process_automated_change_failure(self, mock_process, mock_parse, mock_file):
        """Test process_automated_change CLI function with processing failure."""
        # Mock parsing success but processing failure
        mock_parse.return_value = self.expected_form_data
        mock_result = {
            'success': False,
            'cyclists_found': 0,
            'change_file_path': None,
            'error': 'Invalid URL format'
        }
        mock_process.return_value = mock_result
        
        # Call function
        result = pcm_cli.process_automated_change(self.sample_issue_body)
        
        # Assertions
        assert result is False
        mock_parse.assert_called_once_with(self.sample_issue_body, None)
        mock_process.assert_called_once_with(self.sample_issue_body, author_override=None, issue_title=None)
        
        # Check that GitHub output file was written
        mock_file.assert_called_with('/tmp/github_output', 'a')
        handle = mock_file()
        
        # Verify form data and error were written to output
        written_lines = [call.args[0] for call in handle.write.call_args_list]
        
        # Should include form data
        expected_form_lines = [f"{key}={value}\n" for key, value in self.expected_form_data.items()]
        for expected_line in expected_form_lines:
            assert expected_line in written_lines
        
        # Should include processing results with error
        expected_result_lines = [
            'success=false\n',
            'cyclists_found=0\n',
            'error=Invalid URL format\n'
        ]
        for expected_line in expected_result_lines:
            assert expected_line in written_lines

    @patch.dict('os.environ', {'GITHUB_OUTPUT': '/tmp/github_output'})
    @patch('builtins.open', new_callable=mock_open)
    @patch('src.pcm_cli.model_api.parse_github_issue_form')
    @patch('src.pcm_cli.model_api.process_automated_change_request')
    def test_process_automated_change_with_github_actor(self, mock_process, mock_parse, mock_file):
        """Test process_automated_change CLI function with GitHub actor override."""
        # Mock form data without author
        form_data_no_author = self.expected_form_data.copy()
        form_data_no_author['author'] = ''  # Empty author
        mock_parse.return_value = form_data_no_author
        
        mock_result = {
            'success': True,
            'cyclists_found': 3,
            'change_file_path': '/test/changes/tour-of-panama/change.yaml',
            'error': None
        }
        mock_process.return_value = mock_result
        
        # Call function with GitHub actor
        result = pcm_cli.process_automated_change(self.sample_issue_body, "github_user123")
        
        # Assertions
        assert result is True
        mock_parse.assert_called_once_with(self.sample_issue_body, None)
        mock_process.assert_called_once_with(self.sample_issue_body, author_override="github_user123", issue_title=None)
        
        # Check that GitHub output file was written
        mock_file.assert_called_with('/tmp/github_output', 'a')
        handle = mock_file()
        
        # Verify author was overridden in output
        written_lines = [call.args[0] for call in handle.write.call_args_list]
        assert 'author=github_user123\n' in written_lines

    @patch.dict('os.environ', {'GITHUB_OUTPUT': '/tmp/github_output'})
    @patch('builtins.open', new_callable=mock_open)
    @patch('src.pcm_cli.model_api.parse_github_issue_form')
    @patch('src.pcm_cli.model_api.process_automated_change_request')
    def test_process_automated_change_with_issue_title(self, mock_process, mock_parse, mock_file):
        """Test process_automated_change CLI function with issue title extraction."""
        # Mock form data with change_name extracted from title
        form_data_with_title = self.expected_form_data.copy()
        form_data_with_title['change_name'] = 'Tour de France Stage 1'
        form_data_with_title['branch_name'] = 'change/2025-08-06-tour-de-france-stage-1'
        mock_parse.return_value = form_data_with_title
        
        mock_result = {
            'success': True,
            'cyclists_found': 3,
            'change_file_path': '/test/changes/tour-de-france-stage-1/change.yaml',
            'error': None
        }
        mock_process.return_value = mock_result
        
        # Call function with issue title
        issue_title = "[STATS CHANGE] Tour de France Stage 1"
        result = pcm_cli.process_automated_change(self.sample_issue_body, "github_user123", issue_title)
        
        # Assertions
        assert result is True
        mock_parse.assert_called_once_with(self.sample_issue_body, issue_title)
        mock_process.assert_called_once_with(self.sample_issue_body, author_override="github_user123", issue_title=issue_title)
        
        # Check that GitHub output file was written
        mock_file.assert_called_with('/tmp/github_output', 'a')
        handle = mock_file()
        
        # Verify change_name from title was used in output
        written_lines = [call.args[0] for call in handle.write.call_args_list]
        assert 'change_name=Tour de France Stage 1\n' in written_lines
        assert 'branch_name=change/2025-08-06-tour-de-france-stage-1\n' in written_lines

    @patch('src.pcm_cli.model_api.parse_github_issue_form')
    @patch('src.pcm_cli.model_api.process_automated_change_request')
    def test_process_automated_change_exception(self, mock_process, mock_parse):
        """Test process_automated_change with exception handling."""
        # Mock exception during parsing
        mock_parse.side_effect = Exception("Network error")
        
        # Call function
        result = pcm_cli.process_automated_change(self.sample_issue_body)
        
        # Assertions
        assert result is False
        mock_parse.assert_called_once_with(self.sample_issue_body, None)
        # process should not be called if parse fails
        mock_process.assert_not_called()

    @patch('sys.argv', ['pcm_cli.py', 'help'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_help_command(self, mock_stdout):
        """Test main function with help command."""
        # Call main
        result = pcm_cli.main()
        
        # Assertions
        assert result == 0
        output = mock_stdout.getvalue()
        assert 'PCM Stats Management CLI Tool' in output
        assert 'parse-github-issue' in output
        assert 'process-automated-change' in output

    @patch('sys.argv', ['pcm_cli.py', 'parse-github-issue', 'test_issue_body'])
    @patch('src.pcm_cli.parse_github_issue')
    def test_main_parse_github_issue(self, mock_parse):
        """Test main function with parse-github-issue command."""
        # Mock successful parsing
        mock_parse.return_value = True
        
        # Call main
        result = pcm_cli.main()
        
        # Assertions
        assert result == 0
        mock_parse.assert_called_once_with('test_issue_body', None, None)

    @patch('sys.argv', ['pcm_cli.py', 'parse-github-issue'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_parse_github_issue_missing_args(self, mock_stdout):
        """Test main function with parse-github-issue command missing arguments."""
        # Call main
        result = pcm_cli.main()
        
        # Assertions
        assert result == 1
        output = mock_stdout.getvalue()
        assert 'Error: parse-github-issue command requires issue body' in output

    @patch('sys.argv', ['pcm_cli.py', 'process-automated-change', 'test_issue_body'])
    @patch('src.pcm_cli.process_automated_change')
    def test_main_process_automated_change_success(self, mock_process):
        """Test main function with process-automated-change command success."""
        # Mock successful processing
        mock_process.return_value = True
        
        # Call main
        result = pcm_cli.main()
        
        # Assertions
        assert result == 0
        mock_process.assert_called_once_with('test_issue_body', None, None)

    @patch('sys.argv', ['pcm_cli.py', 'process-automated-change', 'test_issue_body'])
    @patch('src.pcm_cli.process_automated_change')
    def test_main_process_automated_change_failure(self, mock_process):
        """Test main function with process-automated-change command failure."""
        # Mock processing failure
        mock_process.return_value = False
        
        # Call main
        result = pcm_cli.main()
        
        # Assertions
        assert result == 1  # Should exit with error code
        mock_process.assert_called_once_with('test_issue_body', None, None)

    @patch('sys.argv', ['pcm_cli.py', 'process-automated-change'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_process_automated_change_missing_args(self, mock_stdout):
        """Test main function with process-automated-change command missing arguments."""
        # Call main
        result = pcm_cli.main()
        
        # Assertions
        assert result == 1
        output = mock_stdout.getvalue()
        assert 'Error: process-automated-change command requires issue body' in output


if __name__ == '__main__':
    unittest.main()
