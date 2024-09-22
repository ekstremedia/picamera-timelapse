import os
import json
import time
from picamera2 import Picamera2
from datetime import datetime
import yaml
from src.log.logger import get_logger, log, log_warning
from src.overlay.add_to_overlay_data import add_metadata_to_overlay

# Set base directory for the project (two levels up)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))

# Paths for storing metadata and config
DATA_DIR = os.path.join(BASE_DIR, 'data')
METADATA_FILE = os.path.join(DATA_DIR, 'evaluation_metadata.json')
CONFIG_FILE = os.path.join(BASE_DIR, 'config.yaml')

# Create a logger instance for evaluate_light.py
logger = get_logger('evaluate_light.log', echo_to_console=True)

def read_config():
    """
    Reads the configuration from config.yaml.

    Returns:
        dict: The configuration dictionary.
    """
    with open(CONFIG_FILE, 'r') as config_file:
        return yaml.safe_load(config_file)

def create_directory_if_not_exists(directory):
    """
    Creates the directory if it doesn't already exist.

    Parameters:
        directory (str): The directory path to create.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def save_metadata_to_file(metadata, file_path):
    """
    Saves the metadata to a JSON file.

    Parameters:
        metadata (dict): The metadata to save.
        file_path (str): The file path to save the metadata.
    """
    with open(file_path, 'w') as json_file:
        json.dump(metadata, json_file, indent=4)
    # log(logger, f"Metadata saved to {file_path}")

def load_metadata(file_path):
    """
    Loads metadata from a JSON file.

    Parameters:
        file_path (str): The path to the metadata file.

    Returns:
        dict: The metadata dictionary if file exists, otherwise None.
    """
    if os.path.exists(file_path):
        with open(file_path, 'r') as json_file:
            return json.load(json_file)
    return None

def get_file_age_in_seconds(file_path):
    """
    Gets the age of a file in seconds.

    Parameters:
        file_path (str): The file path.

    Returns:
        int: The age of the file in seconds.
    """
    if os.path.exists(file_path):
        file_mod_time = os.path.getmtime(file_path)
        current_time = time.time()
        return int(current_time - file_mod_time)
    return None
def evaluate_light():
    """
    Evaluates the light level using the camera sensor without saving an image.
    If a camera instance is provided, it will be used; otherwise, a new instance will be created.
    Automatically saves the metadata to a JSON file in the root data directory.
    
    Parameters:
        picam2 (Picamera2): The camera instance to use, or None to create a new instance.
    
    Returns:
        str: The Lux value.
    """
    # Load the configuration
    config = read_config()
    evaluate_every = config.get('image', {}).get('evaluate_light_every', 0)
    log(logger, f"Evaluate light every: {evaluate_every} seconds")

    # Create the data directory if it doesn't exist
    create_directory_if_not_exists(DATA_DIR)

    # Check the file age
    file_age = get_file_age_in_seconds(METADATA_FILE)

    # If file exists and it's been modified recently, use the stored Lux value
    if file_age is not None and evaluate_every > 0 and file_age < evaluate_every:
        metadata = load_metadata(METADATA_FILE)
        if metadata:
            lux = round(metadata.get('Lux', 'N/A'), 1)
            log(logger, f"Returning stored Lux value: {lux} (metadata file age: {file_age} seconds)")
            return lux

    # If the metadata file is old or doesn't exist, evaluate the light again
    log(logger, "Evaluating light level...")

    # Initialize the camera
    picam2 = Picamera2()

    # Configure the camera for minimal preview
    preview_config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(preview_config)

    # Start the camera
    picam2.start()
    time.sleep(1)  # Allow camera to warm up

    # Capture sensor metadata
    metadata = picam2.capture_metadata()

    # Stop the camera
    picam2.stop()
    picam2.close()  # Ensure the camera is properly closed
    log(logger, "Camera stopped after light evaluation.")

    # Extract the Lux value for display purposes
    lux = round(metadata.get('Lux', 'N/A'), 1) if metadata else 'N/A'

    add_metadata_to_overlay(metadata)  # Add the Lux value etc to the overlay data

    # Save metadata to the file
    save_metadata_to_file(metadata, METADATA_FILE)
    
    # Return the Lux value
    return lux

if __name__ == "__main__":
    # Evaluate light level and return Lux value
    log(logger, "MAIN")
    lux = evaluate_light()
