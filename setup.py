import os

# Define color classes for ANSI escape codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    LIGHT_BLUE = '\033[94m'
    LIGHT_CYAN = '\033[96m'
    LIGHT_GREEN = '\033[92m'
    ENDC = '\033[0m'

# Expanded rainbow color scheme for folder depths
DEPTH_COLORS = [
    Colors.BLUE, Colors.CYAN, Colors.GREEN, Colors.YELLOW,
    Colors.RED, Colors.MAGENTA, Colors.LIGHT_BLUE, Colors.LIGHT_CYAN,
    Colors.LIGHT_GREEN
]

# Define emojis
EMOJIS = {
    'folder': '📁',
    'file': '📄',
    'hidden': '🙈'
}

def create_ignore_file(ignore_file='ignore.txt'):
    try:
        if not os.path.exists(ignore_file):
            with open(ignore_file, 'w') as file:
                file.write('')
    except IOError as e:
        print(f"Error creating '{ignore_file}': {e}")

def create_output_directory(output_dir='output'):
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    except OSError as e:
        print(f"{Colors.RED}❌ Error creating '{output_dir}' directory: {e}. Try running as sudo{Colors.ENDC}")
