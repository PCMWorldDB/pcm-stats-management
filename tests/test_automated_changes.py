import os
import pytest
import tempfile
import shutil
import yaml
from unittest.mock import patch, MagicMock, mock_open
from src.api import (
    parse_github_issue_form,
    fetch_firstcycling_html,
    parse_firstcycling_html,
    scrape_firstcycling_cyclists,
    create_automated_change_file,
    process_automated_change_request
)


class TestAutomatedChangeFunctions:
    """Test cases for automated change request functions."""
    
    def setup_method(self):
        """Set up test data for each test method."""
        # Sample GitHub issue form body
        self.sample_issue_body = '''
### Change Name
Tour of Panama - Stage 1 Results

### Date
2025-08-06

### Author
BenGe

### Race URL
https://firstcycling.com/race.php?r=32345&y=2025

### Description
Adding results from Stage 1 of the Tour of Panama. Great race with strong competition.

### Namespace
procyclingstats
'''
        
        # Sample HTML content for testing parsing
        self.sample_html = '''<!DOCTYPE html>
<html>
<head><title>Test Race</title></head>
<body>
<table>
    <tr><th>Position</th><th>Rider</th><th>PCM</th></tr>
    <tr>
        <td>1</td>
        <td><a href="rider.php?r=12345&y=2025" title="John Doe">DOE John</a></td>
        <td>85</td>
    </tr>
    <tr>
        <td>2</td>
        <td><a href="rider.php?r=67890&y=2025" title="Jane Smith">SMITH Jane</a></td>
        <td>82</td>
    </tr>
</table>
</body>
</html>'''
        
        # Expected cyclist data
        self.expected_cyclists = [
            {
                'name': 'Doe John',
                'href': 'rider.php?r=12345&y=2025',
                'rider_id': '12345',
                'table_row_number': 1,
                'first_cycling_id': 12345
            },
            {
                'name': 'Smith Jane',
                'href': 'rider.php?r=67890&y=2025',
                'rider_id': '67890',
                'table_row_number': 2,
                'first_cycling_id': 67890
            }
        ]

    def test_parse_github_issue_form_valid_data(self):
        """Test parsing valid GitHub issue form data."""
        result = parse_github_issue_form(self.sample_issue_body)
        
        # Check all required fields
        assert result['change_name'] == '2025-08-06-tour-of-panama---stage-1-results'
        assert result['date'] == '2025-08-06'
        assert result['author'] == 'BenGe'
        assert result['race_url'] == 'https://firstcycling.com/race.php?r=32345&y=2025'
        assert result['description'] == 'Adding results from Stage 1 of the Tour of Panama. Great race with strong competition.'
        assert result['namespace'] == 'procyclingstats'
        assert result['branch_name'] == 'change/2025-08-06-tour-of-panama---stage-1-results'
        
        # Check that branch name is properly sanitized
        assert ' ' not in result['branch_name']
        assert result['branch_name'].startswith('change/')

    def test_parse_github_issue_form_missing_fields(self):
        """Test parsing GitHub issue form with missing fields."""
        incomplete_body = '''
### Change Name
Test Change

### Date
2025-08-06
'''
        result = parse_github_issue_form(incomplete_body)
        
        # Should have some fields filled
        assert result['change_name'] == '2025-08-06-test-change'
        assert result['date'] == '2025-08-06'
        
        # Missing fields should be empty strings
        assert result['author'] == ''
        assert result['race_url'] == ''
        assert result['description'] == ''
        assert result['namespace'] == ''

    def test_parse_github_issue_form_special_characters(self):
        """Test parsing with special characters in change name."""
        special_body = '''
### Change Name
Test Race (2025) - Stage #1 & Results!

### Date
2025-08-06

### Author
Test Author

### Race URL
https://firstcycling.com/race.php?r=123

### Namespace
test
'''
        result = parse_github_issue_form(special_body)
        
        # Check that special characters are properly handled in branch name
        assert result['change_name'] == '2025-08-06-test-race--2025----stage--1---results-'
        assert result['branch_name'] == 'change/2025-08-06-test-race--2025----stage--1---results-'
        
        # Only alphanumeric, hyphens, and underscores should remain
        import re
        assert re.match(r'^change/[a-zA-Z0-9_-]+$', result['branch_name'])

    def test_parse_firstcycling_html_valid_data(self):
        """Test parsing valid FirstCycling HTML content."""
        cyclists, success, error = parse_firstcycling_html(self.sample_html)
        
        assert success is True
        assert error is None
        assert len(cyclists) == 2
        
        # Check first cyclist
        first_cyclist = cyclists[0]
        assert first_cyclist['name'] == 'Doe John'
        assert first_cyclist['rider_id'] == '12345'
        assert first_cyclist['href'] == 'rider.php?r=12345&y=2025'
        assert first_cyclist['table_row_number'] == 1
        assert first_cyclist['first_cycling_id'] == 12345

    def test_parse_firstcycling_html_empty_content(self):
        """Test parsing empty HTML content."""
        cyclists, success, error = parse_firstcycling_html("")
        
        assert success is True
        assert error is None
        assert len(cyclists) == 0

    def test_parse_firstcycling_html_no_cyclist_links(self):
        """Test parsing HTML with no cyclist links."""
        html_no_links = '''
<html>
<body>
<table>
    <tr><th>Header</th></tr>
    <tr><td>No links here</td></tr>
</table>
</body>
</html>'''
        
        cyclists, success, error = parse_firstcycling_html(html_no_links)
        
        assert success is True
        assert error is None
        assert len(cyclists) == 0

    def test_parse_firstcycling_html_malformed_html(self):
        """Test parsing malformed HTML."""
        malformed_html = "<html><body><table><tr><td>Incomplete"
        
        cyclists, success, error = parse_firstcycling_html(malformed_html)
        
        # Should still succeed but find no cyclists
        assert success is True
        assert error is None
        assert len(cyclists) == 0

    def test_parse_firstcycling_html_bytes_input(self):
        """Test parsing HTML provided as bytes."""
        html_bytes = self.sample_html.encode('utf-8')
        
        cyclists, success, error = parse_firstcycling_html(html_bytes)
        
        assert success is True
        assert error is None
        assert len(cyclists) == 2

    @patch('src.utils.commons.get_proxy_list')
    @patch('requests.get')
    def test_fetch_firstcycling_html_success(self, mock_get, mock_get_proxy_list):
        """Test successful HTML fetching."""
        # Mock proxy function to return no proxies (direct connection)
        mock_get_proxy_list.return_value = []
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.content = b"<html>Test content</html>"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        url = "https://firstcycling.com/race.php?r=123&pcm=1"
        content, success, error = fetch_firstcycling_html(url)
        
        assert success is True
        assert error is None
        assert content == b"<html>Test content</html>"
        
        # Check that the direct connection call was made
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert 'headers' in kwargs
        assert 'User-Agent' in kwargs['headers']
        assert kwargs.get('proxies') is None  # Direct connection

    @patch('src.utils.commons.get_proxy_list')
    @patch('requests.get')
    def test_fetch_firstcycling_html_network_error(self, mock_get, mock_get_proxy_list):
        """Test HTML fetching with network error."""
        # Mock proxy function to return no proxies (direct connection)
        mock_get_proxy_list.return_value = []
        
        from requests import RequestException
        mock_get.side_effect = RequestException("Network error")
        
        url = "https://firstcycling.com/race.php?r=123&pcm=1"
        content, success, error = fetch_firstcycling_html(url)
        
        assert success is False
        assert content is None
        assert "Network error" in error

    @patch('src.utils.commons.get_proxy_list')
    def test_fetch_firstcycling_html_missing_pcm_parameter(self, mock_get_proxy_list):
        """Test HTML fetching with missing pcm parameter."""
        # Mock proxy function to return no proxies (direct connection)
        mock_get_proxy_list.return_value = []
        
        url = "https://firstcycling.com/race.php?r=123"
        content, success, error = fetch_firstcycling_html(url)
        
        assert success is False
        assert content is None
        assert "pcm=1 parameter" in error or "Error fetching HTML" in error

    @patch('src.api.fetch_firstcycling_html')
    @patch('src.api.parse_firstcycling_html')
    def test_scrape_firstcycling_cyclists_success(self, mock_parse, mock_fetch):
        """Test successful cyclist scraping."""
        # Mock successful fetch
        mock_fetch.return_value = (self.sample_html, True, None)
        
        # Mock successful parse
        mock_parse.return_value = (self.expected_cyclists, True, None)
        
        url = "https://firstcycling.com/race.php?r=123&pcm=1"
        cyclists, success, error = scrape_firstcycling_cyclists(url)
        
        assert success is True
        assert error is None
        assert len(cyclists) == 2
        
        # Verify function calls
        mock_fetch.assert_called_once_with(url)
        mock_parse.assert_called_once_with(self.sample_html)

    @patch('src.api.fetch_firstcycling_html')
    def test_scrape_firstcycling_cyclists_fetch_failure(self, mock_fetch):
        """Test cyclist scraping with fetch failure."""
        # Mock failed fetch
        mock_fetch.return_value = (None, False, "Fetch error")
        
        url = "https://firstcycling.com/race.php?r=123&pcm=1"
        cyclists, success, error = scrape_firstcycling_cyclists(url)
        
        assert success is False
        assert error == "Fetch error"
        assert cyclists == []

    @patch('src.api.commons.get_path')
    @patch('os.path.exists')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    @patch('yaml.safe_load')
    @patch('yaml.dump')
    def test_create_automated_change_file_success(self, mock_yaml_dump, mock_yaml_load, mock_file, mock_makedirs, mock_exists, mock_get_path):
        """Test successful creation of automated change file with stats lookup."""
        # Mock path functions
        mock_get_path.side_effect = lambda ns, path_type: {
            'changes_dir': '/test/changes',
            'stats_file': '/test/stats.yaml'
        }[path_type]
        
        # Mock stats file exists and content
        mock_exists.return_value = True
        mock_yaml_load.return_value = {
            '12345': {
                'name': 'Lamperti Luke',
                'first_cycling_id': 98765,
                'stats': {
                    'fla': 85,
                    'mo': 70,
                    'tt': 75
                }
            },
            '67890': {
                'name': 'Test Rider',
                'first_cycling_id': 54321,
                'stats': {
                    'fla': 80,
                    'spr': 90
                }
            }
        }
        
        # Test data - cyclists from scraping with first_cycling_id
        namespace = 'test_namespace'
        change_name = 'test-change'
        form_data = {
            'author': 'Test Author',
            'date': '2025-08-06',
            'description': 'Test description',
            'race_url': 'https://firstcycling.com/race.php?r=123&pcm=1'
        }
        scraped_cyclists = [
            {
                'name': 'Lamperti Luke',
                'first_cycling_id': 98765,
                'rider_id': '98765'
            },
            {
                'name': 'Unknown Rider',
                'first_cycling_id': 99999,  # Not in stats file
                'rider_id': '99999'
            }
        ]
        
        # Call function
        file_path, success, error = create_automated_change_file(namespace, change_name, form_data, scraped_cyclists)
        
        # Assertions
        assert success is True
        assert error is None
        assert file_path.replace('\\', '/') == '/test/changes/test-change/change.yaml'
        
        # Check that directory was created
        expected_path = '/test/changes/test-change'
        actual_call_args = mock_makedirs.call_args[0][0]
        assert actual_call_args.replace('\\', '/') == expected_path
        
        # Check that YAML was dumped
        mock_yaml_dump.assert_called_once()
        call_args = mock_yaml_dump.call_args[0]
        change_data = call_args[0]
        
        assert change_data['author'] == 'Test Author'
        assert change_data['date'] == '2025-08-06'
        assert change_data['race_url'] == 'https://firstcycling.com/race.php?r=123&pcm=1'
        
        # Check that only matched cyclist was included with their stats
        assert len(change_data['stats']) == 1
        matched_cyclist = change_data['stats'][0]
        assert matched_cyclist['pcm_id'] == '12345'
        assert matched_cyclist['name'] == 'Lamperti Luke'
        assert matched_cyclist['first_cycling_id'] == 98765
        assert matched_cyclist['fla'] == 85
        assert matched_cyclist['mo'] == 70
        assert matched_cyclist['tt'] == 75

    @patch('src.api.commons.get_path')
    @patch('os.path.exists')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    @patch('yaml.dump')
    def test_create_automated_change_file_no_stats_file(self, mock_yaml_dump, mock_file, mock_makedirs, mock_exists, mock_get_path):
        """Test change file creation when stats.yaml doesn't exist."""
        # Mock path functions
        mock_get_path.side_effect = lambda ns, path_type: {
            'changes_dir': '/test/changes',
            'stats_file': '/test/stats.yaml'
        }[path_type]
        
        # Mock stats file doesn't exist
        mock_exists.return_value = False
        
        # Test data
        namespace = 'test_namespace'
        change_name = 'test-change'
        form_data = {
            'author': 'Test Author',
            'date': '2025-08-06',
            'description': 'Test description',
            'race_url': 'https://firstcycling.com/race.php?r=123&pcm=1'
        }
        scraped_cyclists = [
            {
                'name': 'Some Rider',
                'first_cycling_id': 12345,
                'rider_id': '12345'
            }
        ]
        
        # Call function
        file_path, success, error = create_automated_change_file(namespace, change_name, form_data, scraped_cyclists)
        
        # Assertions
        assert success is True
        assert error is None
        
        # Check that YAML was dumped
        mock_yaml_dump.assert_called_once()
        call_args = mock_yaml_dump.call_args[0]
        change_data = call_args[0]
        
        # Should have empty stats list since no stats file to match against
        assert len(change_data['stats']) == 0

    @patch('src.api.commons.get_path')
    @patch('os.path.exists')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    @patch('yaml.safe_load')
    @patch('yaml.dump')
    def test_create_automated_change_file_partial_matches(self, mock_yaml_dump, mock_yaml_load, mock_file, mock_makedirs, mock_exists, mock_get_path):
        """Test change file creation with partial cyclist matches."""
        # Mock path functions
        mock_get_path.side_effect = lambda ns, path_type: {
            'changes_dir': '/test/changes',
            'stats_file': '/test/stats.yaml'
        }[path_type]
        
        # Mock stats file exists with limited cyclists
        mock_exists.return_value = True
        mock_yaml_load.return_value = {
            '100': {
                'name': 'Found Rider',
                'first_cycling_id': 777,
                'stats': {
                    'fla': 85,
                    'mo': 70
                }
            }
        }
        
        # Test data - mix of found and not found cyclists
        scraped_cyclists = [
            {
                'name': 'Found Rider',
                'first_cycling_id': 777,  # Will be found
                'rider_id': '777'
            },
            {
                'name': 'Missing Rider 1',
                'first_cycling_id': 888,  # Won't be found
                'rider_id': '888'
            },
            {
                'name': 'Missing Rider 2',
                'first_cycling_id': 999,  # Won't be found
                'rider_id': '999'
            }
        ]
        
        namespace = 'test_namespace'
        change_name = 'test-change'
        form_data = {
            'author': 'Test Author',
            'date': '2025-08-06',
            'description': 'Test partial matches',
            'race_url': 'https://firstcycling.com/race.php?r=123&pcm=1'
        }
        
        # Call function
        file_path, success, error = create_automated_change_file(namespace, change_name, form_data, scraped_cyclists)
        
        # Assertions
        assert success is True
        assert error is None
        
        # Check that YAML was dumped
        mock_yaml_dump.assert_called_once()
        call_args = mock_yaml_dump.call_args[0]
        change_data = call_args[0]
        
        # Should have only 1 matched cyclist out of 3 scraped
        assert len(change_data['stats']) == 1
        matched_cyclist = change_data['stats'][0]
        assert matched_cyclist['pcm_id'] == '100'
        assert matched_cyclist['name'] == 'Found Rider'
        assert matched_cyclist['first_cycling_id'] == 777
        assert matched_cyclist['fla'] == 85
        assert matched_cyclist['mo'] == 70

    @patch('src.api.commons.get_path')
    @patch('os.makedirs')
    def test_create_automated_change_file_directory_error(self, mock_makedirs, mock_get_path):
        """Test change file creation with directory creation error."""
        # Mock path and directory creation error
        mock_get_path.side_effect = lambda ns, path_type: {
            'changes_dir': '/test/changes',
            'stats_file': '/test/stats.yaml'
        }[path_type]
        mock_makedirs.side_effect = OSError("Permission denied")
        
        # Test data
        namespace = 'test_namespace'
        change_name = 'test-change'
        form_data = {'author': 'Test', 'date': '2025-08-06'}
        cyclists = []
        
        # Call function
        file_path, success, error = create_automated_change_file(namespace, change_name, form_data, cyclists)
        
        # Assertions
        assert success is False
        assert file_path is None
        assert "Permission denied" in error

    @patch('src.api.parse_github_issue_form')
    @patch('src.api.scrape_firstcycling_cyclists')
    @patch('src.api.create_automated_change_file')
    def test_process_automated_change_request_success(self, mock_create_file, mock_scrape, mock_parse):
        """Test successful processing of automated change request."""
        # Mock functions
        mock_parse.return_value = {
            'change_name': 'Test Change',
            'date': '2025-08-06',
            'author': 'Test Author',
            'race_url': 'https://firstcycling.com/race.php?r=123&pcm=1',
            'namespace': 'test_namespace'
        }
        mock_scrape.return_value = (self.expected_cyclists, True, None)
        mock_create_file.return_value = ('/test/change.yaml', True, None)
        
        # Call function
        result = process_automated_change_request(self.sample_issue_body)
        
        # Debug output
        print(f"Result: {result}")
        
        # Assertions
        assert result['success'] is True
        assert result['error'] is None
        assert result['cyclists_found'] == 2
        assert result['change_file_path'] == '/test/change.yaml'
        assert 'sql_files_generated' not in result

    @patch('src.api.parse_github_issue_form')
    def test_process_automated_change_request_missing_fields(self, mock_parse):
        """Test processing with missing required fields."""
        # Mock missing fields
        mock_parse.return_value = {
            'change_name': '',  # Missing
            'date': '2025-08-06',
            'author': 'Test Author',
            'race_url': 'https://firstcycling.com/race.php?r=123',
            'namespace': 'test_namespace'
        }
        
        # Call function
        result = process_automated_change_request(self.sample_issue_body)
        
        # Assertions
        assert result['success'] is False
        assert 'Missing required form fields' in result['error']

    @patch('src.api.parse_github_issue_form')
    def test_process_automated_change_request_invalid_url(self, mock_parse):
        """Test processing with invalid URL format."""
        # Mock invalid URL
        mock_parse.return_value = {
            'change_name': 'Test Change',
            'date': '2025-08-06',
            'author': 'Test Author',
            'race_url': 'https://invalid-site.com/race.php',
            'namespace': 'test_namespace'
        }
        
        # Call function
        result = process_automated_change_request(self.sample_issue_body)
        
        # Assertions
        assert result['success'] is False
        assert 'Invalid URL format' in result['error']

    def test_process_automated_change_request_url_without_protocol(self):
        """Test processing URL without protocol (should be auto-fixed)."""
        # Test data for simple case
        simple_issue_body = '''### Change Name
Test Change
### Date  
2025-08-06
### Author
Test Author
### Race URL
https://firstcycling.com/race.php?r=123&pcm=1
### Namespace
test_namespace'''
        
        with patch('src.api.scrape_firstcycling_cyclists') as mock_scrape, \
             patch('src.api.create_automated_change_file') as mock_create:
            
            mock_scrape.return_value = ([], True, None)
            mock_create.return_value = ('/test/change.yaml', True, None)
            
            result = process_automated_change_request(simple_issue_body)
            
            # Should succeed and auto-add https://
            assert result['success'] is True
            assert result['form_data']['race_url'].startswith('https://')

    def test_process_automated_change_request_url_without_pcm_parameter(self):
        """Test processing URL without pcm parameter (should be auto-added)."""
        issue_body = '''
### Change Name
Test Change

### Date
2025-08-06

### Author
Test Author

### Race URL
https://firstcycling.com/race.php?r=123

### Namespace
test_namespace
'''
        
        with patch('src.api.scrape_firstcycling_cyclists') as mock_scrape, \
             patch('src.api.create_automated_change_file') as mock_create:
            
            mock_scrape.return_value = ([], True, None)
            mock_create.return_value = ('/test/change.yaml', True, None)
            
            result = process_automated_change_request(issue_body)
            
            # Should succeed and auto-add pcm=1
            assert result['success'] is True
            assert 'pcm=1' in result['form_data']['race_url']

if __name__ == '__main__':
    pytest.main([__file__])
