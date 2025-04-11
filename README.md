# discordcli

A command-line interface (CLI) tool for sending messages to Discord group channel webhooks. This tool allows you to manage webhooks, send messages, and maintain a history of sent messages.

## Requirements
- Python 3.6 or higher
- pip or Homebrew package manager

## Installation

### Using Homebrew (Recommended)
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
- Broadcast messages to multiple webhooks simultaneously
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

### Broadcast Messages
```bash
diss broadcast "Your message"  # Send to all registered webhooks
diss b "Your message"         # Short form of broadcast command
echo "message" | diss         # Pipe a message to all webhooks
```

### Webhook Management
```bash
diss addhook "<webhook_url>" "<n>"    # Add a new webhook
diss deletehook "<n>" (or dh)         # Delete a webhook
diss listhooks (or lh)                   # List all webhooks
diss hook "<n>"                       # Set default webhook
diss whathook (or wh)                    # Show current webhook
diss webhook add <url>        # Add a new webhook
diss webhook remove <url>     # Remove a webhook
diss webhook list            # List all webhooks
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

## Troubleshooting

### Common Issues

1. **Command not found**: If you installed via Homebrew and get "command not found", try:
   ```bash
   brew doctor
   brew link disscli
   ```

2. **Permission denied**: Make sure you have write permissions in your home directory for the database and config files.

3. **Invalid webhook**: Ensure your webhook URL is valid and hasn't expired.

## Development

### Setting Up Development Environment
1. Clone the repository:
   ```bash
   git clone https://github.com/Trevogre/discordcli.git
   cd discordcli
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

### Running Tests
```bash
pytest
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License
This project is licensed under the MIT License.
