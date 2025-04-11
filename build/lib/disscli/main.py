import os
import json
import argparse
import sqlite3
import requests
import sys
import signal
from dotenv import load_dotenv

CONFIG_PATH = os.path.expanduser("~/.dissconfig")
DB_PATH = os.path.expanduser("~/.disscli_history.db")
ENV_PATH = os.path.join(os.getcwd(), ".env")  # Path to .env file in current directory

# Ignore SIGPIPE and handle BrokenPipeError gracefully
signal.signal(signal.SIGPIPE, signal.SIG_DFL)


def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)


def init_db():
    print("Initializing database...", flush=True)
    
    # Create the database file if it doesn't exist
    if not os.path.exists(DB_PATH):
        print("Database file doesn't exist. Creating it...", flush=True)
        # Create the parent directory if it doesn't exist
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        # Create an empty file
        open(DB_PATH, 'a').close()
    
    # Check if the database is empty
    if os.path.getsize(DB_PATH) == 0:
        print("Database file exists but is empty. Initializing tables...", flush=True)
    else:
        print("Database file exists. Checking tables...", flush=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                mentions TEXT
            )
            """
        )
        print("'messages' table checked/created.", flush=True)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS hooks (
                name TEXT PRIMARY KEY,
                webhook_url TEXT NOT NULL,
                is_default INTEGER DEFAULT 0
            )
            """
        )
        print("'hooks' table checked/created.", flush=True)
        conn.commit()
        print("Database initialized successfully.", flush=True)
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}", flush=True)
    finally:
        conn.close()

    # Verify tables exist
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"Existing tables: {tables}", flush=True)
    conn.close()


def add_hook(name, webhook_url):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM hooks WHERE name = ?", (name,))
    if cursor.fetchone():
        print(f"Error: A hook with the name '{name}' already exists.")
        conn.close()
        return

    cursor.execute("INSERT INTO hooks (name, webhook_url) VALUES (?, ?)", (name, webhook_url))
    conn.commit()
    conn.close()
    print(f"Hook '{name}' added successfully.")


def list_hooks():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, is_default FROM hooks")
    rows = cursor.fetchall()
    conn.close()
    for name, is_default in rows:
        default_flag = " (default)" if is_default else ""
        print(f"{name}{default_flag}")


def set_default_hook(name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM hooks WHERE name = ?", (name,))
    if not cursor.fetchone():
        print(f"Error: No hook found with the name '{name}'.")
        conn.close()
        return

    cursor.execute("UPDATE hooks SET is_default = 0")
    cursor.execute("UPDATE hooks SET is_default = 1 WHERE name = ?", (name,))
    conn.commit()
    conn.close()
    print(f"Hook '{name}' is now the default.")


def get_default_hook():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM hooks WHERE is_default = 1")
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def get_webhook_from_env():
    """Read webhook URL from .env file if it exists"""
    if os.path.exists(ENV_PATH):
        load_dotenv(ENV_PATH)
        webhook_url = os.getenv("WEBHOOK_URL")
        if webhook_url:
            return webhook_url.strip('"')  # Remove quotes if present
    return None


def get_hook_url(name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT webhook_url FROM hooks WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def list_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT mentions FROM messages WHERE mentions IS NOT NULL")
    rows = cursor.fetchall()
    conn.close()
    users = set()
    for row in rows:
        users.update(row[0].split(","))
    for user in users:
        print(user)


def save_message(message, mentions):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (message, mentions) VALUES (?, ?)",
        (message, ",".join(mentions) if mentions else None),
    )
    conn.commit()
    conn.close()


def list_messages():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT message, mentions FROM messages")
    rows = cursor.fetchall()
    conn.close()
    return rows


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
    if not sys.stdin.isatty():
        # Read piped input
        piped_message = sys.stdin.read().strip()
        if piped_message:
            return f"```\n{piped_message}\n```"
    return None


def main():
    # First check if we're dealing with a subcommand or a message
    import sys

    # Define known subcommands
    known_subcommands = ["addhook", "listhooks", "hook", "whathook", "users", "list", "setuser", "whoami"]

    # Check if first argument is a known subcommand
    if len(sys.argv) > 1 and sys.argv[1] in known_subcommands:
        # Use normal argparse for subcommands
        parser = argparse.ArgumentParser(description="Send messages to Discord via webhooks.")
        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Subcommand for adding a hook
        addhook_parser = subparsers.add_parser("addhook", help="Add a new webhook")
        addhook_parser.add_argument("webhook", help="The webhook URL")
        addhook_parser.add_argument("name", help="The name of the webhook")

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

        args = parser.parse_args()
        args.message = None
    else:
        # If no subcommand is provided, treat all arguments as the message
        parser = argparse.ArgumentParser(description="Send messages to Discord via webhooks.")
        parser.add_argument("message", nargs="*", help="The message to send")
        args = parser.parse_args()

        # Join all arguments into a single message string only if quoted
        args.message = " ".join(args.message) if args.message and len(args.message) > 0 else None
        args.command = None

    piped_message = handle_piped_input()
    if piped_message:
        args.message = piped_message
        args.command = None

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

    if args.message:
        # Default behavior: send a message
        webhook_url = get_hook_url(get_default_hook())

        if not webhook_url:
            webhook_url = get_webhook_from_env()
            if webhook_url:
                print("Using webhook URL from .env file")
            else:
                print("Error: No webhook configured. Either:")
                print("  1. Use 'addhook' to add one and 'hook' to set it as default, or")
                print("  2. Add WEBHOOK_URL to your .env file")
                return

        username = config.get("username", "DissBot")
        avatar_url = config.get("avatar_url")

        send_message(webhook_url, username, avatar_url, args.message)
        return

    print("Error: No message provided or invalid command.")
    print("\nAvailable commands:")
    print("  diss \"<message>\" - Send a message to Discord.")
    print("  diss list - List previously sent messages.")
    print("  diss addhook \"<webhook>\" \"<name>\" - Add a new webhook.")
    print("  diss listhooks - List all hooks.")
    print("  diss hook <name> - Set the current hook.")
    print("  diss whathook - Show the current hook name.")
    print("  diss users - List users that have been messaged.")
    print("  diss setuser <username> - Set a custom username.")
    print("  diss whoami - Show the current username.")
    return


if __name__ == "__main__":
    init_db()
    try:
        main()
    except BrokenPipeError:
        sys.exit(0)