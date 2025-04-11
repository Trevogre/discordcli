import os
import json
import argparse
import sqlite3
import requests
import sys
import signal

# Allow overriding paths for testing
CONFIG_PATH = os.getenv('DISSCLI_CONFIG_PATH', os.path.expanduser("~/.dissconfig"))
DB_PATH = os.getenv('DISSCLI_DB_PATH', os.path.expanduser("~/.disscli_history.db"))

# Ignore SIGPIPE and handle BrokenPipeError gracefully
signal.signal(signal.SIGPIPE, signal.SIG_DFL)

# Add these constants at the top level after the existing constants
COMMAND_ALIASES = {
    "ls": "list",
    "lh": "listhooks",
    "wh": "whathook",
    "su": "setuser",
    "who": "whoami",
    "dh": "deletehook",
    "dl": "deletelogs"
}

def load_config():
    # Don't expand the path - use the exact CONFIG_PATH value
    if not os.path.exists(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)


def init_db():
    # Create the database file and parent directory if they don't exist
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if not os.path.exists(DB_PATH):
        open(DB_PATH, 'a').close()

    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Create tables if they don't exist
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                mentions TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS hooks (
                name TEXT PRIMARY KEY,
                webhook_url TEXT NOT NULL,
                is_default INTEGER DEFAULT 0
            )
            """
        )
        # Verify tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        if 'messages' in tables and 'hooks' in tables:
            print("Database initialized successfully.")
        else:
            print("Error: Database initialization failed.")


def print_help_message():
    print("Error: No message provided or invalid command.")
    print("\nAvailable commands:")
    print("  diss \"<message>\" - Send a message to Discord.")
    print("  diss list (ls) - List previously sent messages.")
    print("  diss addhook \"<webhook>\" \"<name>\" - Add a new webhook.")
    print("  diss deletehook <name> (dh) - Delete an existing webhook.")
    print("  diss deletelogs (dl) - Delete all message logs.")
    print("  diss listhooks (lh) - List all hooks.")
    print("  diss hook <name> - Set the current hook.")
    print("  diss whathook (wh) - Show the current hook name.")
    print("  diss users - List users that have been messaged.")
    print("  diss setuser <username> (su) - Set a custom username.")
    print("  diss whoami (who) - Show the current username.")
    print("  diss exportconfig [file_path] - Export configuration to the specified file (defaults to ~/dissconfig.json).")
    print("  diss importconfig [file_path] - Import configuration from the specified file (defaults to ~/dissconfig.json).")


def get_db_connection():
    return sqlite3.connect(DB_PATH)


def add_hook(name, webhook_url):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM hooks WHERE name = ?", (name,))
        if cursor.fetchone():
            print(f"Error: A hook with the name '{name}' already exists.")
            return

        # Check if this is the first hook
        cursor.execute("SELECT COUNT(*) FROM hooks")
        is_first_hook = cursor.fetchone()[0] == 0

        # Add the hook
        cursor.execute("INSERT INTO hooks (name, webhook_url, is_default) VALUES (?, ?, ?)", 
                      (name, webhook_url, 1 if is_first_hook else 0))
        print(f"Hook '{name}' added successfully.")
        if is_first_hook:
            print(f"Hook '{name}' set as default since it's the only hook.")


def delete_hook(name):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT is_default FROM hooks WHERE name = ?", (name,))
        result = cursor.fetchone()
        
        if not result:
            print(f"Error: No hook found with the name '{name}'.")
            return
        
        is_default = result[0]
        cursor.execute("DELETE FROM hooks WHERE name = ?", (name,))
        
        if is_default:
            cursor.execute("SELECT name FROM hooks LIMIT 1")
            new_default = cursor.fetchone()
            if new_default:
                cursor.execute("UPDATE hooks SET is_default = 1 WHERE name = ?", (new_default[0],))
                print(f"Deleted default hook '{name}'. New default hook set to '{new_default[0]}'.")
            else:
                print(f"Deleted default hook '{name}'. No other hooks available to set as default.")
        else:
            print(f"Hook '{name}' deleted successfully.")


def list_hooks():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, is_default FROM hooks")
        rows = cursor.fetchall()
        for name, is_default in rows:
            default_flag = " (default)" if is_default else ""
            print(f"{name}{default_flag}")


def set_default_hook(name):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM hooks WHERE name = ?", (name,))
        if not cursor.fetchone():
            print(f"Error: No hook found with the name '{name}'.")
            return

        cursor.execute("UPDATE hooks SET is_default = 0")
        cursor.execute("UPDATE hooks SET is_default = 1 WHERE name = ?", (name,))
        print(f"Hook '{name}' is now the default.")


def get_default_hook():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM hooks WHERE is_default = 1")
        row = cursor.fetchone()
        return row[0] if row else None


def get_hook_url(name):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT webhook_url FROM hooks WHERE name = ?", (name,))
        row = cursor.fetchone()
        return row[0] if row else None


def list_users():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT mentions FROM messages WHERE mentions IS NOT NULL")
        rows = cursor.fetchall()
        users = set()
        for row in rows:
            users.update(row[0].split(","))
        for user in users:
            print(user)


def save_message(message, mentions):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (message, mentions) VALUES (?, ?)",
            (message, ",".join(mentions) if mentions else None),
        )


def list_messages():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT message, mentions FROM messages")
        return cursor.fetchall()


def delete_logs():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM messages")
        deleted_count = cursor.rowcount
        print(f"Successfully deleted {deleted_count} message logs.")


def send_message(webhook_url, username, avatar_url, message):
    mentions = [word for word in message.split() if word.startswith("@")]
    payload = {
        "content": message,
        "username": username,
        "avatar_url": avatar_url,
    }
    response = requests.post(webhook_url, json=payload)
    if response.status_code == 204:
        save_message(message, mentions)
        print("Message sent successfully!")
    else:
        print(f"Failed to send message: {response.status_code} {response.text}")


def set_user(username):
    config = load_config()
    config["username"] = username
    save_config(config)
    print(f"Username set to '{username}'.")


def whoami():
    config = load_config()
    username = config.get("username", "DissBot")
    print(f"Current username: {username}")


def handle_piped_input():
    try:
        # Check if there's input on stdin
        if not sys.stdin.isatty():
            # Read piped input
            piped_message = sys.stdin.read().strip()
            if piped_message:
                # Print the original output to stdout
                print(piped_message)
                # Return formatted as code block
                return f"```\n{piped_message}\n```"
    except (IOError, BrokenPipeError):
        # Silently handle pipe errors
        sys.stderr.close()
    return None


def export_config(file_path):
    config = load_config()
    try:
        with open(file_path, "w") as f:
            json.dump(config, f, indent=4)
        print(f"Configuration exported to '{file_path}'.")
    except Exception as e:
        print(f"Error exporting configuration: {e}")


def import_config(file_path):
    try:
        with open(file_path, "r") as f:
            config = json.load(f)
        save_config(config)
        print(f"Configuration imported from '{file_path}'.")
    except Exception as e:
        print(f"Error importing configuration: {e}")


def main():
    # Initialize database first
    init_db()
    
    # First check if we're dealing with a subcommand or a message
    import sys

    # Define known subcommands
    known_subcommands = ["addhook", "listhooks", "hook", "whathook", "users", "list", "setuser", "whoami", "exportconfig", "importconfig", "deletehook", "deletelogs"]
    
    # First, check if the first argument is an alias and replace it
    if len(sys.argv) > 1 and sys.argv[1] in COMMAND_ALIASES:
        sys.argv[1] = COMMAND_ALIASES[sys.argv[1]]
    
    # Now check if we're dealing with a subcommand or a message
    if len(sys.argv) > 1 and sys.argv[1] in known_subcommands:
        # Use normal argparse for subcommands
        parser = argparse.ArgumentParser(description="Send messages to Discord via webhooks.")
        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Subcommand for adding a hook
        addhook_parser = subparsers.add_parser("addhook", help="Add a new webhook")
        addhook_parser.add_argument("webhook", help="The webhook URL")
        addhook_parser.add_argument("name", help="The name of the webhook")

        # Subcommand for deleting a hook
        deletehook_parser = subparsers.add_parser("deletehook", help="Delete an existing webhook")
        deletehook_parser.add_argument("name", help="The name of the webhook to delete")

        # Subcommand for deleting logs
        subparsers.add_parser("deletelogs", help="Delete all message logs")

        # Subcommand for listing hooks
        subparsers.add_parser("listhooks", help="List all hooks")

        # Subcommand for setting the default hook
        hook_parser = subparsers.add_parser("hook", help="Set the current hook")
        hook_parser.add_argument("name", help="The name of the hook to set as default")

        # Subcommand for showing the current hook
        subparsers.add_parser("whathook", help="Show the current hook name")

        # Subcommand for listing users
        subparsers.add_parser("users", help="List users that have been messaged")

        # Subcommand for listing messages
        subparsers.add_parser("list", help="List previously sent messages")

        # Subcommand for setting a custom username
        setuser_parser = subparsers.add_parser("setuser", help="Set a custom username")
        setuser_parser.add_argument("username", help="The custom username to set")

        # Subcommand for showing the current username
        subparsers.add_parser("whoami", help="Show the current username")

        # Subcommand for exporting configuration
        exportconfig_parser = subparsers.add_parser("exportconfig", help="Export configuration to a file")
        exportconfig_parser.add_argument("file_path", nargs="?", default=os.path.expanduser("~/dissconfig.json"), 
                                       help="The file path to export the configuration to (defaults to ~/dissconfig.json)")

        # Subcommand for importing configuration
        importconfig_parser = subparsers.add_parser("importconfig", help="Import configuration from a file")
        importconfig_parser.add_argument("file_path", nargs="?", default=os.path.expanduser("~/dissconfig.json"),
                                       help="The file path to import the configuration from (defaults to ~/dissconfig.json)")

        args = parser.parse_args()
        args.message = None
    else:
        # If no subcommand is provided, treat all arguments as a potential message
        parser = argparse.ArgumentParser(description="Send messages to Discord via webhooks.")
        parser.add_argument("message", nargs="*", help="The message to send")
        
        try:
            args = parser.parse_args()
            # Check for piped input first
            piped_message = handle_piped_input()
            if piped_message:
                args.message = piped_message
            elif args.message:
                args.message = " ".join(args.message)
            else:
                args.message = None
                print_help_message()
                return
            args.command = None
        except SystemExit:
            # This happens when parsing fails
            args = argparse.Namespace()
            args.message = None
            args.command = None
            print("Error: Messages must be wrapped in quotes.")
            print('Example: diss "your message here"')
            return

    config = load_config()

    if args.command == "addhook":
        add_hook(args.name, args.webhook)
        return

    if args.command == "listhooks":
        list_hooks()
        return

    if args.command == "hook":
        set_default_hook(args.name)
        return

    if args.command == "whathook":
        current_hook = get_default_hook()
        if current_hook:
            print(f"Current hook: {current_hook}")
        else:
            print("No default hook set.")
        return

    if args.command == "users":
        list_users()
        return

    if args.command == "list":
        messages = list_messages()
        for message, mentions in messages:
            print(f"Message: {message}")
            if mentions:
                print(f"Mentions: {mentions}")
        return

    if args.command == "setuser":
        set_user(args.username)
        return

    if args.command == "whoami":
        whoami()
        return

    if args.command == "exportconfig":
        export_config(args.file_path)
        return

    if args.command == "importconfig":
        import_config(args.file_path)
        return

    if args.command == "deletehook":
        delete_hook(args.name)
        return

    if args.command == "deletelogs":
        delete_logs()
        return

    if args.message:
        # Default behavior: send a message
        webhook_url = get_hook_url(get_default_hook())

        if not webhook_url:
            print("Error: No webhook configured. Either:")
            print("  1. Use 'addhook' to add one and 'hook' to set it as default.")
            return

        username = config.get("username", "DissBot")
        avatar_url = config.get("avatar_url")

        send_message(webhook_url, username, avatar_url, args.message)
        return

    if args.message is None:
        print_help_message()
        return

    print_help_message()
    return


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(0)