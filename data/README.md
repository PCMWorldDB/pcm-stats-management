# Data Organization and Structure

This directory contains all data files organized by namespaces, including change files, stats files, and tracking databases.

## 📁 Directory Structure

```
data/
├── <namespace>/              # Each namespace is a separate directory
│   ├── changes/              # Change files directory
│   │   └── <change-name>/    # Individual change directories
│   │       ├── change.yaml   # Change specification
│   │       └── inserts.sql   # Generated SQL statements
│   ├── stats.yaml           # Main stats file for namespace
│   └── tracking_db.sqlite   # Change tracking database
└── README.md               # This file
```

## 🗂️ Namespaces

Namespaces provide logical separation of data by context, such as:
- **Year-based**: `2024`, `2025`, `2026` for different PCM database years
- **Development**: `2025dev`, `2024test` for testing and development
- **Project-based**: `worlddb`, `firstcycling` for different data sources

### Current Namespaces

Available namespaces are automatically detected by scanning the `data/` directory for subdirectories containing the required structure.

### Creating a New Namespace

Namespaces are created automatically when:
1. **Processing the first change file** for that namespace
2. **Importing from a database** using `import-from-db` command
3. **Manually creating** the directory structure

The system will automatically create:
- `changes/` directory for change files
- `tracking_db.sqlite` database with proper schema
- `stats.yaml` file when the first change is processed

## 📝 Change Files

Change files specify modifications to cyclist statistics and are organized in individual directories.

### Change Directory Structure

```
data/<namespace>/changes/<change-name>/
├── change.yaml      # Change specification (required)
└── inserts.sql     # Generated SQL statements (auto-generated)
```

### Change File Format

Each `change.yaml` file must contain:

```yaml
author: "Contributor Name"         # Required: Who made the change
date: "YYYY-MM-DD"                # Required: When the change was made
description: "Brief description"   # Optional: What the change is about
stats:                            # Required: List of stat changes
  - pcm_id: "12345"               # Required: PCM cyclist ID
    name: "Cyclist Name"          # Required: Cyclist name
    first_cycling_id: "67890"     # Optional: FirstCycling.com ID
    fla: 78                       # Optional: Flat terrain stat
    mo: 65                        # Optional: Mountain stat
    mm: 72                        # Optional: Medium mountain stat
    # ... other stats as needed
```

### Supported Stats

The following cyclist statistics are supported:

| Stat Key | Description | Database Column |
|----------|-------------|-----------------|
| `fla` | Flat terrain | `charac_i_plain` |
| `mo` | Mountain | `charac_i_mountain` |
| `mm` | Medium mountain | `charac_i_medium_mountain` |
| `dh` | Downhill | `charac_i_downhilling` |
| `cob` | Cobbles | `charac_i_cobble` |
| `tt` | Time trial | `charac_i_timetrial` |
| `prl` | Prologue | `charac_i_prologue` |
| `spr` | Sprint | `charac_i_sprint` |
| `acc` | Acceleration | `charac_i_acceleration` |
| `end` | Endurance | `charac_i_endurance` |
| `res` | Resistance | `charac_i_resistance` |
| `rec` | Recuperation | `charac_i_recuperation` |
| `hil` | Hill | `charac_i_hill` |
| `att` | Baroudeur | `charac_i_baroudeur` |

### Change Naming Conventions

Change directories should follow descriptive naming patterns:
- **Date-based**: `2025-08-11-Tour-of-Panama`
- **Event-based**: `Vuelta-2025-Stage-Updates`
- **Feature-based**: `New-Cyclist-Additions-August`
- **Source-based**: `FirstCycling-Import-Batch-1`

## 📊 Stats Files

The `stats.yaml` file contains the current state of all cyclist statistics for a namespace.

### Stats File Structure

```yaml
"12345":                        # PCM ID as string key
  name: "John Cyclist"          # Required: Cyclist name
  first_cycling_id: "67890"     # Optional: FirstCycling.com ID
  fla: 78                       # Stats in defined order
  mo: 65
  mm: 72
  # ... other stats
"12346":                        # Next cyclist
  name: "Jane Racer"
  fla: 82
  spr: 89
  # ... stats
```

### Stats File Features

- **Ordered Output**: Cyclists sorted by PCM ID numerically
- **Consistent Structure**: Name first, then first_cycling_id (if present), then stats in defined order
- **UTF-8 Encoding**: Supports international characters in names
- **YAML Format**: Human-readable and git-diff friendly

## 🗄️ Tracking Database

Each namespace has a SQLite database (`tracking_db.sqlite`) that tracks the history of all changes.

### Database Schema

#### `tbl_changes`
Stores metadata about each change file:
- `id`: Primary key
- `name`: Change directory name
- `description`: Change description
- `author`: Who made the change
- `date`: When the change was made

#### `tbl_cyclists`
Stores cyclist information:
- `id`: Primary key
- `pcm_id`: PCM database ID
- `name`: Cyclist name
- `first_cycling_id`: FirstCycling.com ID

#### `tbl_change_stat_history`
Tracks every stat change:
- `id`: Primary key
- `cyclist_id`: Foreign key to `tbl_cyclists`
- `change_id`: Foreign key to `tbl_changes`
- `stat_name`: Which stat was changed
- `stat_value`: New value
- `version`: Version number for this stat

### Database Benefits

- **Full History**: Every stat change is tracked with version numbers
- **Audit Trail**: Know who changed what and when
- **Rollback Capability**: Theoretical ability to roll back changes
- **Reporting**: Query change patterns and statistics

## 🔄 Data Flow

### Processing Workflow

1. **Change Created**: New `change.yaml` file added to namespace
2. **Processing Triggered**: CLI `process-changes` command run
3. **SQL Generated**: `inserts.sql` file created in change directory
4. **Stats Updated**: `stats.yaml` file updated with new data
5. **Database Tracked**: Changes recorded in `tracking_db.sqlite`
6. **Summary Generated**: Processing results reported

### Import Workflow

1. **Source Database**: Existing PCM SQLite database with `DYN_cyclist` table
2. **Import Command**: `import-from-db <namespace> <db_file>` executed
3. **Data Extracted**: Cyclist data read from source database
4. **Stats Created**: New `stats.yaml` file generated
5. **Namespace Initialized**: Directory structure created

## 📋 Data Validation

### Automatic Validation

The system validates:
- **YAML Syntax**: All files must be valid YAML
- **Required Fields**: Essential fields must be present
- **Data Types**: Cyclist IDs must be numeric
- **Stat Values**: Stats must be valid numbers
- **Unicode Support**: International characters properly handled

### Manual Validation

Use the validation command to check all files:
```bash
python -m src.pcm_cli validate-yaml
```

## 🛠️ Data Management

### Adding New Data

1. **Create change directory** in appropriate namespace
2. **Write change.yaml** with required fields
3. **Run processing** to generate SQL and update stats
4. **Review generated files** before committing

### Modifying Existing Data

1. **Create new change file** (don't edit existing ones)
2. **Include only changed stats** in the new file
3. **Process normally** - system handles merging

### Backup and Recovery

- **Git History**: All changes tracked in git
- **Database Backups**: SQLite files can be backed up easily
- **Stats File History**: YAML files show complete current state

## 🔍 Troubleshooting

### Common Issues

1. **Missing Namespace**: Create directory structure manually or use import
2. **Invalid YAML**: Check syntax and required fields
3. **Unicode Errors**: Ensure UTF-8 encoding is used
4. **Database Locks**: Check that SQLite files aren't locked by other processes

### Data Integrity

- **Consistent PCM IDs**: Ensure PCM IDs are consistent across changes
- **Name Matching**: Verify cyclist names match between changes
- **Stat Ranges**: Validate that stat values are reasonable (typically 1-99)

---

For CLI usage instructions, see [`src/README.md`](../src/README.md).
For CI/CD pipeline details, see [`../.github/README.md`](../.github/README.md).
