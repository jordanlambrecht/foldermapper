import os
import subprocess
import sys
import json
import sys
import time
from tabulate import tabulate


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

# Define the path to the virtual environment
venv_path = os.path.join(os.path.dirname(__file__), 'foldermapper', 'venv')

# Function to create and activate the virtual environment
def setup_environment():
    if not os.path.exists(venv_path):
        subprocess.check_call([sys.executable, '-m', 'venv', venv_path])
    
    # Activate the virtual environment
    if sys.platform == 'win32':
        activate_script = os.path.join(venv_path, 'Scripts', 'activate.bat')
    else:
        activate_script = os.path.join(venv_path, 'bin', 'activate')
    os.system(f'source {activate_script}' if sys.platform != 'win32' else activate_script)

    # Install requirements using pip from the virtual environment
    pip_executable = os.path.join(venv_path, 'bin', 'pip') if sys.platform != 'win32' else os.path.join(venv_path, 'Scripts', 'pip.exe')
    requirements_file = os.path.join(os.path.dirname(__file__), 'foldermapper', 'requirements.txt')
    subprocess.check_call([pip_executable, 'install', '-r', requirements_file])

# Set up the environment before importing from the package
setup_environment()


def validate_directory(path):
    if not os.path.exists(path):
        print(f"{Colors.RED}Error: The directory '{path}' does not exist.{Colors.ENDC}")
        return False
    return True

def prompt_with_default(prompt, default):
    return input(f"{prompt} [default: {default}]: ") or default

def prompt_with_default(prompt, default):
    return input(f"{prompt} [default: {default}]: ") or default

def validate_yes_no(prompt, default):
    while True:
        response = prompt_with_default(prompt, default).lower()
        if response in ['yes', 'no']:
            return response == 'yes'
        print(f"{Colors.RED}Invalid entry. Please enter 'yes' or 'no'.{Colors.ENDC}")

def validate_integer(prompt, default):
    while True:
        try:
            return int(prompt_with_default(prompt, default))
        except ValueError:
            print(f"{Colors.RED}Invalid entry. Please enter an integer.{Colors.ENDC}")

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

def get_depth_color(depth, show_emojis=False):
    color = DEPTH_COLORS[depth % len(DEPTH_COLORS)]
    if show_emojis:
        return EMOJIS['folder'] + color
    return color

def print_progress_spinner(progress, total):
    spinner = ['-', '\\', '|', '/']
    percentage = (progress / total) * 100
    bar_length = 20
    filled_length = int(bar_length * progress // total)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    for s in spinner:
        sys.stdout.write(f'{Colors.CYAN} \r{s} [{bar}] {percentage:.2f}% {Colors.ENDC} ')
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write('\r ')

    
def tabulate_stats(stats):
    # Convert the stats dictionary into a list of keys and a list of values
    headers = list(stats.keys())
    values = list(stats.values())
    # Use the tabulate library to format the table
    return tabulate([values], headers=headers, tablefmt="grid")

def export_tree_map(root_dir, stats, export_format, output_dir='output', **config):
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Format the data based on the export format
    if export_format == 'json':
        formatted_data = json.dumps(stats, indent=4)
        file_extension = '.json'
    elif export_format == 'markdown':
        formatted_data = f"# Tree Map for {root_dir}\n\n" + \
                         "| Statistic | Value |\n" + \
                         "|-----------|-------|\n"
        for key, value in stats.items():
            formatted_data += f"| {key} | {value} |\n"
        file_extension = '.md'
    else:  # Default to text format
        formatted_data = f"Tree Map for {root_dir}\n\n"
        for key, value in stats.items():
            formatted_data += f"{key}: {value}\n"
        file_extension = '.txt'

    # Create the output filename and write the data to the file
    output_filename = os.path.join(output_dir, f"tree_map_{os.path.basename(root_dir)}{file_extension}")
    with open(output_filename, 'w') as file:
        file.write(formatted_data)

    print(f"Tree map exported to {output_filename}")
    


def generate_tree_map(root_dir, prefix='', depth=0, stats=None, update_progress=None, **config):
    if stats is None:
        stats = {'main folders': 0, 'sub folders': 0, 'files': 0, 'deepest': 0}

    max_depth = config.get('max_depth')
    show_files = config.get('show_files', True)
    show_hidden = config.get('show_hidden', False)
    file_limit = config.get('file_limit')
    show_emojis = config.get('show_emojis', False)
    vertical_connectors = config.get('vertical_connectors', False)
    count_sub_items = config.get('count_sub_items', False)
    ascii_style = config.get('ascii_style', 'basic')

    if max_depth is not None and depth >= max_depth:
        if count_sub_items:
            subfolders, subfiles = count_sub_items_in_directory(root_dir, show_hidden)
            print(f"{prefix}│   {subfolders} subfolders and {subfiles} files")
        else:
            print(f"{prefix}│   ... and more folders")
        return stats

    try:
        entries = sorted(os.listdir(root_dir))
    except PermissionError:
        print(f"{Colors.RED}Permission denied: {root_dir}{Colors.ENDC}")
        return stats

    entries = [e for e in entries if show_hidden or not e.startswith('.')]
    displayed_files = 0

    connector_symbols = {
        'basic': ('├──', '└──'),
        'plus_minus': ('+-', '+-'),
        'pipes_dashes': ('|-', '+-'),
        'double_lines': ('╠══', '╚══')
    }

    connector_main, connector_last = connector_symbols.get(ascii_style, connector_symbols['basic'])

    for i, entry in enumerate(entries):
        is_last_item = i == len(entries) - 1
        connector = connector_last if is_last_item else connector_main
        entry_path = os.path.join(root_dir, entry)
        is_dir = os.path.isdir(entry_path)

        if is_dir:
            stats['sub folders'] += 1
            icon = EMOJIS['folder'] + ' ' if show_emojis else ''
        elif show_files:
            stats['files'] += 1
            icon = EMOJIS['file'] + ' ' if show_emojis else ''
        else:
            continue

        color = get_depth_color(depth, show_emojis)
        print(f"{prefix}{color}{connector} {icon}{entry}{Colors.ENDC}")

        if is_dir:
            extension = '    ' if is_last_item else '│   ' if vertical_connectors else '    '
            generate_tree_map(entry_path, prefix + extension, depth + 1, stats, update_progress, **config)
        elif show_files:
            displayed_files += 1
            if file_limit is not None and displayed_files >= file_limit:
                if show_files:
                    print(f"{prefix}│   ... and {len(entries) - displayed_files} more files")
                break

    if update_progress:
        update_progress()

    return stats


def count_sub_items_in_directory(directory, show_hidden):
    subfolders = 0
    subfiles = 0
    for entry in os.listdir(directory):
        if not show_hidden and entry.startswith('.'):
            continue
        entry_path = os.path.join(directory, entry)
        if os.path.isdir(entry_path):
            subfolders += 1
        else:
            subfiles += 1
    return subfolders, subfiles



if __name__ == '__main__':
    while True:
        setup_environment()
        config = load_config()

        root_directory = input("📂 Enter the path to the root directory: ")
        if not os.path.exists(root_directory):
            print(f"{Colors.RED}Error: The directory '{root_directory}' does not exist.{Colors.ENDC}")
            continue

        config['max_depth'] = validate_integer("📏  How many folders deep should the search go?", str(config.get('max_depth', 0)))
        config['show_files'] = validate_yes_no("📄  Do you want to see file names?", 'yes' if config.get('show_files', True) else 'no')
        config['show_hidden'] = validate_yes_no("🕵️  Do you want to display hidden files?", 'yes' if config.get('show_hidden', False) else 'no')
        config['ascii_style'] = prompt_with_default("✍️  Choose an ASCII style (basic/plus_minus/pipes_dashes/double_lines)", config.get('ascii_style', 'basic')).lower()
        config['vertical_connectors'] = validate_yes_no("🔗  Do you want to add vertical connectors?", 'yes' if config.get('vertical_connectors', False) else 'no')
        config['show_emojis'] = validate_yes_no("😊  Do you want to use emojis?", 'yes' if config.get('show_emojis', False) else 'no')
        config['count_sub_items'] = validate_yes_no("🔢  Do you want to count sub items?", 'yes' if config.get('count_sub_items', False) else 'no')
        export_option = validate_yes_no("💾  Do you want to export the tree map?", 'yes' if config.get('export_option', False) else 'no')

        if export_option:
            config['export_format'] = prompt_with_default("📄  Choose export format (json/markdown/text)", config.get('export_format', 'text')).lower()

        create_ignore_file()
        create_output_directory()

        total_folders = sum([len(dirs) for _, dirs, _ in os.walk(root_directory)])
        current_folder = [0]

        def update_progress():
            current_folder[0] += 1
            print_progress_spinner(current_folder[0], total_folders)

        stats = generate_tree_map(root_directory, update_progress=update_progress, **config)

        print("\nStatistics:")
        print(tabulate_stats(stats))

        if export_option:
            export_tree_map(root_directory, stats, config['export_format'], **config)

        save_config(config)

        run_again = validate_yes_no("🔄 Do you want to run the script again?", 'no')
        if not run_again:
            break
