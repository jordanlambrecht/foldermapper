import os
import sys
import time
from tabulate import tabulate
import json

###############
# COLOR SETUP #
###############
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


# Load or create configuration file
# Load or create configuration file
# Load or create configuration file
config_file = 'foldermapper_config.json'
if os.path.exists(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
else:
    config = {
        'show_emojis': False,
        'ascii_style': 'basic',
        'vertical_connectors': False,
        'show_hidden': False,
        'file_limit': None
    }
#########
# SETUP #
#########
class Setup:
    @staticmethod
    def create_ignore_file():
        try:
            if not os.path.exists('ignore.txt'):
                with open('ignore.txt', 'w') as file:
                    file.write('')
        except IOError as e:
            print(f"Error creating 'ignore.txt': {e}")

    @staticmethod
    def create_output_directory():
        try:
            if not os.path.exists('output'):
                os.makedirs('output')
        except OSError as e:
            print(f"{Colors.RED}❌ Error creating 'output' directory: {e}. Try running as sudo{Colors.ENDC}")
            print(f"{Colors.RED}❌ Exiting...{Colors.ENDC}")
            print(f"    ")
            print(f"    ")
#########################
# GENERATE THE TREE MAP #
#########################
def generate_tree_map(root_dir, prefix='', max_depth=None, show_files=True, show_hidden=False, file_limit=None, style='basic', vertical_connectors=False, depth=0, stats={'main_folders': 0, 'sub_folders': 0, 'files': 0, 'deepest': 0}):
    if max_depth is not None and depth >= max_depth:
        return
    files = sorted(os.listdir(root_dir))
    if not show_hidden:
        files = [f for f in files if not f.startswith('.')]
    files = [f for f in files if show_files or os.path.isdir(os.path.join(root_dir, f))]
    stats['sub_folders'] += 1 if depth > 0 else 0
    stats['main_folders'] += 1 if depth == 0 else 0
    stats['deepest'] = max(stats['deepest'], depth)
    displayed_files = 0
    color = DEPTH_COLORS[depth % len(DEPTH_COLORS)] if depth < len(DEPTH_COLORS) else DEPTH_COLORS[-1]
    for i, file in enumerate(files):
        is_last_item = i == len(files) - 1
        connector = '└──' if is_last_item else '├──'
        print(f"{prefix}{color}{connector}{Colors.ENDC} {file}")
        displayed_files += 1
        if file_limit is not None and displayed_files >= file_limit:
            break
        if os.path.isdir(os.path.join(root_dir, file)):
            extension = '    ' if is_last_item else '│   '
            generate_tree_map(os.path.join(root_dir, file), prefix + extension, max_depth, show_files, show_hidden, file_limit, style, vertical_connectors, depth + 1, stats)
        else:
            stats['files'] += 1
    return stats

            
def update_progress(current_folder):
    current_folder[0] += 1
    print_progress_spinner(current_folder[0], total_folders)
####################
# PROGRESS SPINNER #
####################
def print_progress_spinner(progress, total):
    spinner = ['-', '\\', '|', '/']
    percentage = (progress / total) * 100
    bar_length = 20
    filled_length = int(bar_length * progress // total)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    for s in spinner:
        sys.stdout.write(f'{Colors.CYAN} \r{s} [{bar}] {percentage:.2f}% {Colors.ENDC} ')
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\r ')


########
# MAIN #
########
if __name__ == '__main__':
    print("\nWelcome to FolderMapper!\n")

    Setup.create_ignore_file()
    Setup.create_output_directory()

    try:
        with open('ignore.txt', 'r') as file:
            ignore_list = file.read().splitlines()
    except IOError as e:
        print(f"Error reading 'ignore.txt': {e}")
        ignore_list = []

    root_directory = input("📂 Enter the path to the root directory: ")
    max_depth = int(input("📏 How many folders deep should the search go? (0 for all): ") or '0')
    max_depth = None if max_depth == 0 else max_depth
    show_files = input("📄 Do you want to see file names? (yes/no) [default: yes]: ").lower() == 'yes'
    show_hidden = input("🕵️‍♂️ Do you want to display hidden files? (yes/no) [default: no]: ").lower() == 'yes'
    file_limit = int(input("🔢 How many files should be listed in each directory? (0 for all): ") or '0')
    file_limit = None if file_limit == 0 else file_limit

    print("\nGenerating tree map...\n")
    stats = generate_tree_map(root_directory, max_depth=max_depth, show_files=show_files, show_hidden=show_hidden, file_limit=file_limit)

    # Output stats
    print("\nStatistics:")
    stats_table = tabulate([stats.values()], headers=stats.keys())
    print(stats_table)

    # Save configuration
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)