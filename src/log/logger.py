import logging
import os
import yaml
from logging.handlers import RotatingFileHandler
from colored import fg, attr

# Function to read config.yaml
def read_config():
    config_path = 'config.yaml'
    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    return {}

# Function to check if logging is enabled for a specific script
def is_logging_enabled(script_name):
    config = read_config()
    return config.get('log', {}).get(script_name, False)

def get_logger(log_file_name, echo_to_console=False):
    script_name = log_file_name.replace('.log', '')

    # Check if logging is enabled for the script
    if not is_logging_enabled(script_name):
        return logging.getLogger('dummy')

    log_levels = read_config().get('log', {}).get('levels', [])
    
    # Handle 'all' case or default log levels
    if 'all' in log_levels:
        log_levels = ['info', 'warning', 'error']
    
    # Create 'logs' folder if it does not exist
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file_path = os.path.join(log_dir, log_file_name)
    logger = logging.getLogger(log_file_name)

    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.DEBUG)

    # Formatter for log messages
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    file_handler = RotatingFileHandler(log_file_path, maxBytes=5 * 1024 * 1024, backupCount=3)
    file_handler.setFormatter(formatter)
    
    # Add filter to handle allowed log levels
    class LevelFilter(logging.Filter):
        def filter(self, record):
            return record.levelname.lower() in log_levels

    file_handler.addFilter(LevelFilter())
    logger.addHandler(file_handler)

    # Custom function to apply colors based on log level for console output
    if echo_to_console:
        class ColoredFormatter(logging.Formatter):
            def format(self, record):
                # Define colors for each log level
                if record.levelname == 'INFO':
                    color = fg('green')
                elif record.levelname == 'WARNING':
                    color = fg('yellow')
                elif record.levelname == 'ERROR':
                    color = fg('red')
                else:
                    color = fg('white')
                
                # Reset color at the end
                reset = attr('reset')

                # Format the log entry
                log_message = super(ColoredFormatter, self).format(record)
                
                # Split the log entry into date/time and the rest (level and message)
                log_parts = log_message.split(" - ", 1)
                date_part = log_parts[0]  # This is the date/time part
                rest_of_log = log_parts[1]  # This contains the level and message

                # Apply the color to the level and message part only, leave the date white
                return f"{fg('white')}{date_part} - {color}{rest_of_log}{reset}"



        console_handler = logging.StreamHandler()
        console_formatter = ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        console_handler.setFormatter(console_formatter)
        console_handler.addFilter(LevelFilter())
        logger.addHandler(console_handler)

    return logger

def log(logger, message):
    """Logs an info message (default)."""
    logger.info(message)

def log_warning(logger, message):
    """Logs a warning message."""
    logger.warning(message)

def log_error(logger, message):
    """Logs an error message."""
    logger.error(message)
    
    
