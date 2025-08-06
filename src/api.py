import yaml
import os
from src import commons


# Function to validate the update file
def validate_update_file(update_file_name, stats_file_path):
    try:
        # Load the update file
        update_file_path = os.path.join(commons.UPDATES_DIR_PATH, update_file_name)
        with open(update_file_path, 'r') as update_file:
            update_data = yaml.safe_load(update_file)

        # Check required keys in the update file
        required_keys = ['name', 'date', 'stat_updates']
        for key in required_keys:
            if key not in update_data:
                print(f"Error: Missing key '{key}' in update file.")
                return False

        # Load the stats file
        with open(stats_file_path, 'r') as stats_file:
            stats_data = yaml.safe_load(stats_file)

        # Validate pcm_ids and keys in stat_updates
        valid_pcm_ids = stats_data.keys()
        for change in update_data['stat_updates']:
            if 'pcm_id' not in change:
                print(f"Error: Missing pcm_id in stat_updates: {change}")
                return False
            elif change['pcm_id'] not in valid_pcm_ids:
                print(f"Error: Invalid pcm_id in stat_updates: {change}")
                return False

            # Validate keys in each stat change
            valid_keys = ['pcm_id', 'name'] + commons.STAT_KEYS
            for key in change:
                if key not in valid_keys:
                    print(f"Error: Invalid key '{key}' in stat_updates: {change}")
                    return False
        result = "Validation successful."
        print(result)
        return True, result

    except Exception as e:
        print(f"Error: {e}")
        return False, str(e)