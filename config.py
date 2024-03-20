import json
import os

# Load or create configuration file
def load_config(config_file='foldermapper_config.json'):
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    else:
        return {
            'show_emojis': False,
            'ascii_style': 'basic',
            'vertical_connectors': False,
            'show_hidden': False,
            'file_limit': None
        }

def save_config(config, config_file='foldermapper_config.json'):
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)
