import logging
import os
import json
import requests

# Initialize logging
LOG_FILE = os.path.expanduser("~/.disscli_error.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_error(error_message):
    logging.error(error_message)

def get_config():
    config_path = os.path.expanduser("~/.dissconfig")
    if not os.path.exists(config_path):
        # Create default config
        config = {"webhooks": []}
        with open(config_path, 'w') as config_file:
            json.dump(config, config_file, indent=4)
        return config
    
    with open(config_path, 'r') as config_file:
        return json.load(config_file)

def save_config(config):
    config_path = os.path.expanduser("~/.dissconfig")
    with open(config_path, 'w') as config_file:
        json.dump(config, config_file, indent=4)

def add_webhook(url):
    try:
        config = get_config()
        if url not in config["webhooks"]:
            config["webhooks"].append(url)
            save_config(config)
            print(f"Webhook added successfully!")
        else:
            print("Webhook already exists!")
    except Exception as e:
        log_error(f"Failed to add webhook: {e}")
        print("Error: Unable to add webhook.")

def list_webhooks():
    try:
        config = get_config()
        if not config["webhooks"]:
            print("No webhooks registered.")
            return
        print("Registered webhooks:")
        for i, url in enumerate(config["webhooks"], 1):
            print(f"{i}. {url}")
    except Exception as e:
        log_error(f"Failed to list webhooks: {e}")
        print("Error: Unable to list webhooks.")

def remove_webhook(url):
    try:
        config = get_config()
        if url in config["webhooks"]:
            config["webhooks"].remove(url)
            save_config(config)
            print("Webhook removed successfully!")
        else:
            print("Webhook not found!")
    except Exception as e:
        log_error(f"Failed to remove webhook: {e}")
        print("Error: Unable to remove webhook.")

def broadcast_message(message):
    try:
        config = get_config()
        if not config["webhooks"]:
            print("No webhooks registered. Add webhooks first.")
            return
        
        success_count = 0
        for webhook_url in config["webhooks"]:
            try:
                response = requests.post(webhook_url, json={"content": message})
                response.raise_for_status()
                success_count += 1
            except requests.exceptions.RequestException as e:
                log_error(f"Failed to send to webhook {webhook_url}: {e}")
        
        if success_count > 0:
            print(f"Message broadcast to {success_count}/{len(config['webhooks'])} webhooks successfully!")
        else:
            print("Failed to broadcast message to any webhooks.")
            
    except Exception as e:
        log_error(f"Failed to broadcast message: {e}")
        print("Error: Unable to broadcast message.")

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
            broadcast_message(piped_message)
        else:
            print("Error: No message provided or invalid command.")
    elif len(args) >= 1:
        cmd = args[0]
        if cmd in ["broadcast", "b"]:
            if len(args) < 2:
                print("Error: Message required for broadcast.")
                print("Usage: diss broadcast <message>")
                print("   or: diss b <message>")
            else:
                broadcast_message(args[1])
        elif cmd == "webhook":
            if len(args) < 2:
                print("Error: Subcommand required for webhook management.")
                print("Usage:")
                print("  diss webhook add <url> - Add a webhook")
                print("  diss webhook remove <url> - Remove a webhook")
                print("  diss webhook list - List all webhooks")
            else:
                subcmd = args[1]
                if subcmd == "add" and len(args) >= 3:
                    add_webhook(args[2])
                elif subcmd == "remove" and len(args) >= 3:
                    remove_webhook(args[2])
                elif subcmd == "list":
                    list_webhooks()
                else:
                    print("Invalid webhook subcommand.")
                    print("Usage:")
                    print("  diss webhook add <url> - Add a webhook")
                    print("  diss webhook remove <url> - Remove a webhook")
                    print("  diss webhook list - List all webhooks")
        elif cmd == "exportconfig":
            export_config(args[1])
        elif cmd == "importconfig":
            import_config(args[1])
        else:
            print("Usage:")
            print("\nBroadcast Commands:")
            print("  diss broadcast <message>  - Send message to all webhooks")
            print("  diss b <message>         - Short form of broadcast")
            print("  echo 'msg' | diss        - Pipe message to all webhooks")
            print("\nWebhook Management:")
            print("  diss webhook add <url>   - Add a webhook")
            print("  diss webhook remove <url> - Remove a webhook")
            print("  diss webhook list        - List all webhooks")
            print("\nConfiguration:")
            print("  diss exportconfig <path> - Export configuration to file")
            print("  diss importconfig <path> - Import configuration from file")