# Converting `disscli` to a Discord Bot

This document outlines the steps required to convert the `disscli` CLI tool into a Discord bot for enhanced functionality, such as programmatically looking up users and sending mentions.

## Why Convert to a Bot?

Webhooks are limited to sending messages and cannot query Discord's user database. By converting `disscli` to a bot, you can:

1. Programmatically look up users by their username and discriminator (e.g., `username#1234`).
2. Send mentions that highlight users without manually entering user IDs.
3. Access additional Discord features, such as role mentions, channel management, and more.

## Steps to Convert `disscli` to a Bot

### 1. Create a Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click "New Application" and give your bot a name.
3. Navigate to the "Bot" tab and click "Add Bot."
4. Copy the bot token and store it securely (you'll need it for authentication).

### 2. Add the Bot to Your Server

1. Go to the "OAuth2" tab in the Developer Portal.
2. Under "OAuth2 URL Generator," select the following scopes:
   - `bot`
3. Under "Bot Permissions," select the following permissions:
   - `View Members`
   - `Send Messages`
   - `Mention Everyone`
4. Copy the generated URL and open it in your browser.
5. Select your server and authorize the bot.

### 3. Update `disscli` to Use the Discord API

1. Install the `discord.py` library:
   ```bash
   pip install discord.py
   ```

2. Update the `main.py` file to include bot functionality:
   - Use the `discord.Client` class to interact with Discord.
   - Replace the webhook functionality with bot commands.

3. Add a command to look up users:
   ```python
   @client.event
   async def on_message(message):
       if message.content.startswith("!lookup"):
           username = message.content.split(" ")[1]
           for member in message.guild.members:
               if member.name == username:
                   await message.channel.send(f"User ID for {username}: {member.id}")
   ```

### 4. Cache User Data

To avoid repeated API calls, cache user data locally:

1. Create a database table to store user IDs.
2. Update the cache whenever the bot starts or a new user joins the server.

### 5. Replace Mentions in Messages

1. Parse `@username` in messages.
2. Replace it with `<@USER_ID>` using the cached user data.

### 6. Run the Bot

1. Create a new entry point for the bot in `setup.py`:
   ```python
   entry_points={
       "console_scripts": [
           "dissbot=disscli.bot:main",
       ]
   }
   ```
2. Run the bot:
   ```bash
   dissbot
   ```

## Future Enhancements

- Add support for role mentions (`<@&ROLE_ID>`).
- Implement slash commands for a more modern Discord experience.
- Add logging and error handling for better debugging.

By converting `disscli` to a bot, you can unlock the full potential of Discord's API and provide a richer user experience.