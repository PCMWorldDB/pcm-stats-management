# GitHub Actions CI/CD Setup for PCM Stats Management

This directory contains GitHub Actions workflows that automate the processing of PCM (Pro Cycling Manager) statistics changes. The workflows can read files from the repository, process them using custom Python functions, and commit changes back to the repository.

## 🚀 Features

- **Automated Processing**: Automatically processes new YAML change files
- **Database Management**: Creates and updates SQLite tracking databases
- **SQL Generation**: Generates INSERT statements for database updates  
- **Smart Triggers**: Only runs when relevant files change
- **Error Handling**: Comprehensive error reporting and logging
- **Testing**: Validates code quality and runs tests
- **Manual Triggers**: Can be run manually with custom parameters

## 📁 Workflow Files

### `process-changes.yml` (Main Workflow)
- **Triggers**: Push to main/develop, PRs, manual dispatch
- **Purpose**: Automated processing of change files and SQL generation
- **Features**: 
  - Processes new YAML files in `src/changes/`
  - Generates SQL INSERT statements
  - Commits results back to repository
  - Runs tests for validation
  - Smart change detection using dedicated scripts
  - PR comments with processing summaries

## 🛠️ Setup Instructions

### 1. Prerequisites
- Python 3.8+ environment
- Required Python packages (see `requirements.txt`)
- SQLite database schema file (`src/models/tracking_schema.sql`)

### 2. Repository Configuration
1. **Copy workflow files** to your repository's `.github/workflows/` directory
2. **Ensure proper permissions** in your repository settings:
   - Go to Settings → Actions → General
   - Set "Workflow permissions" to "Read and write permissions"
   - Enable "Allow GitHub Actions to create and approve pull requests"

### 3. Required Repository Structure
```
your-repo/
├── .github/workflows/           # GitHub Actions workflow
├── src/
│   ├── api.py                  # Database processing functions
│   ├── changes/                # YAML change files
│   ├── models/
│   │   ├── tracking_schema.sql          # Database schema
│   └── utils/
│       └── commons.py          # Common utilities
├── tests/                      # Test files
└── requirements.txt            # Python dependencies
```

## 🔧 Configuration Options

### Environment Variables
The workflow uses these environment variables (automatically set):
- `GITHUB_TOKEN`: Automatically provided by GitHub Actions

### Manual Workflow Inputs
The workflow supports manual triggers with the workflow_dispatch event.

## 📋 How It Works

### Automatic Triggering
1. **File Changes**: Workflows trigger when files in `src/changes/`
2. **Change Detection**: Smart detection only processes when relevant changes are found
3. **Processing**: Runs custom Python functions to process YAML files
4. **Database Updates**: Creates/updates SQLite tracking databases
5. **SQL Generation**: Generates INSERT statements for manual review
6. **Commits**: Automatically commits generated files back to repository

## 📊 Monitoring and Debugging

### GitHub Actions Interface
1. Go to your repository's **Actions** tab
2. Select a workflow run to view details
3. Expand job steps to see detailed logs
4. Download artifacts for offline analysis

## 🔄 Customization
