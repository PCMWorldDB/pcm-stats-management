# PCM Stats Management

A management system for Pro Cycling Manager (PCM) cyclist statistics with automated processing, change tracking, and collaborative review workflows.

## 🌟 Features

- **Automated Change Processing**: Process stat change files and generate SQL statements automatically
- **Change History Tracking**: Maintain complete history of all stat modifications with SQLite tracking database
- **Collaborative Review**: Git-based workflow for reviewing and approving stat changes
- **Multi-Namespace Support**: Organize data by different contexts (years, projects, etc.)
- **Database Import**: Import cyclist data from existing PCM SQLite databases
- **YAML Validation**: Comprehensive validation of change files and stats files
- **CI/CD Integration**: Automated GitHub Actions workflows for processing and validation


## 📝 Adding a Stat Change

To add new stat changes to the system:

1. Create new branch Off of `uat` branch with naming convention `change/{my-change-description}`
2. Create a new directory and `change.yml` file for the namespace you're working on:
   1.  `data/{my-namespace}/changes/{my-change-name}/change.yml
3. Commit changes, and push the branch
4. Create Pull Request into UAT and the automation pipelines will run.
5. Review Generated Files Check the generated `inserts.sql` file in your change directory and updated `stats.yaml` file.

## 🗂️ Adding a Namespace

Namespaces organize data by context (e.g., different years, projects, or databases):

1. **Create Namespace Structure**: The system will automatically create the structure when you create a namespace directory:
   ```
   data/<namespace>/
   ├── changes/           # Change files
   ├── init_cdb.sqlite    # PCM database to generate initial stats from
   ```

2. **Manual Initialization**: The namespace structure is created automatically when processing the first change file.

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