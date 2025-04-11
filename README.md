# discordcli

A command-line interface (CLI) tool for sending messages to Discord group channel webhooks. This tool allows you to manage webhooks, send messages, and maintain a history of sent messages.

## Features
- Add and manage Discord webhooks.
- Send messages to Discord channels via webhooks.
- Maintain a history of sent messages.
- List users mentioned in messages.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/discordcli.git
   cd discordcli
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Initialize the database:
   ```bash
   python -m disscli.main
   ```

## Usage
Run the CLI tool using the `diss` command. Below are some examples of available commands:

### Send a Message
```bash
python -m disscli.main "Your message here"
```

### Add a Webhook
```bash
python -m disscli.main addhook "<webhook_url>" "<name>"
```

### List Webhooks
```bash
python -m disscli.main listhooks
```

### Set Default Webhook
```bash
python -m disscli.main hook "<name>"
```

### List Sent Messages
```bash
python -m disscli.main list
```

### Set a Custom Username
```bash
python -m disscli.main setuser "<username>"
```

### Show Current Username
```bash
python -m disscli.main whoami
```

## Configuration
The tool uses a SQLite database located at `~/.disscli_history.db` to store webhook and message history. Configuration settings, such as the default username, are stored in `~/.dissconfig`.

## License
This project is licensed under the MIT License.
