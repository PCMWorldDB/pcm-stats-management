# PCM Stats Management CLI Tool

The unified command-line interface for all PCM stats management operations. This tool consolidates functionality for processing changes, validating files, and importing data.

## 🚀 Usage

### Running the CLI
```bash
python -m src.pcm_cli <command> [options]
```

## 📋 Available Commands

### `process-changes`
Processes change files for all namespaces automatically.

**Purpose**: Main CI/CD operation that:
- Scans all namespaces for new change files
- Creates tracking databases if they don't exist
- Processes YAML change files into SQL statements
- Updates stats.yaml files with new data
- Generates processing summaries

**Usage**:
```bash
python -m src.pcm_cli process-changes
```

**Output**:
- Generates `inserts.sql` files in each change directory
- Updates `stats.yaml` files with new cyclist data
- Creates or updates `tracking_db.sqlite` files
- Prints processing summary in JSON format

### `validate-yaml`
Validates all YAML files across all namespaces.

**Purpose**: Comprehensive validation that checks:
- YAML syntax correctness
- Required fields presence
- Data structure compliance
- Both change files and stats files

**Usage**:
```bash
python -m src.pcm_cli validate-yaml
```

**Validation Rules**:
- **Change files**: Must have `author`, `date`, and `stats` fields
- **Stats files**: Must have cyclist entries with `name` field
- **Structure**: All cyclist IDs must be numeric
- **Syntax**: Valid YAML format

### `import-from-db`
Imports cyclist data from existing PCM SQLite databases.

**Purpose**: Bootstrap new namespaces or migrate data from existing PCM databases.

**Usage**:
```bash
python -m src.pcm_cli import-from-db <namespace> <db_file>
```

**Parameters**:
- `namespace`: Target namespace (e.g., "2025", "2025dev")
- `db_file`: Path to SQLite database file containing DYN_cyclist table

**Example**:
```bash
python -m src.pcm_cli import-from-db 2025dev /path/to/pcm_database.sqlite
```

**Database Requirements**:
- Must contain `DYN_cyclist` table
- Required columns: `IDcyclist`, `gene_sz_lastname`, `gene_sz_firstname`, `value_f_current_ability`
- Stat columns: `charac_i_plain`, `charac_i_mountain`, etc.

### `help`
Shows detailed help information.

**Usage**:
```bash
python -m src.pcm_cli help
```

## 📁 Source Code Layout

### Core Modules

```
src/
├── pcm_cli.py              # Main CLI entry point and command router
├── api.py                  # Core business logic and database operations
├── __init__.py             # Package initialization
├── examples/               # Example data and imports
│   └── firstcycling_export/
├── models/                 # Database schemas and models
│   ├── api.py              # Model API definitions
│   ├── schema.sql          # Main database schema
│   └── tracking_db/        # Tracking database schema
├── stats/                  # Stats configuration
│   └── stats.yaml          # Global stats configuration
└── utils/                  # Utility modules
    └── commons.py          # Common utilities and constants
```

### Module Descriptions

#### `pcm_cli.py` - CLI Entry Point
- **Purpose**: Command-line interface and argument parsing
- **Key Functions**:
  - `main()`: CLI argument parsing and command routing
  - `process_changes()`: Delegates to API for change processing
  - `validate_yaml_files()`: Delegates to API for validation
  - `import_from_db()`: Delegates to API for database import

#### `api.py` - Core Business Logic
- **Purpose**: All business logic and database operations
- **Key Functions**:
  - `process_all_namespaces()`: Main processing workflow
  - `process_new_change_files()`: Process individual change files
  - `update_stats_file_with_changes()`: Update stats.yaml files
  - `validate_yaml_files()`: Comprehensive YAML validation
  - `import_cyclists_from_db()`: Database import functionality
  - `create_new_database()`: Initialize tracking databases

#### `utils/commons.py` - Shared Utilities
- **Purpose**: Common constants, path utilities, and shared functions
- **Key Features**:
  - Path management for namespaces
  - Stat key definitions and ordering
  - Namespace discovery utilities
  - Configuration constants

### Data Flow

1. **CLI Command** → `pcm_cli.py` parses arguments
2. **Business Logic** → `api.py` processes the request
3. **File Operations** → Read/write YAML files and SQLite databases
4. **Utilities** → `commons.py` provides paths and constants
5. **Output** → Generated SQL files and updated stats files

### Integration Points

#### With Tests
- Test files in `tests/` directory validate all CLI commands
- Comprehensive test coverage for processing and validation
- Integration tests for database operations

#### With CI/CD
- CLI commands are used in GitHub Actions workflows
- `process-changes` is the main CI/CD entry point
- Validation runs before processing in the pipeline

#### With Data Structure
- CLI operates on data files in `data/<namespace>/` directories
- Respects namespace isolation and organization
- Generates outputs in appropriate namespace directories

## 🔧 Configuration

### Environment Variables
The CLI respects these environment variables:
- Standard Python path variables for module imports
- SQLite database connection settings (default timeouts, etc.)

### Path Configuration
All paths are managed through `commons.py`:
- Namespace root directories
- Change file locations
- Stats file paths
- Database file paths

### Stat Configuration
Cyclist stats are defined in `commons.STAT_KEYS`:
```python
STAT_KEYS = ['fla', 'mo', 'mm', 'dh', 'cob', 'tt', 'prl', 'spr', 'acc', 'end', 'res', 'rec', 'hil', 'att']
```

## 🐛 Error Handling

### Common Issues
1. **Import Errors**: Ensure you're running from the repository root
2. **Database Errors**: Check SQLite file permissions and schema
3. **YAML Errors**: Validate YAML syntax and required fields
4. **Unicode Errors**: Fixed with UTF-8 encoding in recent updates

### Debugging
- Use `--help` flag for command-specific help
- Check file paths and permissions
- Validate YAML files before processing
- Review generated SQL files for database issues

## 📊 Output Formats

### JSON Summary (process-changes)
```json
{
  "processed_namespaces": 1,
  "successful_namespaces": ["2025dev"],
  "failed_namespaces": [],
  "total_changes": 5,
  "overall_success": true
}
```

### Validation Report (validate-yaml)
```
✅ change.yaml (change-2025dev): Valid
✅ stats.yaml (stats-2025dev): Valid
🎉 All YAML files passed validation!
```

### Import Report (import-from-db)
```
✅ Successfully imported 150 cyclists to data/2025dev/stats.yaml
   - Namespace: 2025dev
   - Source: /path/to/database.sqlite
   - Cyclists: 150
```
- Useful for testing before pushing to GitHub

```bash
python src/cli.py test-local
```

### `status`
Check project status and generate workflow variables
- Checks for change files
- Checks database status
- Checks generated files
- Validates dependencies
- Outputs GitHub Actions environment variables
- Generates workflow status summary

```bash
python src/cli.py status
```

### `help`
Show help message with command descriptions

```bash
python src/cli.py help
```

## Migration from Old Scripts

The new CLI consolidates the following old scripts:

| Old Script | New Command |
|------------|-------------|
| `scripts/process_changes.py` | `python src/cli.py process` |
| `scripts/validate_yaml.py` | `python src/cli.py validate-yaml` |
| `scripts/validate_setup.py` | `python src/cli.py validate-setup` |
| `scripts/test_local_ci.py` | `python src/cli.py test-local` |
| `scripts/workflow_utils.py` | `python src/cli.py status` |

## GitHub Actions Integration

The GitHub Actions workflow (`.github/workflows/cicd.yml`) has been updated to use the new CLI:

- Feature branches: `python src/cli.py status` and `python src/cli.py validate-yaml`
- Code validation: `python src/cli.py validate-setup`
- Main branch (when enabled): `python src/cli.py status` and `python src/cli.py process`

## Dependencies

The CLI requires the same dependencies as the original scripts:
- PyYAML
- SQLite3 (built-in)
- pathlib (built-in)
- json (built-in)

Install with:
```bash
pip install -r requirements.txt
```

## Benefits of Consolidation

1. **Single Entry Point**: One command instead of multiple scripts
2. **Consistent Interface**: All commands use the same CLI pattern
3. **Better Error Handling**: Centralized error handling and logging
4. **Easier Maintenance**: One file to maintain instead of many
5. **Cleaner Repository**: Reduced file clutter in the scripts folder
6. **Better Documentation**: All functionality documented in one place
