# PCM Stats Management CLI Tool

This consolidated CLI tool replaces the multiple individual scripts in the `scripts/` folder with a single, unified command-line interface.

## Usage

```bash
python src/cli.py <command> [options]
```

## Available Commands

### `process`
Process change files (main CI/CD operation)
- Creates or updates tracking database
- Processes new YAML change files
- Generates SQL insert statements
- Creates processing summary for GitHub Actions

```bash
python src/cli.py process
```

### `validate-yaml`
Validate YAML change files format
- Checks YAML syntax
- Validates required fields (name, date, stats)
- Validates stats structure

```bash
python src/cli.py validate-yaml
```

### `validate-setup`
Validate repository structure and setup
- Checks required files and directories
- Validates Python imports
- Validates GitHub Actions workflow syntax
- Creates missing directories automatically
- Generates setup report

```bash
python src/cli.py validate-setup
```

### `test-local`
Run local CI/CD simulation
- Validates workflow files
- Creates sample change file
- Simulates the full processing pipeline
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
