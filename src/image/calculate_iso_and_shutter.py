# src/image/calculate_iso_and_shutter.py
from src.log.logger import get_logger, log

logger = get_logger('calculate_iso_and_shutter.log', echo_to_console=True)

def calculate_iso_and_shutter(lux, config):
    """
    Calculate ISO and shutter speed based on the Lux value.
    """
    log(logger, f"Calculating ISO and shutter speed for Lux value: {lux}")

    # Define Lux thresholds
    lux_day_night_threshold = 5.0   # Start manual adjustments below this Lux
    lux_night_min = 0.5             # Minimum Lux value (darkest night)

    # Get ISO and shutter speed settings from config
    iso_day = config['camera_settings']['iso_day']      # Auto ISO during the day
    iso_night = config['camera_settings']['iso_night']
    shutter_speed_day = 0                              # 0 for auto-exposure during the day
    shutter_speed_start = 119305                        # Start manual shutter speed from here (µs)
    shutter_speed_night = config['camera_settings']['shutter_speed_night']  # Max shutter speed at night

    if lux >= lux_day_night_threshold:
        # Daytime settings
        iso = iso_day
        shutter_speed = shutter_speed_day  # Use auto-exposure
        daylight = True
    elif lux <= lux_night_min:
        # Nighttime settings
        iso = iso_night
        shutter_speed = shutter_speed_night
        daylight = False
    else:
        # Transition period - interpolate between start and night settings
        daylight = False
        # Compute interpolation factor
        factor = (lux_day_night_threshold - lux) / (lux_day_night_threshold - lux_night_min)
        factor = max(0, min(factor, 1))

        # Interpolate ISO
        iso = iso_day + factor * (iso_night - iso_day)
        iso = round(max(iso_day, min(iso, iso_night)), 1)

        # Interpolate shutter speed
        shutter_speed = shutter_speed_start + factor * (shutter_speed_night - shutter_speed_start)
        shutter_speed = int(round(max(shutter_speed_start, min(shutter_speed, shutter_speed_night)), 0))

        # If shutter speed hasn't increased beyond the start point, use auto-exposure
        if shutter_speed <= shutter_speed_start:
            shutter_speed = 0  # Use auto-exposure
            iso = iso_day      # Use auto ISO

    log(logger, f"ISO: {iso}, Shutter Speed: {shutter_speed if shutter_speed else 'auto'}, Daylight: {daylight}")

    # Return None for shutter_speed and iso if auto-exposure is to be used
    return iso if shutter_speed else None, shutter_speed if shutter_speed else None, daylight
