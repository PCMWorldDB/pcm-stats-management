import os
import pytest
import yaml
from src.model import api
from src.utils import commons 

STATS_PATH = commons.STATS_FILE_PATH

# Helper to create a stats.yaml-like structure in a temp file
def write_stats_yaml(tmp_path):
    stats = {
        1: {
            "name": "F. Archibold",
            "first_cycling_id": 1,
            "fla": 75,
            "mo": 70,
            "mm": 65,
            "dh": 80,
            "cob": 61,
            "tt": 90,
            "prl": 85,
            "spr": 68,
            "acc": 80,
            "end": 70,
            "res": 75,
            "rec": 64,
            "hil": 69,
            "att": 68
        },
        2: {
            "name": "G. Rojas Campos",
            "first_cycling_id": 2,
            "fla": 75,
            "mo": 70,
            "mm": 65,
            "dh": 80,
            "cob": 61,
            "tt": 90,
            "prl": 85,
            "spr": 68,
            "acc": 80,
            "end": 70,
            "res": 75,
            "rec": 64,
            "hil": 69,
            "att": 68
        }
    }
    stats_file = tmp_path / "stats.yaml"
    yaml.dump(stats, stats_file.open('w'))
    return str(stats_file)

def test_validate_success(tmp_path):
    stats_file = write_stats_yaml(tmp_path)
    update = {
        "name": "Tour of Panama",
        "date": "2025-08-06",
        "stats": [
            {"pcm_id": 1, "name": "F. Archibold", "fla": 76},
            {"pcm_id": 2, "name": "G. Rojas Campos", "dh": 65}
        ]
    }
    update_file = tmp_path / "valid_update.yaml"
    yaml.dump(update, update_file.open('w'))
    assert api.validate_update_file(str(update_file), stats_file)

def test_validate_missing_key(tmp_path):
    stats_file = write_stats_yaml(tmp_path)
    update = {
        "name": "Tour of Panama",
        "stats": [
            {"pcm_id": 1, "name": "F. Archibold", "fla": 76}
        ]
    }
    update_file = tmp_path / "missing_key.yaml"
    yaml.dump(update, update_file.open('w'))
    assert not api.validate_update_file(str(update_file), stats_file)

def test_validate_invalid_pcm_id(tmp_path):
    stats_file = write_stats_yaml(tmp_path)
    update = {
        "name": "Tour of Panama",
        "date": "2025-08-06",
        "stats": [
            {"pcm_id": 999, "name": "Unknown Rider", "fla": 76}
        ]
    }
    update_file = tmp_path / "invalid_pcm_id.yaml"
    yaml.dump(update, update_file.open('w'))
    assert not api.validate_update_file(str(update_file), stats_file)
