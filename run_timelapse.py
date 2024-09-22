import os
import subprocess
import time
import yaml
from src.log.logger import get_logger, log, log_warning, log_error
logger = get_logger('run_timelapse.log', echo_to_console=True)

def load_config(config_path):
    """
    Loads the configuration from a YAML file.

    Parameters:
        config_path (str): Path to the config.yaml file.

    Returns:
        dict: The configuration dictionary.
    """
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

if __name__ == "__main__":
    # Load the configuration
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    config = load_config(config_path)

    interval = config['timelapse']['interval']
    
    while True:
        # Start the timer to measure the time taken for capturing the image
        start_time = time.time()
        log(logger, f"Starting a new capture cycle.")
        
        try:
            script_path = os.path.join(os.path.dirname(__file__), 'capture_image.py')
            subprocess.run(['python3', script_path], check=True)
        except subprocess.CalledProcessError as e:
            log(logger, f"Error during image capture: {e}")
        
        # Calculate the time taken to capture the image
        capture_duration = time.time() - start_time
        remaining_sleep = max(0, interval - capture_duration)  # Ensure no negative sleep times

        log(logger, f"Capture took {capture_duration:.2f} seconds. Sleeping for {remaining_sleep:.2f} seconds before next capture.")
        time.sleep(remaining_sleep)
