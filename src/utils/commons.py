import os

STAT_KEYS = ['fla', 'mo', 'mm', 'dh', 'cob', 'tt', 'prl', 'spr', 'acc', 'end', 'res', 'rec', 'hil', 'att']
DATA_PATH = os.path.join('data')
MODEL_DIR_PATH = os.path.join('src', 'model')

PATH_TYPES = ['root', 'changes_dir', 'stats_file', 'tracking_db', 'cdb']

def get_path(namespace, path_type):
    assert path_type in PATH_TYPES, f"Invalid path_type: {path_type}"
    if path_type == 'root':
        return os.path.join(DATA_PATH, namespace)
    elif path_type == 'changes_dir':
        return os.path.join(DATA_PATH, namespace, 'changes')
    elif path_type == 'stats_file':
        return os.path.join(DATA_PATH, namespace, 'stats.yaml')
    elif path_type == 'tracking_db':
        return os.path.join(DATA_PATH, namespace, 'tracking_db.sqlite')
    elif path_type == 'cdb':
        return os.path.join(DATA_PATH, namespace, 'cdb')


def get_available_namespaces():
    """
    Discover all available namespaces by scanning the data directory.
    
    Returns:
        list: List of namespace directory names
    """
    if not os.path.exists(DATA_PATH):
        return []
    
    namespaces = []
    for item in os.listdir(DATA_PATH):
        item_path = os.path.join(DATA_PATH, item)
        if os.path.isdir(item_path):
            namespaces.append(item)
    
    return sorted(namespaces)