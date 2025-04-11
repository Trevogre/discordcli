# discordcli

A command-line interface (CLI) tool for sending messages to Discord group channel webhooks. This tool allows you to manage webhooks, send messages, and maintain a history of sent messages.

## Installation

### Using Homebrew
```bash
brew tap Trevogre/tap
brew install disscli
```

### Using pip
```bash
pip install disscli
```

## Features
- Add, manage, and delete Discord webhooks
- Send messages to Discord channels via webhooks
- Maintain a history of sent messages with ability to clear history
- List users mentioned in messages
- Command aliases for frequently used commands
- Configuration import/export

## Usage
Run the CLI tool using the `diss` command. Below are some examples of available commands:

### Send a Message
```bash
diss "Your message here"
```

### Webhook Management
```bash
diss addhook "<webhook_url>" "<name>"    # Add a new webhook
diss deletehook "<name>" (or dh)         # Delete a webhook
diss listhooks (or lh)                   # List all webhooks
diss hook "<name>"                       # Set default webhook
diss whathook (or wh)                    # Show current webhook
```

### Message History
```bash
diss list (or ls)                        # List sent messages
diss deletelogs (or dl)                  # Delete all message logs
diss users                               # List mentioned users
```

### User Settings
```bash
diss setuser "<username>" (or su)        # Set a custom username
diss whoami (or who)                     # Show current username
```

### Configuration
```bash
diss exportconfig [file_path]            # Export configuration
diss importconfig [file_path]            # Import configuration
```
The file path defaults to ~/dissconfig.json if not specified.

## Configuration
The tool uses a SQLite database located at `~/.disscli_history.db` to store webhook and message history. Configuration settings, such as the default username, are stored in `~/.dissconfig`.

## License
This project is licensed under the MIT License.
