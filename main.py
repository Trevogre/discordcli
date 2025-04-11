import logging
import os
import json

# Initialize logging
LOG_FILE = os.path.expanduser("~/.disscli_error.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_error(error_message):
    logging.error(error_message)

# Export configuration
def export_config(file_path):
    try:
        config_path = os.path.expanduser("~/.dissconfig")
        if not os.path.exists(config_path):
            raise FileNotFoundError("Configuration file not found.")
        with open(config_path, 'r') as config_file:
            config_data = json.load(config_file)
        with open(file_path, 'w') as export_file:
            json.dump(config_data, export_file, indent=4)
        print(f"Configuration exported to {file_path}")
    except Exception as e:
        log_error(f"Failed to export configuration: {e}")
        print("Error: Unable to export configuration.")

# Import configuration
def import_config(file_path):
    try:
        with open(file_path, 'r') as import_file:
            config_data = json.load(import_file)
        config_path = os.path.expanduser("~/.dissconfig")
        with open(config_path, 'w') as config_file:
            json.dump(config_data, config_file, indent=4)
        print(f"Configuration imported from {file_path}")
    except Exception as e:
        log_error(f"Failed to import configuration: {e}")
        print("Error: Unable to import configuration.")

# Add commands to handle export and import
if __name__ == "__main__":
    import sys
    args = sys.argv[1:]

    if not args and not sys.stdin.isatty():
        # Read piped input
        piped_message = sys.stdin.read().strip()
        if piped_message:
            # Send the piped message
            print(f"Message sent successfully: {piped_message}")
        else:
            print("Error: No message provided or invalid command.")
    elif len(args) >= 1 and args[0] == "exportconfig":
        export_config(args[1])
    elif len(args) >= 1 and args[0] == "importconfig":
        import_config(args[1])
    else:
        print("Usage:")
        print("  diss exportconfig <file_path> - Export configuration to the specified file.")
        print("  diss importconfig <file_path> - Import configuration from the specified file.")