# GitHub Actions CI/CD Pipeline

Comprehensive automation system for PCM Stats Management that validates, processes, and deploys changes through GitHub Actions workflows.

## 🚀 Pipeline Overview

The CI/CD system implements a **test-first approach** with automated processing, validation, and deployment of cyclist stat changes across multiple namespaces.

### Pipeline Philosophy
- **Test First**: All code is validated before any processing begins
- **Fail Fast**: Stop processing immediately if validation fails
- **Comprehensive**: Validate both code quality and data integrity
- **Transparent**: Detailed logging and reporting at every step

## � Workflow Files

### `process-changes.yml` - Main Processing Pipeline

**Location**: `.github/workflows/process-changes.yml`

**Purpose**: Main automation pipeline that processes stat changes and manages the complete lifecycle from validation to deployment.

**Triggers**:
- **Push events**: `main` and `develop` branches
- **Pull requests**: All PRs targeting `main` or `develop`
- **Manual dispatch**: Can be triggered manually via GitHub Actions UI
- **File changes**: Automatically triggered when files in `src/changes/` are modified

## 🔄 Pipeline Stages

### Stage 1: Environment Setup
```yaml
- name: Checkout repository
- name: Set up Python 3.8
- name: Install dependencies
```

**Purpose**: Prepare the execution environment
- Checks out the complete repository code
- Sets up Python 3.8 runtime environment
- Installs all dependencies from `requirements.txt`
- Verifies Python environment is ready for processing

### Stage 2: Test Execution
```yaml
- name: Run comprehensive test suite
  run: python -m pytest tests/ -v --tb=short
```

**Purpose**: Validate code quality and functionality
- **Test Coverage**: Runs all tests in `tests/` directory
- **Test Types**: Unit tests, integration tests, validation tests
- **Failure Handling**: Pipeline stops if any test fails
- **Reporting**: Detailed test output with verbose reporting

**Test Categories**:
- **Process Changes Tests**: Validate change file processing logic
- **YAML Validation Tests**: Test file format validation
- **Database Tests**: Verify SQLite operations and schema
- **CLI Tests**: Test command-line interface functionality

### Stage 3: YAML Validation
```yaml
- name: Validate all YAML files
  run: python -m src.pcm_cli validate-yaml
```

**Purpose**: Comprehensive validation of all data files
- **Syntax Checking**: Validates YAML syntax across all files
- **Structure Validation**: Ensures required fields are present
- **Data Integrity**: Checks cyclist IDs, names, and stat values
- **Cross-Namespace**: Validates files across all namespaces

**Validation Rules**:
- Change files must have `author`, `date`, and `stats`
- Stats files must have valid cyclist entries with `name`
- All cyclist IDs must be numeric
- YAML syntax must be valid

### Stage 4: Change Detection
```yaml
- name: Check for relevant changes
  run: python scripts/check_changes.py
```

**Purpose**: Intelligent change detection to avoid unnecessary processing
- **File Analysis**: Scans repository for meaningful changes
- **Smart Detection**: Ignores documentation-only changes
- **Efficiency**: Skips processing when no data changes exist
- **Output**: Sets processing flag for subsequent stages

### Stage 5: Change Processing
```yaml
- name: Process changes for all namespaces
  run: python -m src.pcm_cli process-changes
```

**Purpose**: Main processing logic execution
- **Multi-Namespace**: Processes all available namespaces automatically
- **SQL Generation**: Creates INSERT statements for database updates
- **Stats Updates**: Updates `stats.yaml` files with new data
- **Database Tracking**: Records changes in SQLite tracking databases

**Processing Steps**:
1. Scan all namespaces for new change files
2. Validate each change file structure
3. Generate SQL INSERT statements
4. Update stats.yaml files
5. Update tracking databases
6. Generate processing summaries

### Stage 6: Artifact Management
```yaml
- name: Commit and push generated files
```

**Purpose**: Persist generated files back to repository
- **Auto-Commit**: Commits generated SQL files and updated stats
- **Clean History**: Uses meaningful commit messages
- **Branch Safety**: Only commits to appropriate branches
- **Conflict Resolution**: Handles merge conflicts gracefully

## 🎯 Trigger Conditions

### Automatic Triggers

#### Push Events
```yaml
on:
  push:
    branches: [main, develop]
    paths: ['src/**', 'data/**', 'tests/**']
```
- Triggers on pushes to main or develop branches
- Only when relevant files are modified
- Ensures production and development branches stay in sync

#### Pull Request Events
```yaml
on:
  pull_request:
    branches: [main, develop]
    types: [opened, synchronize, reopened]
```
- Validates all pull requests before merge
- Runs complete test suite on PR code
- Provides feedback directly in PR comments
- Prevents broken code from reaching main branches

#### Manual Dispatch
```yaml
on:
  workflow_dispatch:
    inputs:
      namespace:
        description: 'Specific namespace to process'
        required: false
```
- Allows manual triggering via GitHub Actions UI
- Optional namespace parameter for targeted processing
- Useful for debugging and emergency processing

### File-Based Triggers
The pipeline intelligently responds to changes in specific file patterns:
- `src/changes/**/*.yaml` - Change files
- `src/**/*.py` - Source code modifications
- `tests/**/*.py` - Test updates
- `data/**/*.yaml` - Direct data file changes

## 📊 Pipeline Outputs

### Success Indicators
- ✅ **All tests passed**
- ✅ **YAML validation successful**
- ✅ **Changes processed without errors**
- ✅ **Generated files committed successfully**

### Generated Artifacts
1. **SQL Files**: `inserts.sql` in each change directory
2. **Updated Stats**: Modified `stats.yaml` files
3. **Database Updates**: Updated `tracking_db.sqlite` files
4. **Processing Logs**: Detailed execution logs
5. **JSON Summaries**: Machine-readable processing results

### Failure Handling
- **Test Failures**: Pipeline stops immediately, no processing occurs
- **Validation Errors**: Detailed error messages with file locations
- **Processing Errors**: Graceful error handling with rollback capability
- **Commit Conflicts**: Automatic conflict resolution or manual intervention prompts

## 🔧 Configuration

### Environment Variables
```yaml
env:
  PYTHONPATH: ${{ github.workspace }}
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Automatic Variables**:
- `GITHUB_TOKEN`: Authentication for repository operations
- `PYTHONPATH`: Ensures proper Python module imports
- `GITHUB_WORKSPACE`: Repository root directory path

### Workflow Settings
```yaml
permissions:
  contents: write
  pull-requests: write
  checks: write
```

**Required Permissions**:
- **Contents Write**: Commit generated files back to repository
- **Pull Requests Write**: Add comments to PRs with processing results
- **Checks Write**: Report test status and validation results

### Repository Configuration

#### Required Settings
In repository Settings → Actions → General:
- ✅ **Workflow permissions**: "Read and write permissions"
- ✅ **Allow GitHub Actions to create and approve pull requests**: Enabled

#### Branch Protection (Recommended)
For production repositories:
- **Require status checks**: Pipeline must pass before merge
- **Require up-to-date branches**: Ensure latest code is tested
- **Include administrators**: Apply rules to all users

## 🐛 Debugging and Monitoring

### Viewing Pipeline Runs
1. Navigate to repository's **Actions** tab
2. Select specific workflow run
3. Expand job steps to see detailed logs
4. Download artifacts for offline analysis

### Common Issues and Solutions

#### Test Failures
```bash
# Local testing before push
python -m pytest tests/ -v
python -m src.pcm_cli validate-yaml
```

#### YAML Validation Errors
```bash
# Check specific files locally
python -m src.pcm_cli validate-yaml
# Fix syntax errors and required fields
```

#### Processing Errors
```bash
# Test processing locally
python -m src.pcm_cli process-changes
# Check file permissions and database access
```

#### Permission Issues
- Verify repository settings allow Actions to write
- Check branch protection rules
- Ensure GITHUB_TOKEN has sufficient permissions

### Log Analysis
- **Step-by-step execution**: Each pipeline stage logs detailed progress
- **Error context**: Failures include file names, line numbers, and error descriptions
- **Processing summaries**: JSON output shows exactly what was processed
- **Timing information**: Performance metrics for optimization

## 🔄 Customization

### Adding New Validation Steps
```yaml
- name: Custom validation
  run: python scripts/custom_validator.py
```

### Environment-Specific Processing
```yaml
- name: Production processing
  if: github.ref == 'refs/heads/main'
  run: python -m src.pcm_cli process-changes --production
```

### Notification Integration
```yaml
- name: Notify Discord
  if: success()
  run: python scripts/notify_discord.py
```

## 📈 Performance and Optimization

### Pipeline Efficiency
- **Parallel Execution**: Tests and validation run concurrently where possible
- **Smart Caching**: Python dependencies cached between runs
- **Conditional Processing**: Skips unnecessary steps based on change detection
- **Incremental Updates**: Only processes new or modified change files

### Resource Usage
- **Execution Time**: Typically 2-5 minutes for full pipeline
- **Memory Usage**: Optimized for GitHub Actions standard runners
- **Storage**: Minimal artifact storage with automatic cleanup

---

For CLI usage details, see [`../src/README.md`](../src/README.md).
For data organization information, see [`../data/README.md`](../data/README.md).
