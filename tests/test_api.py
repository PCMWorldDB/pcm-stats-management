import os
import pytest
import yaml
from src import api
from src.utils import commons

def test_api_module_import():
    """Test that the api module can be imported correctly."""
    assert hasattr(api, 'process_all_namespaces')
    assert hasattr(api, 'process_namespace')
    assert hasattr(api, 'update_stats_file_with_changes')

def test_commons_module_import():
    """Test that the commons module can be imported correctly."""
    assert hasattr(commons, 'STAT_KEYS')
    assert hasattr(commons, 'get_path')
    assert hasattr(commons, 'get_available_namespaces')

def test_stat_keys_order():
    """Test that STAT_KEYS has the expected order."""
    expected_keys = ['fla', 'mo', 'mm', 'dh', 'cob', 'tt', 'prl', 'spr', 'acc', 'end', 'res', 'rec', 'hil', 'att']
    assert commons.STAT_KEYS == expected_keys

def test_get_path_function():
    """Test that get_path function works correctly."""
    namespace = "test"
    
    # Test various path types
    assert commons.get_path(namespace, 'root') == os.path.join('data', namespace)
    assert commons.get_path(namespace, 'changes_dir') == os.path.join('data', namespace, 'changes')
    assert commons.get_path(namespace, 'stats_file') == os.path.join('data', namespace, 'stats.yaml')
    assert commons.get_path(namespace, 'tracking_db') == os.path.join('data', namespace, 'tracking_db.sqlite')
    assert commons.get_path(namespace, 'cdb') == os.path.join('data', namespace, 'cdb')
    
    # Test invalid path type
    with pytest.raises(AssertionError):
        commons.get_path(namespace, 'invalid_type')