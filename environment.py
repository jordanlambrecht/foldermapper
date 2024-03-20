import os
import subprocess
import sys

# Define the path to the virtual environment
venv_path = os.path.join(os.path.dirname(__file__), 'venv')

# Function to activate the virtual environment
def activate_venv():
    if sys.platform == 'win32':
        activate_script = os.path.join(venv_path, 'Scripts', 'activate.bat')
    else:
        activate_script = os.path.join(venv_path, 'bin', 'activate')
    os.system(f'source {activate_script}' if sys.platform != 'win32' else activate_script)

# Function to install required packages
def install_requirements(requirements_file='requirements.txt'):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_file])

# Check if the virtual environment exists, and create it if it doesn't
def setup_environment():
    if not os.path.exists(venv_path):
        subprocess.check_call([sys.executable, '-m', 'venv', venv_path])
    activate_venv()
    install_requirements()
