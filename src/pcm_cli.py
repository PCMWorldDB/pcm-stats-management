#!/usr/bin/env python3
"""
PCM Stats Management CLI Tool

A unified command-line interface for all PCM stats management operations.
This script consolidates all functionality from multiple scripts into a single tool.

Usage:
    python pcm_cli.py <command> [options]

Commands:
    process        - Process change files (main CI/CD operation)
    validate-yaml  - Validate YAML change files format
    validate-setup - Validate repository structure and setup
    test-local     - Run local CI/CD simulation
    status         - Check project status and generate workflow variables
    help           - Show this help message

Examples:
    python pcm_cli.py process
    python pcm_cli.py validate-yaml
    python pcm_cli.py validate-setup
    python pcm_cli.py test-local
    python pcm_cli.py status
"""

import os
import sys
import json
import yaml
import tempfile
import shutil
import argparse
from pathlib import Path
from src.utils import commons
from src.model import api as model_api
# Add src directory to Python path
sys.path.insert(0, os.path.dirname(__file__))




class PCMStatsManager:
    """Main class for PCM Stats Management operations."""
    
    def __init__(self):
        # If we're in src directory, go up one level to repo root
        if Path(__file__).parent.name == 'src':
            self.repo_root = Path(__file__).parent.parent
        else:
            self.repo_root = Path(__file__).parent.parent
        os.chdir(self.repo_root)
    
    def process_changes(self):
        """Process change files for all namespaces (main CI/CD operation)."""
        print("🚀 Starting PCM stats processing for all namespaces...")

        try:
            # Process all namespaces automatically
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
    
    
    def validate_yaml_syntax(self, file_path):
        """Validate that a YAML file has correct syntax."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
            return True, None
        except yaml.YAMLError as e:
            return False, f"YAML syntax error: {e}"
        except Exception as e:
            return False, f"File error: {e}"
    
    def validate_required_fields_change_file(self, file_path, data):
        """Validate that required fields are present in a change file YAML data."""
        required_fields = ['name', 'date', 'stats']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        # Additional validation for stats
        if not isinstance(data['stats'], list):
            return False, "stats must be a list"
        
        if len(data['stats']) == 0:
            return False, "stats cannot be empty"
        
        # Validate each stat update entry
        for i, stat_update in enumerate(data['stats']):
            if not isinstance(stat_update, dict):
                return False, f"stats[{i}] must be a dictionary"
            
            required_stat_fields = ['pcm_id', 'name']
            missing_stat_fields = [field for field in required_stat_fields if field not in stat_update]
            
            if missing_stat_fields:
                return False, f"stats[{i}] missing required fields: {', '.join(missing_stat_fields)}"
        
        return True, None
    
    def validate_required_fields_stats_file(self, file_path, data):
        """Validate that required fields are present in a stats file YAML data."""
        if not isinstance(data, dict):
            return False, "Stats file must be a dictionary with cyclist IDs as keys"
        
        if len(data) == 0:
            return False, "Stats file cannot be empty"
        
        # Validate each cyclist entry
        for cyclist_id, cyclist_data in data.items():
            if not isinstance(cyclist_data, dict):
                return False, f"Cyclist {cyclist_id} data must be a dictionary"
            
            required_fields = ['name']
            missing_fields = [field for field in required_fields if field not in cyclist_data]
            
            if missing_fields:
                return False, f"Cyclist {cyclist_id} missing required fields: {', '.join(missing_fields)}"
            
            # Validate that cyclist ID is numeric (can be string or int)
            try:
                int(cyclist_id)
            except ValueError:
                return False, f"Cyclist ID '{cyclist_id}' must be numeric"
        
        return True, None
    
    def detect_yaml_file_type(self, file_path, data):
        """Detect whether this is a change file or stats file based on structure."""
        if isinstance(data, dict):
            # Check if it has change file structure (name, date, stats at top level)
            if 'name' in data and 'date' in data and 'stats' in data:
                return 'change_file'
            # Check if it has stats file structure (numeric keys with cyclist data)
            elif all(isinstance(key, (str, int)) for key in data.keys()):
                # Try to convert keys to int to confirm they're cyclist IDs
                try:
                    numeric_keys = [int(k) for k in data.keys()]
                    return 'stats_file'
                except ValueError:
                    pass
        
        return 'unknown'
    
    def validate_single_yaml_file(self, file_path):
        """Validate a single YAML file (either change file or stats file)."""
        # First validate YAML syntax
        is_valid, error = self.validate_yaml_syntax(file_path)
        if not is_valid:
            return False, error
        
        # Load and validate structure
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Detect file type
            file_type = self.detect_yaml_file_type(file_path, data)
            
            if file_type == 'change_file':
                is_valid, error = self.validate_required_fields_change_file(file_path, data)
                if not is_valid:
                    return False, f"Change file validation error: {error}"
            elif file_type == 'stats_file':
                is_valid, error = self.validate_required_fields_stats_file(file_path, data)
                if not is_valid:
                    return False, f"Stats file validation error: {error}"
            else:
                return False, "Unknown file type - does not match change file or stats file structure"
            
            return True, None
            
        except Exception as e:
            return False, f"Validation error: {e}"
    
    def validate_yaml_files(self):
        """Validate all YAML files (both change files and stats files)."""
        print(f"📋 Validating YAML files format for all namespaces...")
        
        try:
            all_yaml_files = []
            validation_errors = []
            
            # Get all available namespaces
            namespaces = commons.get_available_namespaces() if commons else ['2025']
            
            for namespace in namespaces:
                print(f"🔍 Checking namespace: {namespace}")
                
                # Check change files using namespace
                if commons:
                    changes_dir = Path(commons.get_path(namespace, 'changes_dir'))
                else:
                    changes_dir = Path(f'data/{namespace}/changes')
                
                if changes_dir.exists():
                    change_files = []
                    for pattern in ['*.yaml', '*.yml']:
                        change_files.extend(changes_dir.glob(pattern))
                    all_yaml_files.extend([(f, f'change-{namespace}') for f in change_files])
                    print(f"🔍 Found {len(change_files)} change files in {changes_dir}")
                else:
                    print(f"ℹ️  Changes directory not found: {changes_dir}")
                
                # Check stats file using namespace
                if commons:
                    stats_file = Path(commons.get_path(namespace, 'stats_file'))
                else:
                    stats_file = Path(f'data/{namespace}/stats.yaml')
                    
                if stats_file.exists():
                    all_yaml_files.append((stats_file, f'stats-{namespace}'))
                    print(f"🔍 Found stats file: {stats_file}")
                else:
                    print(f"ℹ️  Stats file not found: {stats_file}")
            
            # Check legacy change files in src/changes/ (for backward compatibility)
            legacy_changes_dir = Path('src/changes')
            if legacy_changes_dir.exists():
                legacy_change_files = []
                for pattern in ['*.yaml', '*.yml']:
                    legacy_change_files.extend(legacy_changes_dir.glob(pattern))
                all_yaml_files.extend([(f, 'legacy_change') for f in legacy_change_files])
                print(f"🔍 Found {len(legacy_change_files)} legacy change files in {legacy_changes_dir}")
            
            if not all_yaml_files:
                print("ℹ️  No YAML files found to validate")
                return True
            
            print(f"🔍 Total {len(all_yaml_files)} YAML files to validate")
            
            # Validate each file
            for yaml_file, file_category in all_yaml_files:
                is_valid, error = self.validate_single_yaml_file(yaml_file)
                
                if is_valid:
                    print(f"✅ {yaml_file.name} ({file_category}): Valid")
                else:
                    print(f"❌ {yaml_file.name} ({file_category}): {error}")
                    validation_errors.append((yaml_file.name, error))
            
            # Summary
            if validation_errors:
                print(f"\n❌ Validation failed for {len(validation_errors)} files:")
                for filename, error in validation_errors:
                    print(f"   - {filename}: {error}")
                return False
            else:
                print(f"\n✅ All {len(all_yaml_files)} YAML files passed validation!")
                return True
                
        except Exception as e:
            print(f"❌ Error during validation: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def check_file_exists(self, file_path, description=""):
        """Check if a file exists and print status."""
        if os.path.exists(file_path):
            print(f"✅ {description}: {file_path}")
            return True
        else:
            print(f"❌ Missing {description}: {file_path}")
            return False
    
    def check_directory_exists(self, dir_path, description=""):
        """Check if a directory exists and print status."""
        if os.path.exists(dir_path):
            print(f"✅ {description}: {dir_path}")
            return True
        else:
            print(f"❌ Missing {description}: {dir_path}")
            return False
    
    def validate_python_imports(self):
        """Validate that required Python imports work."""
        print("\n🐍 Validating Python imports...")
        
        imports_to_test = [
            ("yaml", "PyYAML"),
            ("sqlite3", "SQLite3 (built-in)"),
            ("pathlib", "pathlib (built-in)"),
            ("json", "json (built-in)")
        ]
        
        all_imports_ok = True
        
        for module_name, description in imports_to_test:
            try:
                __import__(module_name)
                print(f"✅ {description}")
            except ImportError:
                print(f"❌ Missing: {description}")
                all_imports_ok = False
        
        return all_imports_ok
    
    def validate_workflow_syntax(self):
        """Validate GitHub Actions workflow YAML syntax."""
        print("\n📋 Validating workflow files...")
        
        workflows_dir = self.repo_root / ".github" / "workflows"
        
        if not workflows_dir.exists():
            print(f"❌ Workflows directory not found: {workflows_dir}")
            return False
        
        workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
        
        if not workflow_files:
            print("❌ No workflow files found!")
            return False
        
        all_valid = True
        
        for workflow_file in workflow_files:
            try:
                with open(workflow_file) as f:
                    workflow_data = yaml.safe_load(f)
                
                # Basic validation
                required_keys = ['name', 'on', 'jobs']
                missing_keys = [key for key in required_keys if key not in workflow_data]
                
                if missing_keys:
                    print(f"❌ {workflow_file.name}: Missing required keys: {missing_keys}")
                    all_valid = False
                else:
                    print(f"✅ {workflow_file.name}: Valid YAML syntax")
                    
            except Exception as e:
                print(f"❌ {workflow_file.name}: YAML error: {e}")
                all_valid = False
        
        return all_valid
    
    def validate_repository_structure(self):
        """Validate the repository has the expected structure."""
        print("\n📁 Validating repository structure...")
        
        model_dir = commons.MODEL_DIR_PATH if commons else "src/models"
        
        # Use default namespace for validation (2025) or check all namespaces
        default_namespace = '2025'
        stats_file_path = commons.get_path(default_namespace, 'stats_file') if commons else "data/stats.yaml"
        changes_dir_path = commons.get_path(default_namespace, 'changes_dir') if commons else "data/changes"
        tracking_db_path = commons.get_path(default_namespace, 'tracking_db') if commons else "data/tracking_db.sqlite"
        
        required_files = [
            (self.repo_root / "requirements.txt", "Main requirements file"),
            (self.repo_root / model_dir / "api.py", "Models API"),
            (self.repo_root / model_dir / "tracking_schema.sql", "Database schema"),
            (self.repo_root / "src" / "utils" / "commons.py", "Common utilities"),
            (self.repo_root / stats_file_path, "Main stats file"),
            (self.repo_root / ".github" / "workflows" / "cicd.yml", "Main CI/CD workflow"),
        ]
        
        required_dirs = [
            (self.repo_root / changes_dir_path, "Data changes directory"),
            (self.repo_root / "src" / "changes", "Legacy changes directory"),
            (self.repo_root / os.path.dirname(tracking_db_path), "Database directory"),
            (self.repo_root / "tests", "Tests directory"),
            (self.repo_root / ".github" / "workflows", "Workflows directory"),
        ]
        
        all_files_ok = True
        all_dirs_ok = True
        
        for file_path, description in required_files:
            if not self.check_file_exists(file_path, description):
                all_files_ok = False
        
        for dir_path, description in required_dirs:
            if not self.check_directory_exists(dir_path, description):
                all_dirs_ok = False
                # Create missing directories
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"   ✅ Created: {dir_path}")
        
        return all_files_ok and all_dirs_ok
    
    def validate_setup(self):
        """Run comprehensive setup validation."""
        print("=" * 60)
        print("🔍 GitHub Actions CI/CD Setup Validator")
        print("=" * 60)
        
        all_checks_passed = True
        
        # Run all validation checks
        checks = [
            ("Repository Structure", self.validate_repository_structure),
            ("Python Imports", self.validate_python_imports),
            ("Workflow Syntax", self.validate_workflow_syntax)
        ]
        
        for check_name, check_function in checks:
            print(f"\n🔍 Running {check_name} validation...")
            if not check_function():
                all_checks_passed = False
        
        # Generate report
        report = {
            "timestamp": str(os.popen("date").read().strip()) if os.name != 'nt' else 'timestamp',
            "repository_root": str(self.repo_root),
            "python_version": sys.version,
            "platform": sys.platform,
            "status": "ready" if all_checks_passed else "needs_attention"
        }
        
        report_file = self.repo_root / "ci_cd_setup_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Setup report saved to: {report_file}")
        
        print("\n" + "=" * 60)
        if all_checks_passed:
            print("🎉 All validations passed! Your CI/CD setup is ready!")
            print("\n📋 Next steps:")
            print("   1. Commit and push your changes to GitHub")
            print("   2. Check the Actions tab in your GitHub repository")
            print("   3. Add some YAML change files to test the workflow")
            print("   4. Monitor the workflow execution and logs")
        else:
            print("⚠️  Some validations failed. Please address the issues above.")
            print("\n📋 Common solutions:")
            print("   1. Install missing Python packages: pip install -r requirements.txt")
            print("   2. Create missing directories (some were auto-created)")
            print("   3. Fix any YAML syntax errors in workflow files")
            print("   4. Ensure all required files are present")
        
        print("=" * 60)
        return all_checks_passed
    
    def create_sample_change_file(self):
        """Create a sample change file for testing."""
        default_namespace = '2025'  # Use default namespace for sample
        print(f"📝 Creating sample change file for namespace '{default_namespace}'...")
        
        # Use commons path for changes directory with namespace
        if commons:
            changes_dir = Path(commons.get_path(default_namespace, 'changes_dir'))
        else:
            changes_dir = self.repo_root / f"data/{default_namespace}/changes"
        changes_dir.mkdir(parents=True, exist_ok=True)
        
        sample_file = changes_dir / "test-change.yaml"
        
        sample_content = """name: "Test Change for CI/CD"
author: "Local Test"
date: "2025-08-07"
description: "Sample change file for testing GitHub Actions workflow"

stats:
  - pcm_id: 12345
    name: "Test Cyclist"
    first_cycling_id: "tc001"
    mo: 75
    hil: 72
    spr: 68
    tt: 70
    cob: 65
    end: 78
    res: 76
"""
        
        with open(sample_file, 'w') as f:
            f.write(sample_content)
        
        print(f"✅ Created sample file: {sample_file}")
        return sample_file
    
    def test_local_ci(self):
        """Run local CI/CD simulation."""
        print("=" * 60)
        print("🧪 PCM Stats Management - Local CI/CD Tester")
        print("=" * 60)
        
        try:
            # Step 1: Validate workflow files
            print("🔍 Validating workflow files...")
            if not self.validate_workflow_syntax():
                print("❌ Workflow validation failed!")
                return False
            
            # Step 2: Create sample data if needed
            self.create_sample_change_file()
            
            # Step 4: Simulate the processing
            print("🚀 Simulating GitHub Actions workflow...")
            if not self.process_changes():
                print("❌ Processing simulation failed!")
                return False
            
            print("=" * 60)
            print("🎉 Local testing completed successfully!")
            print("📋 Next steps:")
            print("   1. Review any generated files")
            print("   2. Commit your workflow files to trigger GitHub Actions")
            print("   3. Monitor the Actions tab in your GitHub repository")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"❌ Error during local testing: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def check_change_files(self):
        """Check for YAML change files across all namespaces."""
        # Check all available namespaces
        namespaces = commons.get_available_namespaces() if commons else ['2025']
        
        overall_result = {
            'has_changes': False,
            'yaml_files': [],
            'total_files': 0,
            'changes_dir_exists': False,
            'namespaces_checked': namespaces,
            'namespace_details': {}
        }
        
        for namespace in namespaces:
            # Check primary location using namespace
            if commons:
                changes_dir = Path(commons.get_path(namespace, 'changes_dir'))
            else:
                changes_dir = Path(f'data/{namespace}/changes')
            
            namespace_result = {
                'has_changes': False,
                'yaml_files': [],
                'total_files': 0,
                'changes_dir_exists': False,
                'primary_location': str(changes_dir),
                'namespace': namespace
            }
            
            # Check primary location (data/{namespace}/changes)
            if changes_dir.exists():
                namespace_result['changes_dir_exists'] = True
                overall_result['changes_dir_exists'] = True
                yaml_files = []
                for pattern in ['*.yaml', '*.yml']:
                    yaml_files.extend(changes_dir.glob(pattern))
                
                namespace_result['yaml_files'].extend([f.name for f in yaml_files])
                namespace_result['total_files'] += len(yaml_files)
                namespace_result['has_changes'] = len(yaml_files) > 0
                
                overall_result['yaml_files'].extend([f"{namespace}:{f.name}" for f in yaml_files])
                overall_result['total_files'] += len(yaml_files)
                if len(yaml_files) > 0:
                    overall_result['has_changes'] = True
            
            overall_result['namespace_details'][namespace] = namespace_result
        
        # Check legacy location (src/changes) for backward compatibility
        legacy_changes_dir = Path('src/changes')
        if legacy_changes_dir.exists():
            if not overall_result['changes_dir_exists']:
                overall_result['changes_dir_exists'] = True
            yaml_files = []
            for pattern in ['*.yaml', '*.yml']:
                yaml_files.extend(legacy_changes_dir.glob(pattern))
            
            # Add legacy files with a prefix to distinguish them
            overall_result['yaml_files'].extend([f"[legacy] {f.name}" for f in yaml_files])
            overall_result['total_files'] += len(yaml_files)
            if len(yaml_files) > 0:
                overall_result['has_changes'] = True
        
        return overall_result
    
    def check_database_status(self):
        """Check the status of tracking databases across all namespaces."""
        namespaces = commons.get_available_namespaces() if commons else ['2025']
        
        overall_result = {
            'db_dir_exists': False,
            'databases': [],
            'has_databases': False,
            'namespaces_checked': namespaces,
            'namespace_details': {}
        }
        
        for namespace in namespaces:
            if commons:
                db_file_path = commons.get_path(namespace, 'tracking_db')
                db_dir = Path(db_file_path).parent
            else:
                db_dir = Path(f'data/models/tracking_db/{namespace}')
                db_file_path = str(db_dir / 'tracking_db.sqlite')
            
            namespace_result = {
                'db_dir_exists': db_dir.exists(),
                'databases': [],
                'has_databases': False,
                'db_path': str(db_dir),
                'db_file_path': db_file_path,
                'namespace': namespace
            }
            
            if db_dir.exists():
                overall_result['db_dir_exists'] = True
                db_files = list(db_dir.glob('*.sqlite')) + list(db_dir.glob('*.db'))
                namespace_result['databases'] = [f.name for f in db_files]
                namespace_result['has_databases'] = len(db_files) > 0
                
                overall_result['databases'].extend([f"{namespace}:{f.name}" for f in db_files])
                if len(db_files) > 0:
                    overall_result['has_databases'] = True
            
            overall_result['namespace_details'][namespace] = namespace_result
        
        return overall_result
    
    def check_generated_files(self):
        """Check for generated files that should be committed."""
        model_dir = commons.MODEL_DIR_PATH if commons else 'src/models'
        files_to_check = [
            os.path.join(model_dir, 'generated_inserts.sql'),
            'processing_summary.json',
        ]
        
        result = {
            'generated_files': [],
            'has_generated_files': False
        }
        
        for file_path in files_to_check:
            if Path(file_path).exists():
                result['generated_files'].append(file_path)
        
        result['has_generated_files'] = len(result['generated_files']) > 0
        
        return result
    
    def check_dependencies(self):
        """Check if required dependencies and files exist."""
        model_dir = commons.MODEL_DIR_PATH if commons else 'src/models'
        required_files = [
            'requirements.txt',
            os.path.join(model_dir, 'api.py'),
            os.path.join(model_dir, 'tracking_schema.sql'),
            'src/utils/commons.py'
        ]
        
        result = {
            'missing_files': [],
            'all_dependencies_ok': True
        }
        
        for file_path in required_files:
            if not Path(file_path).exists():
                result['missing_files'].append(file_path)
        
        result['all_dependencies_ok'] = len(result['missing_files']) == 0
        
        return result
    
    def output_github_actions_variables(self, checks):
        """Output essential GitHub Actions environment variables."""
        # Only output the variables that are actually used by the workflow
        variables = {
            # Essential for workflow control
            'NEW_CHANGES': 'true' if checks['changes']['has_changes'] else 'false',
            'GENERATED_FILES': 'true' if checks['generated']['has_generated_files'] else 'false', 
            'DEPENDENCIES_OK': 'true' if checks['dependencies']['all_dependencies_ok'] else 'false'
        }
        
        # Output to GitHub Actions environment
        github_output = os.environ.get('GITHUB_OUTPUT')
        
        if github_output:
            # Running in GitHub Actions - write to output file
            with open(github_output, 'a') as f:
                for key, value in variables.items():
                    f.write(f"{key}={value}\n")
            print(f"✅ GitHub Actions variables written to {github_output}")
        else:
            # Running locally - print to console
            print("\n🔧 GitHub Actions Environment Variables:")
            for key, value in variables.items():
                print(f"{key}={value}")
            
            # Also show detailed info when running locally for debugging
            print(f"\n📊 Detailed Status:")
            print(f"   Change files: {checks['changes']['total_files']}")
            print(f"   Generated files: {len(checks['generated']['generated_files'])}")
            if checks['dependencies']['missing_files']:
                print(f"   Missing files: {', '.join(checks['dependencies']['missing_files'])}")
    
    def check_status(self):
        """Check comprehensive project status."""
        print("🔍 Running comprehensive project status check...")
        
        try:
            print(f"📁 Working directory: {self.repo_root}")
            
            # Run all checks
            checks = {
                'changes': self.check_change_files(),
                'database': self.check_database_status(),
                'generated': self.check_generated_files(),
                'dependencies': self.check_dependencies()
            }
            
            # Print detailed results
            print("\n📋 Check Results:")
            print(f"   Changes: {checks['changes']['total_files']} YAML files found")
            print(f"   Database: {len(checks['database']['databases'])} database files found")
            print(f"   Generated: {len(checks['generated']['generated_files'])} generated files found")
            print(f"   Dependencies: {'✅ OK' if checks['dependencies']['all_dependencies_ok'] else '❌ Missing files'}")
            
            if checks['dependencies']['missing_files']:
                print(f"   Missing files: {', '.join(checks['dependencies']['missing_files'])}")
            
            # Output GitHub Actions variables
            self.output_github_actions_variables(checks)
            
            # Generate summary
            summary = {
                'timestamp': str(os.popen("date").read().strip()) if os.name != 'nt' else 'timestamp',
                'repository_root': str(Path.cwd()),
                'checks': checks,
                'overall_status': 'ready' if all([
                    checks['dependencies']['all_dependencies_ok'],
                    checks['changes']['changes_dir_exists']
                ]) else 'needs_attention'
            }
            
            # Save summary to file
            with open('workflow_status.json', 'w') as f:
                json.dump(summary, f, indent=2)
            
            print(f"✅ Status summary saved to workflow_status.json")
            
            # Determine success
            if checks['dependencies']['all_dependencies_ok']:
                print("✅ All checks passed successfully!")
                return True
            else:
                print("⚠️  Some dependency issues found, but continuing...")
                return True
                
        except Exception as e:
            print(f"❌ Error during status check: {e}")
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
    python pcm_cli.py validate-setup
    python pcm_cli.py test-local
    python pcm_cli.py status
        """
    )
    
    parser.add_argument(
        'command',
        choices=['process-changes', 'validate-yaml', 'validate-setup', 'test-local', 'status', 'help'],
        help='Command to execute'
    )
    
    # Handle no arguments or help
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ['help', '--help', '-h']):
        parser.print_help()
        return 0
    
    args = parser.parse_args()
    
    # Initialize manager without namespace
    manager = PCMStatsManager()
    
    # Execute command
    success = True
    
    if args.command == 'process-changes':
        print("=" * 60)
        print(f"🤖 PCM Stats Management - Processing All Namespaces")
        print("=" * 60)
        
        success = manager.process_changes()
        
    elif args.command == 'validate-yaml':
        success = manager.validate_yaml_files()
        
    elif args.command == 'validate-setup':
        success = manager.validate_setup()
        
    elif args.command == 'test-local':
        success = manager.test_local_ci()
        
    elif args.command == 'status':
        success = manager.check_status()
        
    elif args.command == 'help':
        parser.print_help()
        return 0
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
