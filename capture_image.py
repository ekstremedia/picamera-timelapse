import json
import os
import time
import yaml
from src.log.logger import get_logger, log, log_warning, log_error
from src.image.evaluate_light import evaluate_light
from picamera2 import Picamera2
from src.image.configure_camera import configure_camera
from datetime import datetime
from src.overlay.add_image_overlay import overlay_image_with_text

# Set the config path
BASE_PATH = os.path.dirname(__file__) 
CONFIG_FILE = os.path.join(BASE_PATH, 'config.yaml')
METADATA_FILE = os.path.join(BASE_PATH, 'data', 'capture_metadata.json')

# Create a logger instance for capture_image.py
logger = get_logger('capture_image.log', echo_to_console=True)

def read_config(config_path=CONFIG_FILE):
    """
    Reads the configuration from a YAML file.
    
    Parameters:
        config_path (str): The path to the configuration file.
    
    Returns:
        dict: The configuration dictionary.
    """
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                log(logger, f"Configuration loaded from {config_path}")
                return config
        except yaml.YAMLError as e:
            log_error(logger, f"Error parsing configuration file: {e}")
    else:
        log_error(logger, f"Configuration file {config_path} not found.")
    
    return {}

def save_metadata(metadata):
    """
    Saves the captured metadata to a JSON file.

    Parameters:
        metadata (dict): The metadata dictionary to save.
    """
    try:
        with open(METADATA_FILE, 'w') as f:
            json.dump(metadata, f, indent=4)
        # print(f"Metadata saved to {METADATA_FILE}")
    except Exception as e:
        log_error(f"Error saving metadata: {e}")
        
def capture_image(config):
    try:
        log(logger, "Starting image capture...")

        # Get the Lux reading without passing picam2
        lux = evaluate_light()
        log(logger, f"Lux value: {lux}")

        # Initialize the camera
        picam2 = Picamera2()
        log(logger, "Camera initialized.")

        # Configure the camera
        still_config = configure_camera(picam2, config, lux)
        
        picam2.configure(still_config)
        log(logger, "Camera configured for still capture.")

        # Start the camera
        picam2.start()
        log(logger, "Camera started for image capture.")

        # Allow time for auto exposure to adjust
        time.sleep(2)  # Increase if necessary

        # # Optionally, capture and discard initial frames
        # for _ in range(3):
        #     picam2.capture_request().release()

        now = datetime.now()
        dir_name = os.path.join(config['image_output']['root_folder'], now.strftime(config['image_output']['folder_structure']))
        os.makedirs(dir_name, exist_ok=True)
        time_format = config['image_output'].get('filename_time_format', '%Y_%m_%d_%H_%M_%S')
        file_name = os.path.join(dir_name, f"{config['image_output']['filename_prefix']}{now.strftime(time_format)}.{config['image_output']['image_extension']}")

        # Capture request and metadata
        request = picam2.capture_request()
        if request:
            image = request.make_image("main")
            metadata = request.get_metadata()
            request.release()
            save_metadata(metadata)
        else:
            raise ValueError("Failed to capture request, request is None")
        
        # Save the image file
        image.save(file_name)
        log(logger, f"Image saved to {file_name}")

        # Stop the camera after capturing the image
        picam2.stop()
        log(logger, "Camera stopped after image capture.")

        overlay_image_with_text(file_name, output_image_path=file_name)

        # Update symlink to the latest image
        # Create or update symlink to the latest image
        symlink_path = config['image_output']['status_file']
        try:
            if os.path.islink(symlink_path) or os.path.exists(symlink_path):
                os.remove(symlink_path)
            os.symlink(file_name, symlink_path)

        except Exception as e:
            log_error(f"Error updating symlink: {e}")
            if logger:
                log(logger, f"Error updating symlink: {e}")   

    except Exception as e:
        log_error(logger, f"Error during image capture: {e}")
        
if __name__ == "__main__":
    try:
        # Load the configuration
        config = read_config()

        # If the config is empty, warn the user and use defaults
        if not config:
            log_warning(logger, "Configuration is empty or missing, using default settings.")

        # Capture the image with the loaded configuration
        capture_image(config)
        
    except Exception as e:
        log_error(logger, f"Fatal error in main execution: {e}")
