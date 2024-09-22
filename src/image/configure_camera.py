# scripts/image/configure_camera.py

import libcamera
# from scripts.image.set_hdr_status import set_hdr_state  # Importing HDR functions
from src.overlay.add_to_overlay_data import add_to_overlay_data

def configure_camera(picam2, config, daylight, lux=None):
    focus_mode = libcamera.controls.AfModeEnum.Manual if config['camera_settings']['focus_mode'] == 'manual' else libcamera.controls.AfModeEnum.Auto  # type: ignore
    lens_position = config['camera_settings']['lens_position'] if config['camera_settings']['focus_mode'] == 'manual' else None

    quality = config['camera_settings']['image_quality']
    add_to_overlay_data('Quality', quality)  # Add the quality to the overlay data
    # Set common controls
    controls = {
        "AwbEnable": config['camera_settings']['awb_enable'],
        "AwbMode": getattr(libcamera.controls.AwbModeEnum, config['camera_settings']['awb_mode']),  # type: ignore
        "AfMode": focus_mode,
        "LensPosition": lens_position,
        "ColourGains": tuple(config['camera_settings']['colour_gains_day']) if daylight else tuple(config['camera_settings']['colour_gains_night']),
    }
        
    shutter_speed = config['camera_settings']['shutter_speed_night']
    iso = config['camera_settings']['iso_night']

    if daylight:
        # Ensure auto exposure is enabled
        controls["AeEnable"] = True
        # Remove any manual exposure settings
        controls.pop("ExposureTime", None)
        controls.pop("AnalogueGain", None)
        shutter_speed = "auto"
        iso = "auto"
    else:
        # Disable auto exposure and set manual exposure settings
        controls["AeEnable"] = False
        controls["AwbEnable"] = False  # Only set at night
        if (shutter_speed is not None) and (iso is not None):
            controls["ExposureTime"] = int(shutter_speed)
            controls["AnalogueGain"] = iso or 1.0
            
    add_to_overlay_data('Iso', iso)
    add_to_overlay_data('Shutterspeed', shutter_speed) 

    # Apply exposure compensation for daylight to brighten images if exposure_value is set in config
    exposure_value = config['camera_settings'].get('exposure_value')  # Safely fetch the exposure_value or None if not set
    if daylight and exposure_value is not None:
        controls["ExposureValue"] = exposure_value  # Apply exposure compensation

    return picam2.create_still_configuration(
        main={"size": tuple(config['camera_settings']['main_size'])},
        display=None,
        controls=controls
    )