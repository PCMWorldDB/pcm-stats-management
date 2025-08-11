# PCM Stats Management

A comprehensive system for managing Pro Cycling Manager (PCM) cyclist statistics with automated processing, change tracking, and collaborative review workflows.

## 🌟 Features

- **Automated Change Processing**: Process YAML change files and generate SQL statements automatically
- **Change History Tracking**: Maintain complete history of all stat modifications with SQLite tracking database
- **Collaborative Review**: Git-based workflow for reviewing and approving stat changes
- **Multi-Namespace Support**: Organize data by different contexts (years, projects, etc.)
- **Database Import**: Import cyclist data from existing PCM SQLite databases
- **YAML Validation**: Comprehensive validation of change files and stats files
- **CI/CD Integration**: Automated GitHub Actions workflows for processing and validation

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git
- SQLite

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/PCMWorldDB/pcm-stats-management.git
   cd pcm-stats-management
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Verify installation:
   ```bash
   python -m src.pcm_cli validate-yaml
   ```

## 📋 Basic Usage

### Processing Changes
Process all pending change files across all namespaces:
```bash
python -m src.pcm_cli process-changes
```

### Validating Files
Validate all YAML files for syntax and structure:
```bash
python -m src.pcm_cli validate-yaml
```

### Importing from Database
Import cyclist data from an existing PCM SQLite database:
```bash
python -m src.pcm_cli import-from-db <namespace> <database_file>
```

## 📝 Adding a Stat Change

To add new stat changes to the system:

1. **Create a Change Directory**: In your namespace's `changes/` folder, create a new directory with a descriptive name:
   ```
   data/<namespace>/changes/2025-08-11-Tour-of-Panama/
   ```

2. **Create change.yaml**: Inside the directory, create a `change.yaml` file:
   ```yaml
   author: "Your Name"
   date: "2025-08-11"
   description: "Updated stats for Tour of Panama riders"
   stats:
     - pcm_id: "12345"
       name: "John Cyclist"
       first_cycling_id: "67890"
       fla: 78
       mo: 65
       spr: 82
   ```

3. **Process the Change**: Run the processing command:
   ```bash
   python -m src.pcm_cli process-changes
   ```

4. **Review Generated Files**: Check the generated `inserts.sql` file in your change directory and updated `stats.yaml` file.

## 🗂️ Adding a Namespace

Namespaces organize data by context (e.g., different years, projects, or databases):

1. **Create Namespace Structure**: The system will automatically create the structure when you first use a namespace:
   ```
   data/<namespace>/
   ├── changes/           # Change files
   ├── stats.yaml        # Main stats file
   └── tracking_db.sqlite # Change tracking database
   ```

2. **Initialize with Import**: Start a new namespace by importing from an existing database:
   ```bash
   python -m src.pcm_cli import-from-db <namespace> <database_file>
   ```

3. **Manual Initialization**: The namespace structure is created automatically when processing the first change file.

## 📁 Project Structure

```
pcm-stats-management/
├── .github/workflows/    # CI/CD automation
├── data/                 # Data files organized by namespace
├── src/                  # Source code
├── tests/                # Test suite
├── scripts/              # Utility scripts
└── README.md            # This file
```

## 🔄 Workflow

1. **Create Changes**: Add YAML change files to namespace directories
2. **Process**: Run processing to generate SQL and update stats files
3. **Review**: Check generated SQL statements and updated files
4. **Commit**: Commit changes to Git for collaborative review
5. **Deploy**: Use CI/CD pipeline for automated processing

## 🛠️ Advanced Usage

For detailed usage of the CLI tool, see [`src/README.md`](src/README.md).

For information about data organization, see [`data/README.md`](data/README.md).

For CI/CD pipeline details, see [`.github/README.md`](.github/README.md).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your changes using the change file system
4. Submit a pull request for review

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

![Project Workflow](flow_img.jpg)