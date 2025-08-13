import sqlite3
import os
import yaml
from pathlib import Path
from src.utils import commons

def _find_change_file(change_dir_path):
    """
    Find change file in a directory, supporting both .yaml and .yml extensions.
    
    Args:
        change_dir_path (str): Path to the change directory
        
    Returns:
        str: Path to the change file if found, None otherwise
    """
    # Try change.yaml first, then change.yml
    for filename in ['change.yaml', 'change.yml']:
        change_file_path = os.path.join(change_dir_path, filename)
        if os.path.exists(change_file_path):
            return change_file_path
    return None

def _write_stats_yaml_with_flow_style(data, file_path):
    """
    Write stats YAML file with flow style formatting for stats dictionaries.
    
    Args:
        data (dict): The stats data to write
        file_path (str): Path to write the YAML file
    """
    # Custom YAML dumper for stats formatting
    class StatsYAMLDumper(yaml.SafeDumper):
        def represent_dict(self, data):
            # Check if this is a stats dictionary (nested inside a cyclist)
            if all(key in ['fla', 'mo', 'mm', 'dh', 'cob', 'tt', 'prl', 'spr', 'acc', 'end', 'res', 'rec', 'hil', 'att'] for key in data.keys()):
                return self.represent_mapping('tag:yaml.org,2002:map', data.items(), flow_style=True)
            else:
                return self.represent_mapping('tag:yaml.org,2002:map', data.items(), flow_style=False)
    
    # Override the dict representer
    StatsYAMLDumper.add_representer(dict, StatsYAMLDumper.represent_dict)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, Dumper=StatsYAMLDumper, default_flow_style=False, sort_keys=False, allow_unicode=True)

def init_namespace(namespace):
    """
    Initialize the directory structure for a given namespace.
    
    Args:
        namespace (str): The namespace to initialize (e.g., 'procyclingstats')
    """
    base_path = commons.get_path(namespace, 'root')
    os.makedirs(base_path, exist_ok=True)
    print(f"Initialized directory structure for namespace '{namespace}' at: {base_path}")

    base_path = commons.get_path(namespace, 'changes_dir')
    os.makedirs(base_path, exist_ok=True)

    create_new_database(namespace, 'tracking')
    
    # Check for init_cdb.sqlite file and import cyclists if it exists
    init_db_path = os.path.join(commons.get_path(namespace, 'root'), 'init_cdb.sqlite')
    if os.path.exists(init_db_path):
        print(f"🔍 Found init database file: {init_db_path}")
        print(f"📥 Importing cyclists from init database...")
        
        import_success = import_cyclists_from_db(namespace, init_db_path)
        if import_success:
            print(f"✅ Successfully imported cyclists from init database")
        else:
            print(f"❌ Failed to import cyclists from init database")
    else:
        print(f"ℹ️  No init database file found at: {init_db_path}")

def create_new_database(namespace, type='tracking'):
    """
    Create a new SQLite database with the required schema.
    
    Args:
        namespace (str): The namespace to create the database for
        type (str): Type of database schema to use (default: 'tracking')
    
    Returns:
        str: Path to the created database file
    """
    # Get the database path
    db_path = commons.get_path(namespace, 'tracking_db')
    if not os.path.exists(db_path):
        # Read schema from tracking_schema.sql
        schema_path = os.path.join(commons.MODEL_DIR_PATH, f'{type}_schema.sql')
        with open(schema_path, 'r') as schema_file:
            schema_sql = schema_file.read()
        
        # Create database and execute schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.executescript(schema_sql)
        conn.commit()
        conn.close()
        
        print(f"Tracking database created successfully at: {db_path}")
    return db_path

def get_database_connection(namespace):
    """
    Get a connection to the SQLite database for the given namespace.
    
    Args:
        namespace (str): The namespace to connect to
    
    Returns:
        sqlite3.Connection: Database connection object
    """
    db_path = commons.get_path(namespace, 'tracking_db')
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found for namespace '{namespace}': {db_path}")
    
    return sqlite3.connect(db_path)

def update_stats_file_with_changes(namespace, change_yaml_path):
    """
    Update the stats.yaml file with changes from a change file.
    
    Args:
        namespace (str): The namespace to process
        change_yaml_path (str): Path to the change.yaml file
        
    Returns:
        dict: Summary of updates made to stats file
    """
    stats_file_path = commons.get_path(namespace, 'stats_file')
    
    try:
        # Load the change data
        with open(change_yaml_path, 'r', encoding='utf-8') as f:
            change_data = yaml.safe_load(f)
        
        # Load existing stats file
        if os.path.exists(stats_file_path):
            with open(stats_file_path, 'r', encoding='utf-8') as f:
                stats_data = yaml.safe_load(f) or {}
        else:
            stats_data = {}
        
        
        updates_made = 0
        cyclists_added = 0
        stats_updated = 0
        
        # Process each stat update from the change file
        for stat_update in change_data.get('stats', []):
            pcm_id = str(stat_update.get('pcm_id'))  # Ensure pcm_id is string for YAML keys
            cyclist_name = stat_update.get('name')
            
            if not pcm_id or not cyclist_name:
                continue
            
            # Create cyclist entry if it doesn't exist
            if pcm_id not in stats_data:
                stats_data[pcm_id] = {}
                cyclists_added += 1
                print(f"  ➕ Added new cyclist: {cyclist_name} (PCM ID: {pcm_id})")
            
            # Build ordered dictionary for this cyclist
            ordered_cyclist_data = {}
            
            # 1. Name (always first)
            ordered_cyclist_data['name'] = cyclist_name
            if stats_data[pcm_id].get('name') != cyclist_name:
                if pcm_id in stats_data and 'name' in stats_data[pcm_id]:
                    print(f"  📝 Updated name for PCM ID {pcm_id}: {cyclist_name}")
            
            # 2. first_cycling_id (second if present)
            first_cycling_id = stat_update.get('first_cycling_id')
            if first_cycling_id and first_cycling_id != 'NULL':
                ordered_cyclist_data['first_cycling_id'] = first_cycling_id
                old_fc_id = stats_data[pcm_id].get('first_cycling_id')
                if old_fc_id != first_cycling_id:
                    print(f"  🆔 Updated {cyclist_name} first_cycling_id: {old_fc_id} → {first_cycling_id}")
            elif 'first_cycling_id' in stats_data.get(pcm_id, {}):
                # Preserve existing first_cycling_id if not in change
                ordered_cyclist_data['first_cycling_id'] = stats_data[pcm_id]['first_cycling_id']
            
            # 3. Stats dictionary (nested structure)
            stats_dict = {}
            
            # Get existing stats from nested structure
            existing_stats = stats_data[pcm_id].get('stats', {}) if pcm_id in stats_data else {}
            
            for stat_name in commons.STAT_KEYS:
                # Check if this stat is being updated in the change
                new_stat_value = stat_update.get(stat_name)
                old_stat_value = existing_stats.get(stat_name)
                
                if new_stat_value is not None and new_stat_value != '':
                    # Use the new value from the change
                    stats_dict[stat_name] = new_stat_value
                    if old_stat_value != new_stat_value:
                        stats_updated += 1
                        print(f"  🔄 Updated {cyclist_name} {stat_name}: {old_stat_value} → {new_stat_value}")
                elif old_stat_value is not None:
                    # Preserve existing value if not being changed
                    stats_dict[stat_name] = old_stat_value
            
            # Add stats dictionary to cyclist data
            if stats_dict:
                ordered_cyclist_data['stats'] = stats_dict
            
            # Update the cyclist data with ordered structure
            stats_data[pcm_id] = ordered_cyclist_data
            updates_made += 1
        
        # Create ordered output for the entire file
        ordered_stats_data = {}
        for pcm_id in sorted(stats_data.keys(), key=lambda x: int(x)):
            ordered_stats_data[pcm_id] = stats_data[pcm_id]
        
        # Write updated stats back to file with custom formatting
        _write_stats_yaml_with_flow_style(ordered_stats_data, stats_file_path)
        
        summary = {
            "stats_file_updated": True,
            "cyclists_processed": updates_made,
            "cyclists_added": cyclists_added,
            "stats_updated": stats_updated,
            "stats_file_path": stats_file_path
        }
        
        if updates_made > 0:
            print(f"  ✅ Updated stats file: {stats_file_path}")
            print(f"     - Cyclists processed: {updates_made}")
            print(f"     - New cyclists added: {cyclists_added}")
            print(f"     - Individual stats updated: {stats_updated}")
        
        return summary
        
    except Exception as e:
        print(f"❌ Error updating stats file: {e}")
        return {
            "stats_file_updated": False,
            "error": str(e),
            "cyclists_processed": 0,
            "cyclists_added": 0,
            "stats_updated": 0
        }

def process_new_change_files(namespace):
    """
    Process new change YAML files and generate SQL INSERT statements.
    Each change is in its own directory with 'change.yaml' and generates 'inserts.sql'.
    Also updates the stats.yaml file with the changes.
    
    Args:
        namespace (str): The namespace to process changes for
    
    Returns:
        dict: Summary of processed files and changes
    """
    changes_dir = commons.get_path(namespace, 'changes_dir')

    conn = get_database_connection(namespace)
    cursor = conn.cursor()
    
    try:
        # Get existing change directory names from database 
        cursor.execute("SELECT name FROM tbl_changes")
        existing_changes = {row[0] for row in cursor.fetchall()}
        
        # Get all change directories (subdirectories in changes/)
        if not os.path.exists(changes_dir):
            return {
                "processed_files": 0,
                "new_changes": 0,
                "skipped_files": 0,
                "output_file": None,
                "stat_changes": {}
            }
        
        change_directories = [d for d in os.listdir(changes_dir) 
                            if os.path.isdir(os.path.join(changes_dir, d))]
        
        # Find new change directories that haven't been processed
        new_change_dirs = [d for d in change_directories if d not in existing_changes]
        
        processed_files = 0
        total_new_changes = 0
        total_sql_files_generated = 0
        all_stat_changes = {}
        
        for change_dir_name in new_change_dirs:
            change_dir_path = os.path.join(changes_dir, change_dir_name)
            change_yaml_path = _find_change_file(change_dir_path)
            inserts_sql_path = os.path.join(change_dir_path, 'inserts.sql')
            
            # Check if change file exists in this directory
            if not change_yaml_path:
                print(f"⚠️  Skipping {change_dir_name}: No change.yaml or change.yml file found")
                continue
                
            # Generate SQL for this change
            step1_sql, step2_sql, changes_count = _generate_sql_for_change_file(cursor, change_dir_name, change_yaml_path)
            if changes_count >= 0:
                # Write single SQL file with all statements
                inserts_sql_path = os.path.join(change_dir_path, 'inserts.sql')
                with open(inserts_sql_path, 'w', encoding='utf-8') as f:
                    f.write(f"-- Generated SQL INSERT statements for {change_dir_name}\n")
                    f.write("-- Review before executing\n\n")
                    
                    # Write Step 1 statements (tbl_changes and tbl_cyclists)
                    if step1_sql:
                        f.write("-- Step 1: tbl_changes and tbl_cyclists\n")
                        for sql in step1_sql:
                            f.write(sql + ";\n")
                        f.write("\n")
                    
                    # Write Step 2 statements (tbl_change_stat_history)
                    if step2_sql:
                        f.write("-- Step 2: tbl_change_stat_history\n")
                        for sql in step2_sql:
                            f.write(sql + ";\n")
                
                # Update the stats.yaml file with the changes
                print(f"🔄 Updating stats file for {change_dir_name}...")
                stats_update_summary = update_stats_file_with_changes(namespace, change_yaml_path)
                all_stat_changes[change_dir_name] = stats_update_summary
                
                processed_files += 1
                total_new_changes += changes_count
                total_sql_files_generated += 1
                print(f"✅ Generated {inserts_sql_path} with {changes_count} changes")
        
        summary = {
            "processed_files": processed_files,
            "new_changes": total_new_changes,
            "skipped_files": len(change_directories) - processed_files,
            "sql_files_generated": total_sql_files_generated,
            "stat_changes": all_stat_changes
        }
        
        print(f"SQL generation complete: {summary}")
        return summary
        
    except Exception as e:
        print(f"Error processing change files: {e}")
        raise
    finally:
        conn.close()

def _generate_sql_for_change_file(cursor, change_dir_name, change_yaml_path):
    """
    Generate SQL INSERT statements for a single change file.
    Creates statements for tbl_changes, tbl_cyclists, and tbl_change_stat_history.
    
    Args:
        cursor: SQLite cursor
        change_dir_name (str): Name of the change directory (used as identifier)
        change_yaml_path (str): Full path to the change.yaml file
    
    Returns:
        tuple: (list of SQL statements for basic tables, list of SQL statements for stat history, number of changes), (-1) on error
    """
    try:
        with open(change_yaml_path, 'r', encoding='utf-8') as f:
            change_data = yaml.safe_load(f)
        
        # Validate required fields (name is not required since we use directory name)
        if not all(key in change_data for key in ['date', 'stats']):
            print(f"Skipping {change_dir_name}: Missing required fields (date, stats)")
            return [], [], -1
        
        step1_statements = []  # tbl_changes and tbl_cyclists
        step2_statements = []  # tbl_change_stat_history
        
        # Step 1: Generate INSERT for tbl_changes (using change_dir_name as the name)
        step1_statements.append(f"""INSERT INTO tbl_changes (name, description, author, date)
VALUES ('{change_dir_name}', '{change_data.get('description', '')}', '{change_data.get('author', 'Unknown')}', '{change_data['date']}')""")
        
        changes_inserted = 0
        
        # Step 1: Generate cyclist INSERTs
        processed_cyclists = set()  # Track cyclists to avoid duplicates
        
        for stat_update in change_data['stats']:
            pcm_id = stat_update.get('pcm_id')
            cyclist_name = stat_update.get('name')
            
            if not pcm_id or not cyclist_name:
                continue
            
            # Generate cyclist INSERT if not exists and not already processed
            if pcm_id not in processed_cyclists:
                cyclist_sql = _generate_cyclist_insert_if_not_exists(cursor, pcm_id, cyclist_name, stat_update)
                if cyclist_sql:
                    step1_statements.append(cyclist_sql)
                processed_cyclists.add(pcm_id)
        
        # Step 2: Generate stat change INSERTs
        for stat_update in change_data['stats']:
            pcm_id = stat_update.get('pcm_id')
            cyclist_name = stat_update.get('name')
            
            if not pcm_id or not cyclist_name:
                continue
            
            # Generate stat change INSERTs using subqueries for foreign keys and version
            for stat_name in commons.STAT_KEYS:
                stat_value = stat_update.get(stat_name)
                
                if stat_value is None or stat_value == '':
                    continue
                
                # Check if this stat value is different from the latest version
                if _should_insert_stat_change(cursor, pcm_id, stat_name, stat_value):
                    step2_statements.append(f"""INSERT INTO tbl_change_stat_history (cyclist_id, change_id, stat_name, stat_value, version)
VALUES (
    (SELECT id FROM tbl_cyclists WHERE pcm_id = '{pcm_id}'),
    (SELECT id FROM tbl_changes WHERE name = '{change_dir_name}'),
    '{stat_name}',
    {stat_value},
    COALESCE(
        (SELECT MAX(version) + 1 
         FROM tbl_change_stat_history csh 
         JOIN tbl_cyclists c ON csh.cyclist_id = c.id 
         WHERE c.pcm_id = '{pcm_id}' AND csh.stat_name = '{stat_name}'), 
        1
    )
)""")
                    
                    changes_inserted += 1
        
        return step1_statements, step2_statements, changes_inserted
        
    except Exception as e:
        print(f"Error processing change {change_dir_name}: {e}")
        return [], [], -1

def _generate_cyclist_insert_if_not_exists(cursor, pcm_id, name, stat_update):
    """Generate cyclist INSERT SQL if they don't exist in the database."""
    cursor.execute("SELECT pcm_id FROM tbl_cyclists WHERE pcm_id = ?", (pcm_id,))
    if not cursor.fetchone():
        first_cycling_id = stat_update.get('first_cycling_id', 'NULL')
        first_cycling_id_sql = f"'{first_cycling_id}'" if first_cycling_id != 'NULL' else 'NULL'
        return f"""
INSERT INTO tbl_cyclists (pcm_id, name, first_cycling_id)
VALUES ('{pcm_id}', '{name}', {first_cycling_id_sql})"""
    return None

def _should_insert_stat_change(cursor, pcm_id, stat_name, new_value):
    """Check if the new stat value is different from the latest version."""
    cursor.execute("""
        SELECT csh.stat_value 
        FROM tbl_change_stat_history csh 
        JOIN tbl_cyclists c ON csh.cyclist_id = c.id 
        WHERE c.pcm_id = ? AND csh.stat_name = ?
        ORDER BY csh.version DESC LIMIT 1
    """, (pcm_id, stat_name))
    
    result = cursor.fetchone()
    return result is None or result[0] != new_value

def process_namespace(namespace):
    """
    Process changes for a single namespace.
    
    Args:
        namespace (str): The namespace to process
        
    Returns:
        dict: Summary of processing results for this namespace
    """
    print(f"🔄 Processing namespace: {namespace}")
    print("-" * 40)
    
    try:
        init_namespace(namespace)

        # Process changes for this namespace
        summary = process_new_change_files(namespace)
        
        # Determine success status
        success = summary.get("processed_files", 0) >= 0  # Even 0 processed files is success
        
        if success:
            print(f"✅ Successfully processed namespace: {namespace}")
            print(f"   - Files processed: {summary.get('processed_files', 0)}")
            print(f"   - New changes: {summary.get('new_changes', 0)}")
            print(f"   - Files skipped: {summary.get('skipped_files', 0)}")
            print(f"   - SQL files generated: {summary.get('sql_files_generated', 0)}")
        else:
            print(f"❌ Processing failed for namespace: {namespace}")
        
        # Return enhanced summary with success status
        return {
            **summary,
            "namespace": namespace,
            "success": success,
            "error": None
        }
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error processing namespace {namespace}: {error_msg}")
        
        # Return error summary
        return {
            "namespace": namespace,
            "processed_files": 0,
            "new_changes": 0,
            "skipped_files": 0,
            "success": False,
            "error": error_msg
        }
    finally:
        print()  # Add spacing between namespaces

def process_all_namespaces():
    """
    Process changes for all available namespaces automatically.
    
    Returns:
        dict: Summary of processing results for all namespaces
    """
    # Get all available namespaces
    namespaces = commons.get_available_namespaces()
    
    if not namespaces:
        print("⚠️  No namespaces found in the data directory")
        return {
            "processed_namespaces": 0,
            "successful_namespaces": [],
            "failed_namespaces": [],
            "total_changes": 0,
            "overall_success": True
        }
    
    print(f"Found {len(namespaces)} namespace(s): {', '.join(namespaces)}")
    print()
    
    overall_summary = {
        "processed_namespaces": 0,
        "successful_namespaces": [],
        "failed_namespaces": [],
        "namespace_details": {},
        "total_changes": 0,
        "overall_success": True
    }
    
    for namespace in namespaces:
        namespace_result = process_namespace(namespace)
        overall_summary['processed_namespaces'] += 1
        overall_summary['namespace_details'][namespace] = namespace_result
        overall_summary['total_changes'] += namespace_result.get('new_changes', 0)
        
        if namespace_result['success']:
            overall_summary['successful_namespaces'].append(namespace)
        else:
            overall_summary['failed_namespaces'].append(namespace)
            overall_summary['overall_success'] = False
    
    # Final summary
    print("=" * 60)
    print(f"📊 Processing Summary:")
    print(f"   - Total namespaces: {len(namespaces)}")
    print(f"   - Successfully processed: {len(overall_summary['successful_namespaces'])}")
    print(f"   - Failed: {len(overall_summary['failed_namespaces'])}")
    print(f"   - Total new changes: {overall_summary['total_changes']}")
    
    if overall_summary["overall_success"]:
        print("✅ All namespaces processed successfully")
    else:
        print("❌ One or more namespaces had issues")
        if overall_summary["failed_namespaces"]:
            print(f"   Failed namespaces: {', '.join(overall_summary['failed_namespaces'])}")
    
    print("=" * 60)
    
    return overall_summary


# =============================================================================
# YAML Validation Functions
# =============================================================================

def validate_yaml_syntax(file_path):
    """Validate that a YAML file has correct syntax."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            yaml.safe_load(f)
        return True, None
    except yaml.YAMLError as e:
        return False, f"YAML syntax error: {e}"
    except Exception as e:
        return False, f"File error: {e}"

def validate_required_fields_change_file(data):
    """Validate that required fields are present in a change file YAML data."""
    # Check for 'author'
    # 'date' and 'stats' are always required
    required_fields = ['date', 'stats']
    missing_fields = [field for field in required_fields if field not in data]
    
    # Check that 'author' is present
    if 'author' not in data:
        missing_fields.append('author')
    
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

def validate_required_fields_stats_file(data):
    """Validate that required fields are present in a stats file YAML data with new nested structure."""
    if not isinstance(data, dict):
        return False, "Stats file must be a dictionary with cyclist IDs as keys"
    
    if len(data) == 0:
        return False, "Stats file cannot be empty"
    
    # Validate each cyclist entry
    for cyclist_id, cyclist_data in data.items():
        if not isinstance(cyclist_data, dict):
            return False, f"Cyclist {cyclist_id} data must be a dictionary"
        
        # Required fields for new schema
        required_fields = ['name']
        missing_fields = [field for field in required_fields if field not in cyclist_data]
        
        if missing_fields:
            return False, f"Cyclist {cyclist_id} missing required fields: {', '.join(missing_fields)}"
        
        # Validate that cyclist ID is numeric (can be string or int)
        try:
            int(cyclist_id)
        except ValueError:
            return False, f"Cyclist ID '{cyclist_id}' must be numeric"
        
        # Validate stats structure if present
        if 'stats' in cyclist_data:
            if not isinstance(cyclist_data['stats'], dict):
                return False, f"Cyclist {cyclist_id} 'stats' must be a dictionary"
            
            # Validate stat keys and values
            for stat_key, stat_value in cyclist_data['stats'].items():
                if stat_key not in commons.STAT_KEYS:
                    return False, f"Cyclist {cyclist_id} has invalid stat key: {stat_key}"
                
                if not isinstance(stat_value, (int, float)):
                    return False, f"Cyclist {cyclist_id} stat '{stat_key}' must be numeric, got: {type(stat_value).__name__}"
        
        # Validate first_cycling_id if present
        if 'first_cycling_id' in cyclist_data:
            if not isinstance(cyclist_data['first_cycling_id'], (int, str)):
                return False, f"Cyclist {cyclist_id} 'first_cycling_id' must be numeric"
    
    return True, None

def detect_yaml_file_type(file_path):
    """Detect whether this is a change file or stats file based on structure."""
    file_path = Path(file_path)
    if file_path.is_file() and file_path.name.lower() in ['change.yaml', 'change.yml']:
        return 'change_file'
    elif file_path.is_file() and file_path.name.lower() == 'stats.yaml':
        return 'stats_file'
    return 'unknown'

def validate_single_yaml_file(file_path):
    """Validate a single YAML file (either change file or stats file)."""
    # First validate YAML syntax
    is_valid, error = validate_yaml_syntax(file_path)
    if not is_valid:
        return False, error
    
    # Load and validate structure
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Detect file type
        file_type = detect_yaml_file_type(file_path)
        
        if file_type == 'change_file':
            is_valid, error = validate_required_fields_change_file(data)
            if not is_valid:
                return False, f"Change file validation error: {error}"
        elif file_type == 'stats_file':
            is_valid, error = validate_required_fields_stats_file(data)
            if not is_valid:
                return False, f"Stats file validation error: {error}"
        else:
            return False, "Unknown file type - does not match change file or stats file structure"
        
        return True, None
        
    except Exception as e:
        return False, f"Validation error: {e}"

def validate_change_files():
    """Validate all change.yaml files across all namespaces."""
    print(f"📋 Validating change files for all namespaces...")
    
    try:
        all_change_files = []
        validation_errors = []
        
        # Get all available namespaces
        namespaces = commons.get_available_namespaces()
        
        for namespace in namespaces:
            print(f"🔍 Checking change files in namespace: {namespace}")
            
            # Check change files using namespace
            changes_dir = Path(commons.get_path(namespace, 'changes_dir'))
            
            if changes_dir.exists():
                # Look for change directories containing change.yaml or change.yml files
                change_directories = [d for d in changes_dir.iterdir() if d.is_dir()]
                change_files = []
                
                for change_dir in change_directories:
                    # Try both extensions
                    for filename in ['change.yaml', 'change.yml']:
                        change_file = change_dir / filename
                        if change_file.exists():
                            change_files.append(change_file)
                            break  # Only add one file per directory
                
                all_change_files.extend([(f, f'change-{namespace}') for f in change_files])
                print(f"🔍 Found {len(change_files)} change files in {changes_dir}")
            else:
                print(f"ℹ️  Changes directory not found: {changes_dir}")
        
        if not all_change_files:
            print("ℹ️  No change files found to validate")
            return True
        
        print(f"🔍 Total {len(all_change_files)} change files to validate")
        
        # Validate each change file
        for yaml_file, file_category in all_change_files:
            is_valid, error = validate_single_yaml_file(yaml_file)
            
            if is_valid:
                print(f"✅ {yaml_file.parent.name}/{yaml_file.name} ({file_category}): Valid")
            else:
                print(f"❌ {yaml_file.parent.name}/{yaml_file.name} ({file_category}): {error}")
                validation_errors.append((f"{yaml_file.parent.name}/{yaml_file.name}", error))
        
        # Summary
        if validation_errors:
            print(f"\n❌ Change file validation failed for {len(validation_errors)} files:")
            for filename, error in validation_errors:
                print(f"   - {filename}: {error}")
            return False
        else:
            print(f"\n✅ All {len(all_change_files)} change files passed validation!")
            return True
            
    except Exception as e:
        print(f"❌ Error during change file validation: {e}")
        import traceback
        traceback.print_exc()
        return False

def validate_stats_files():
    """Validate all stats.yaml files across all namespaces."""
    print(f"📋 Validating stats files for all namespaces...")
    
    try:
        all_stats_files = []
        validation_errors = []
        
        # Get all available namespaces
        namespaces = commons.get_available_namespaces()
        
        for namespace in namespaces:
            print(f"🔍 Checking stats file in namespace: {namespace}")
            
            # Check stats file using namespace
            stats_file = Path(commons.get_path(namespace, 'stats_file'))
                
            if stats_file.exists():
                all_stats_files.append((stats_file, f'stats-{namespace}'))
                print(f"🔍 Found stats file: {stats_file}")
            else:
                print(f"ℹ️  Stats file not found: {stats_file}")
        
        if not all_stats_files:
            print("ℹ️  No stats files found to validate")
            return True
        
        print(f"🔍 Total {len(all_stats_files)} stats files to validate")
        
        # Validate each stats file
        for yaml_file, file_category in all_stats_files:
            is_valid, error = validate_single_yaml_file(yaml_file)
            
            if is_valid:
                print(f"✅ {yaml_file.name} ({file_category}): Valid")
            else:
                print(f"❌ {yaml_file.name} ({file_category}): {error}")
                validation_errors.append((yaml_file.name, error))
        
        # Summary
        if validation_errors:
            print(f"\n❌ Stats file validation failed for {len(validation_errors)} files:")
            for filename, error in validation_errors:
                print(f"   - {filename}: {error}")
            return False
        else:
            print(f"\n✅ All {len(all_stats_files)} stats files passed validation!")
            return True
            
    except Exception as e:
        print(f"❌ Error during stats file validation: {e}")
        import traceback
        traceback.print_exc()
        return False

def validate_yaml_files():
    """Validate all YAML files (both change files and stats files)."""
    print("🔍 Starting comprehensive YAML validation...")
    
    # Validate change files
    change_files_valid = validate_change_files()
    print()  # Add spacing
    
    # Validate stats files
    stats_files_valid = validate_stats_files()
    
    # Overall summary
    if change_files_valid and stats_files_valid:
        print("\n🎉 All YAML files passed validation!")
        return True
    else:
        print("\n❌ Some YAML files failed validation!")
        return False


# =============================================================================
# Database Import Functions
# =============================================================================

def import_cyclists_from_db(namespace, db_file):
    """
    Import cyclist data from SQLite database DYN_cyclist table to create stats.yaml file.
    
    Args:
        namespace (str): The namespace to create stats file for
        db_file (str): Path to the SQLite database file
        
    Returns:
        bool: True if successful, False otherwise
    """
    import sqlite3
    import os
    
    # Column mapping from database to stats.yaml
    STAT_COLUMN_MAPPING = {
        'fla': 'charac_i_plain',
        'mo': 'charac_i_mountain', 
        'mm': 'charac_i_medium_mountain',
        'dh': 'charac_i_downhilling',
        'cob': 'charac_i_cobble',
        'tt': 'charac_i_timetrial',
        'prl': 'charac_i_prologue',
        'spr': 'charac_i_sprint',
        'acc': 'charac_i_acceleration',
        'end': 'charac_i_endurance',
        'res': 'charac_i_resistance',
        'rec': 'charac_i_recuperation',
        'hil': 'charac_i_hill',
        'att': 'charac_i_baroudeur'
    }
    
    try:
        # Check if database file exists
        if not os.path.exists(db_file):
            print(f"❌ Database file not found: {db_file}")
            return False
        
        print(f"📂 Reading database file: {db_file}")
        
        # Connect to database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Check if DYN_cyclist table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='DYN_cyclist'")
        if not cursor.fetchone():
            print("❌ Table 'DYN_cyclist' not found in database")
            conn.close()
            return False
        
        # Get table schema to verify columns exist
        cursor.execute("PRAGMA table_info(DYN_cyclist)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Check required columns exist
        required_columns = [
            'IDcyclist', 'gene_sz_lastname', 'gene_sz_firstname', 
            'value_f_current_ability'
        ] + list(STAT_COLUMN_MAPPING.values())
        
        missing_columns = [col for col in required_columns if col not in columns]
        if missing_columns:
            print(f"❌ Missing required columns in DYN_cyclist table: {missing_columns}")
            conn.close()
            return False
        
        # Build SELECT query
        select_columns = [
            'IDcyclist',
            'gene_sz_lastname', 
            'gene_sz_firstname',
            'value_f_current_ability'
        ] + list(STAT_COLUMN_MAPPING.values())
        
        query = f"SELECT {', '.join(select_columns)} FROM DYN_cyclist"
        print(f"🔍 Executing query: {query}")
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        if not rows:
            print("⚠️  No cyclist data found in DYN_cyclist table")
            conn.close()
            return False
        
        print(f"📊 Found {len(rows)} cyclists in database")
        
        # Build stats data structure
        stats_data = {}
        
        for row in rows:
            cyclist_id = str(row[0])  # IDcyclist as string for YAML keys
            lastname = row[1] or ""
            firstname = row[2] or ""
            first_cycling_id = row[3]
            
            # Combine first and last name
            full_name = f"{firstname} {lastname}".strip()
            if not full_name:
                full_name = f"Cyclist {cyclist_id}"
            
            # Create cyclist entry with new nested structure
            cyclist_data = {
                'name': full_name
            }
            
            # Add first_cycling_id if present
            if first_cycling_id is not None and first_cycling_id != '':
                cyclist_data['first_cycling_id'] = int(first_cycling_id)
            
            # Create stats dictionary
            stats_dict = {}
            stat_values = row[4:]  # The stat columns start at index 4
            for i, stat_key in enumerate(commons.STAT_KEYS):
                if i < len(stat_values) and stat_values[i] is not None:
                    stats_dict[stat_key] = stat_values[i]
            
            # Add stats as nested dictionary
            if stats_dict:
                cyclist_data['stats'] = stats_dict
            
            stats_data[cyclist_id] = cyclist_data
        
        conn.close()
        
        # Create ordered output (sort by cyclist ID numerically)
        ordered_stats_data = {}
        for cyclist_id in sorted(stats_data.keys(), key=lambda x: int(x)):
            ordered_stats_data[cyclist_id] = stats_data[cyclist_id]
        
        # Ensure namespace directory exists
        namespace_dir = commons.get_path(namespace, 'root')
        os.makedirs(namespace_dir, exist_ok=True)
        
        # Write stats.yaml file with custom formatting
        stats_file_path = commons.get_path(namespace, 'stats_file')
        
        print(f"💾 Writing stats file: {stats_file_path}")
        
        _write_stats_yaml_with_flow_style(ordered_stats_data, stats_file_path)
        
        print(f"✅ Successfully imported {len(ordered_stats_data)} cyclists to {stats_file_path}")
        print(f"   - Namespace: {namespace}")
        print(f"   - Source: {db_file}")
        print(f"   - Cyclists: {len(ordered_stats_data)}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error importing from database: {e}")
        import traceback
        traceback.print_exc()
        return False


# =============================================================================
# UAT Branch Processing Functions
# =============================================================================

def process_uat_changes():
    """
    Process UAT changes for all namespaces by executing SQL inserts and exporting tracking data.
    
    This function:
    1. Reads tracking_db.sqlite for each namespace
    2. Compares tbl_changes with change directories  
    3. Sorts new changes alphanumerically (highest processed last)
    4. Executes inserts.sql for each new change
    5. Exports vw_tracking_export to tracking_export.csv
    
    Returns:
        dict: Summary of UAT processing results for all namespaces
    """
    # Get all available namespaces
    namespaces = commons.get_available_namespaces()
    
    if not namespaces:
        print("⚠️  No namespaces found in the data directory")
        return {
            "processed_namespaces": 0,
            "successful_namespaces": [],
            "failed_namespaces": [],
            "total_changes_executed": 0,
            "overall_success": True
        }
    
    print(f"Found {len(namespaces)} namespace(s): {', '.join(namespaces)}")
    print()
    
    overall_summary = {
        "processed_namespaces": 0,
        "successful_namespaces": [],
        "failed_namespaces": [],
        "namespace_details": {},
        "total_changes_executed": 0,
        "overall_success": True
    }
    
    for namespace in namespaces:
        namespace_result = process_uat_namespace(namespace)
        overall_summary['processed_namespaces'] += 1
        overall_summary['namespace_details'][namespace] = namespace_result
        overall_summary['total_changes_executed'] += namespace_result.get('changes_executed', 0)
        
        if namespace_result['success']:
            overall_summary['successful_namespaces'].append(namespace)
        else:
            overall_summary['failed_namespaces'].append(namespace)
            overall_summary['overall_success'] = False
    
    # Final summary
    print("=" * 60)
    print(f"📊 UAT Processing Summary:")
    print(f"   - Total namespaces: {len(namespaces)}")
    print(f"   - Successfully processed: {len(overall_summary['successful_namespaces'])}")
    print(f"   - Failed: {len(overall_summary['failed_namespaces'])}")
    print(f"   - Total changes executed: {overall_summary['total_changes_executed']}")
    
    if overall_summary["overall_success"]:
        print("✅ All namespaces processed successfully")
    else:
        print("❌ One or more namespaces had issues")
        if overall_summary["failed_namespaces"]:
            print(f"   Failed namespaces: {', '.join(overall_summary['failed_namespaces'])}")
    
    print("=" * 60)
    
    return overall_summary

def process_uat_namespace(namespace):
    """
    Process UAT changes for a single namespace.
    
    Args:
        namespace (str): The namespace to process
        
    Returns:
        dict: Summary of UAT processing results for this namespace
    """
    print(f"🔄 Processing UAT namespace: {namespace}")
    print("-" * 40)
    
    try:
        # Check if tracking database exists
        db_path = commons.get_path(namespace, 'tracking_db')
        if not os.path.exists(db_path):
            print(f"❌ Tracking database not found for namespace: {namespace}")
            return {
                "namespace": namespace,
                "success": False,
                "error": f"Tracking database not found: {db_path}",
                "changes_executed": 0,
                "export_created": False
            }
        
        print(f"📊 Using tracking database: {db_path}")
        
        # Get connection to tracking database
        conn = get_database_connection(namespace)
        cursor = conn.cursor()
        
        try:
            # Get existing changes from database
            cursor.execute("SELECT name FROM tbl_changes")
            existing_changes = {row[0] for row in cursor.fetchall()}
            print(f"📋 Found {len(existing_changes)} existing changes in database")
            
            # Get all change directories
            changes_dir = commons.get_path(namespace, 'changes_dir')
            
            if not os.path.exists(changes_dir):
                print(f"⚠️  Changes directory not found: {changes_dir}")
                change_directories = []
            else:
                change_directories = [d for d in os.listdir(changes_dir) 
                                    if os.path.isdir(os.path.join(changes_dir, d))]
                print(f"📁 Found {len(change_directories)} change directories")
            
            # Find new change directories that haven't been processed
            new_change_dirs = [d for d in change_directories if d not in existing_changes]
            
            # Sort alphanumerically (highest value processed last)
            new_change_dirs.sort()
            
            print(f"🆕 Found {len(new_change_dirs)} new changes to process")
            if new_change_dirs:
                print(f"   - Changes: {', '.join(new_change_dirs)}")
            
            changes_executed = 0
            
            # Process each new change directory
            for change_dir_name in new_change_dirs:
                change_dir_path = os.path.join(changes_dir, change_dir_name)
                inserts_sql_path = os.path.join(change_dir_path, 'inserts.sql')
                
                # Check if SQL file exists
                if not os.path.exists(inserts_sql_path):
                    print(f"⚠️  Skipping {change_dir_name}: No inserts.sql file found")
                    continue
                
                print(f"⚡ Executing SQL for change: {change_dir_name}")
                
                # Execute SQL statements
                try:
                    print(f"   📋 Executing SQL statements")
                    with open(inserts_sql_path, 'r', encoding='utf-8') as f:
                        sql_content = f.read()
                    
                    # Split by semicolon, handling multi-line statements properly
                    # Remove comments first, then split and clean
                    lines = sql_content.split('\n')
                    cleaned_lines = []
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('--'):
                            cleaned_lines.append(line)
                    
                    # Join lines and split by semicolon
                    cleaned_sql = ' '.join(cleaned_lines)
                    sql_statements = [stmt.strip() for stmt in cleaned_sql.split(';') if stmt.strip()]
                    
                    print(f"   🔧 Executing {len(sql_statements)} SQL statements")
                    for sql_statement in sql_statements:
                        if sql_statement:
                            cursor.execute(sql_statement)
                    
                    conn.commit()
                    changes_executed += 1
                    print(f"   ✅ Successfully executed all SQL for {change_dir_name}")
                    
                except Exception as e:
                    print(f"   ❌ Error executing SQL for {change_dir_name}: {e}")
                    conn.rollback()
                    continue
            
            # Export tracking data to CSV
            conn.commit()
            cursor = conn.cursor()
            export_success = export_tracking_data(namespace, cursor)
            
            # Final summary for this namespace
            summary = {
                "namespace": namespace,
                "success": True,
                "error": None,
                "changes_executed": changes_executed,
                "export_created": export_success,
                "total_changes_found": len(change_directories),
                "new_changes_found": len(new_change_dirs)
            }
            
            print(f"✅ Successfully processed namespace: {namespace}")
            print(f"   - Changes executed: {changes_executed}")
            print(f"   - Export created: {'Yes' if export_success else 'No'}")
            
            return summary
            
        finally:
            conn.close()
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error processing UAT namespace {namespace}: {error_msg}")
        
        return {
            "namespace": namespace,
            "success": False,
            "error": error_msg,
            "changes_executed": 0,
            "export_created": False
        }
    finally:
        print()  # Add spacing between namespaces

def export_tracking_data(namespace, cursor):
    """
    Export tracking data from vw_tracking_export view to CSV file.
    
    Args:
        namespace (str): The namespace to export data for
        cursor: SQLite cursor connected to tracking database
        
    Returns:
        bool: True if export was successful, False otherwise
    """
    try:
        import csv
        
        # Export path
        namespace_dir = commons.get_path(namespace, 'root')
        export_path = os.path.join(namespace_dir, 'tracking_export.csv')
        
        print(f"📤 Exporting tracking data to: {export_path}")
        
        # Query the tracking export view
        cursor.execute("SELECT * FROM vw_tracking_export")
        rows = cursor.fetchall()
        
        if not rows:
            print("⚠️  No data found in tracking export view")
            return False
        
        # Get column names
        cursor.execute("PRAGMA table_info(vw_tracking_export)")
        # For a view, we need to get column names differently
        cursor.execute("SELECT * FROM vw_tracking_export LIMIT 0")
        column_names = [description[0] for description in cursor.description]
        
        # Write CSV file
        with open(export_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(column_names)
            
            # Write data rows
            writer.writerows(rows)
        
        print(f"✅ Successfully exported {len(rows)} rows to CSV")
        return True
        
    except Exception as e:
        print(f"❌ Error exporting tracking data: {e}")
        return False
