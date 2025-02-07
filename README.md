# Discord Bot

## Overview
This is a modular Discord bot built using discord.py, designed with a flexible cog-based architecture. The bot supports multiple extensions and slash commands.

## Features
- Dynamic cog loading
- Slash command synchronization
- Multiple bot extensions
- Configurable command prefix

## Prerequisites
- Python 3.9+
- discord.py
- python-dotenv
- colorama

## Setup Instructions

1. Clone the repository
   ```bash
   git clone https://github.com/hao511/Discord-Python-Bot-cogs-function.git
   cd discord-bot
   ```

2. Create a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root
   ```
   DISCORD_TOKEN=your_discord_bot_token_here
   ```

## Configuration

### Cogs
The bot loads multiple cogs automatically. To add or remove cogs, modify the `cogslist` in `main.py`:

```python
self.cogslist = [
    "cogs.example",
    # Add or remove cogs as needed
]
```

### Command Prefix
The bot uses two command prefixes:
- Mentions
- `>` (greater than symbol)

## Running the Bot
```bash
python main.py
```


## Logging
The bot provides console logging with timestamps and color-coded messages for different events.

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request
