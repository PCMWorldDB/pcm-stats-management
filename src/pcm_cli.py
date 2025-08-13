#!/usr/bin/env python3
"""
PCM Stats Management CLI Tool

A unified command-line interface for all PCM stats management operations.
This script consolidates all functionality from multiple scripts into a single tool.

Usage:
    python pcm_cli.py <command> [options]

Commands:
    process-changes- Process change files (main CI/CD operation)
    validate-yaml  - Validate YAML change files format
    import-from-db - Import cyclist data from SQLite database
    process-uat    - Process UAT changes by executing SQL and exporting data
    help           - Show this help message

Examples:
    python pcm_cli.py process-changes
    python pcm_cli.py validate-yaml
    python pcm_cli.py process-uat
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add the parent directory (repo root) to Python path so we can import src modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from src import api as model_api


def process_changes():
    """Process change files for all namespaces (main CI/CD operation)."""
    try:
        summary = model_api.process_all_namespaces()
        
        print(json.dumps(summary))
        
        # Check if any changes were made
        if summary['total_changes'] > 0:
            print("✅ Processing completed successfully with new changes!")
            return True
        else:
            print("ℹ️  Processing completed - no new changes found.")
            return summary['overall_success']
            
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        return False


def validate_yaml_files():
    """Validate all YAML files (both change files and stats files)."""
    try:
        # Delegate to API for validation logic
        return model_api.validate_yaml_files()
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        import traceback
        traceback.print_exc()
        return False


def import_from_db(namespace, db_file):
    """Import cyclist data from SQLite database to create stats.yaml file."""
    try:
        # Delegate to API for import logic
        return model_api.import_cyclists_from_db(namespace, db_file)
    except Exception as e:
        print(f"❌ Error during database import: {e}")
        import traceback
        traceback.print_exc()
        return False


def process_uat():
    """Process UAT changes by executing SQL inserts and exporting tracking data."""
    try:
        # Delegate to API for UAT processing logic
        summary = model_api.process_uat_changes()
        
        print(json.dumps(summary))
        
        # Check if any changes were executed
        if summary['total_changes_executed'] > 0:
            print("✅ UAT processing completed successfully with changes executed!")
            return True
        else:
            print("ℹ️  UAT processing completed - no new changes found.")
            return summary['overall_success']
            
    except Exception as e:
        print(f"❌ Error during UAT processing: {e}")
        import traceback
        traceback.print_exc()
        return False
  
def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="PCM Stats Management CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python pcm_cli.py process-changes
    python pcm_cli.py validate-yaml
    python pcm_cli.py process-uat
    python pcm_cli.py import-from-db 2025 /path/to/database.sqlite
        """
    )
    
    parser.add_argument(
        'command',
        choices=['process-changes', 'validate-yaml', 'import-from-db', 'process-uat', 'help'],
        help='Command to execute'
    )
    
    parser.add_argument(
        'namespace',
        nargs='?',
        help='Namespace for import-from-db command'
    )
    
    parser.add_argument(
        'db_file',
        nargs='?',
        help='SQLite database file path for import-from-db command'
    )
    
    # Handle no arguments or help
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ['help', '--help', '-h']):
        parser.print_help()
        return 0
    
    args = parser.parse_args()

    # Execute command
    success = True
    
    if args.command == 'process-changes':
        print("=" * 60)
        print(f"🤖 PCM Stats Management - Processing All Namespaces")
        print("=" * 60)
        
        success = process_changes()
        
    elif args.command == 'validate-yaml':
        success = validate_yaml_files()
        
    elif args.command == 'import-from-db':
        if not args.namespace or not args.db_file:
            print("❌ Error: import-from-db command requires namespace and db_file arguments")
            print("Usage: python pcm_cli.py import-from-db <namespace> <db_file>")
            return 1
        
        print("=" * 60)
        print(f"📥 Importing cyclist data from database to namespace: {args.namespace}")
        print("=" * 60)
        
        success = import_from_db(args.namespace, args.db_file)
        
    elif args.command == 'process-uat':
        print("=" * 60)
        print(f"🚀 PCM Stats Management - UAT Processing")
        print("=" * 60)
        
        success = process_uat()
        
    elif args.command == 'help':
        parser.print_help()
        return 0
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
