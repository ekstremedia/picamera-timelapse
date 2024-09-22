import os
import json
from src.log.logger import log_error

# Set the path to the overlay data JSON file
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data'))
OVERLAY_DATA_FILE = os.path.join(BASE_DIR, 'overlay_data.json')

# Function to load the overlay data from the JSON file
def load_overlay_data():
    """
    Loads the overlay data from the overlay_data.json file.

    Returns:
        dict: The overlay data dictionary.
    """
    if os.path.exists(OVERLAY_DATA_FILE):
        with open(OVERLAY_DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

# Function to save the overlay data back to the JSON file
def save_overlay_data(data):
    """
    Saves the updated overlay data to the overlay_data.json file.

    Parameters:
        data (dict): The updated overlay data dictionary.
    """
    with open(OVERLAY_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Function to update the overlay data with a new key-value pair
def add_to_overlay_data(key, value):
    """
    Adds or updates a key-value pair in the overlay data.

    Parameters:
        key (str): The key to set in the overlay data.
        value (any): The value associated with the key.
    """
    # Load the existing overlay data
    overlay_data = load_overlay_data()

    # Update the overlay data with the new key-value pair
    overlay_data[key] = value

    # Save the updated overlay data back to the file
    save_overlay_data(overlay_data)

def add_metadata_to_overlay(metadata):
    """
    Extracts relevant metadata and adds it to the overlay data.

    Parameters:
        metadata (dict): The metadata dictionary.
    """
    if metadata:
        # Extract the required values
        overlay_data = {
            "Lux": round(metadata.get('Lux', 'N/A'), 1),
            "ExposureTime": round(metadata.get('ExposureTime', 'N/A'), 1),
            "AnalogueGain": round(metadata.get('AnalogueGain', 'N/A'), 1),
            "DigitalGain": round(metadata.get('DigitalGain', 'N/A'), 1),
            "FrameDuration": round(metadata.get('FrameDuration', 'N/A'), 1),
            "SensorTemperature": round(metadata.get('SensorTemperature', 'N/A'), 1),
            "LensPosition": round(metadata.get('LensPosition', 'N/A'), 1),
            "ColourTemperature": round(metadata.get('ColourTemperature', 'N/A'), 1)
        }

        # Add all the extracted data to the overlay JSON
        add_to_overlay_data("camera_metadata", overlay_data)
    else:
        log_error("No metadata available to add to overlay.")

# Example usage
if __name__ == "__main__":
    # Replace these with your key and value
    key = "example_key"
    value = "example_value"
    
    # Add the key-value pair to the overlay data
    add_to_overlay_data(key, value)
    print(f"Added key: {key} with value: {value} to overlay data.")
