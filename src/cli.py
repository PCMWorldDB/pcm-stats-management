import argparse
import yaml
import os
import commons
import api


# Main CLI function
def main():
    parser = argparse.ArgumentParser(description="PCM Stats Management CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate an update file.")
    validate_parser.add_argument("--update", required=True, help="Path to the update YAML file.")

    args = parser.parse_args()

    if args.command == "validate":
        update_file_name = args.update
        api.validate_update_file(update_file_name, commons.STATS_FILE_PATH)

if __name__ == "__main__":
    main()