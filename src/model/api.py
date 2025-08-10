import sqlite3
import os
import yaml
from src.utils import commons

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

def process_new_change_files(namespace):
    """
    Process new change YAML files and generate SQL INSERT statements.
    Each change is in its own directory with 'change.yaml' and generates 'inserts.sql'.
    
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
                "output_file": None
            }
        
        change_directories = [d for d in os.listdir(changes_dir) 
                            if os.path.isdir(os.path.join(changes_dir, d))]
        
        # Find new change directories that haven't been processed
        new_change_dirs = [d for d in change_directories if d not in existing_changes]
        
        processed_files = 0
        total_new_changes = 0
        total_sql_files_generated = 0
        
        for change_dir_name in new_change_dirs:
            change_dir_path = os.path.join(changes_dir, change_dir_name)
            change_yaml_path = os.path.join(change_dir_path, 'change.yaml')
            inserts_sql_path = os.path.join(change_dir_path, 'inserts.sql')
            
            # Check if change.yaml exists in this directory
            if not os.path.exists(change_yaml_path):
                print(f"⚠️  Skipping {change_dir_name}: No change.yaml file found")
                continue
                
            # Generate SQL for this change
            file_sql, changes_count = _generate_sql_for_change_file(cursor, change_dir_name, change_yaml_path)
            if changes_count >= 0:
                # Write SQL statements to the change directory's inserts.sql file
                with open(inserts_sql_path, 'w') as f:
                    f.write(f"-- Generated SQL INSERT statements for {change_dir_name}\n")
                    f.write("-- Review before executing\n\n")
                    for sql in file_sql:
                        f.write(sql + ";\n")
                
                # Mark this change as processed in the database (just the tbl_changes entry)
                # This prevents regenerating the same SQL files repeatedly
                try:
                    with open(change_yaml_path, 'r') as f:
                        change_data = yaml.safe_load(f)
                    
                    cursor.execute("""
                        INSERT INTO tbl_changes (name, description, author, date)
                        VALUES (?, ?, ?, ?)
                    """, (change_dir_name,
                          change_data.get('description', ''), 
                          change_data.get('author', 'Unknown'), 
                          change_data.get('date', 'Unknown')))
                    conn.commit()
                    
                except Exception as e:
                    print(f"⚠️  Warning: Could not mark {change_dir_name} as processed: {e}")
                
                processed_files += 1
                total_new_changes += changes_count
                total_sql_files_generated += 1
                print(f"✅ Generated {inserts_sql_path} with {changes_count} changes")
        
        summary = {
            "processed_files": processed_files,
            "new_changes": total_new_changes,
            "skipped_files": len(change_directories) - processed_files,
            "sql_files_generated": total_sql_files_generated
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
    
    Args:
        cursor: SQLite cursor
        change_dir_name (str): Name of the change directory (used as identifier)
        change_yaml_path (str): Full path to the change.yaml file
    
    Returns:
        tuple: (list of SQL statements, number of changes), (-1) on error
    """
    try:
        with open(change_yaml_path, 'r') as f:
            change_data = yaml.safe_load(f)
        
        # Validate required fields (name is not required since we use directory name)
        if not all(key in change_data for key in ['date', 'stats']):
            print(f"Skipping {change_dir_name}: Missing required fields (date, stats)")
            return [], -1
        
        sql_statements = []
        
        # Generate INSERT for tbl_changes (using change_dir_name as the name)
        sql_statements.append(f"""INSERT INTO tbl_changes (name, description, author, date)
VALUES ('{change_dir_name}', '{change_data.get('description', '')}', '{change_data.get('author', 'Unknown')}', '{change_data['date']}')""")
        
        changes_inserted = 0
        
        for stat_update in change_data['stats']:
            pcm_id = stat_update.get('pcm_id')
            cyclist_name = stat_update.get('name')
            
            if not pcm_id or not cyclist_name:
                continue
            
            # Generate cyclist INSERT if not exists
            cyclist_sql = _generate_cyclist_insert_if_not_exists(cursor, pcm_id, cyclist_name, stat_update)
            if cyclist_sql:
                sql_statements.append(cyclist_sql)
            
            # Generate stat change INSERTs using subqueries for foreign keys and version
            for stat_name in commons.STAT_KEYS:
                stat_value = stat_update.get(stat_name)
                
                if stat_value is None or stat_value == '':
                    continue
                
                # Check if this stat value is different from the latest version
                if _should_insert_stat_change(cursor, pcm_id, stat_name, stat_value):
                    sql_statements.append(f"""INSERT INTO tbl_change_stat_history (cyclist_id, change_id, stat_name, stat_value, version)
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
        
        return sql_statements, changes_inserted
        
    except Exception as e:
        print(f"Error processing change {change_dir_name}: {e}")
        return [], -1

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

def _get_next_version(cursor, pcm_id, stat_name):
    """Get the next version number for a cyclist's stat."""
    cursor.execute("""
        SELECT MAX(version) FROM tbl_change_history
        WHERE cyclist_pcm_id = ? AND stat_name = ?
    """, (pcm_id, stat_name))
    
    result = cursor.fetchone()
    return (result[0] or 0) + 1

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
        # Initialize namespace if needed
        db_path = commons.get_path(namespace, 'tracking_db')
        if not os.path.exists(db_path):
            print(f"🗄️  Creating new tracking database for {namespace}...")
            init_namespace(namespace)
        else:
            print(f"📊 Using existing database for {namespace}")
  
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
    print("=" * 60)
    print("🌐 PCM Stats Management - Processing All Namespaces")
    print("=" * 60)
    
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
