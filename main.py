import discord
from discord.ext import commands, tasks
from datetime import datetime
from colorama import Back, Fore, Style
import platform
from dotenv import load_dotenv
from collections import defaultdict
import os
from typing import List

# Load environment settings
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Track voice channel time for each member
loyalty_points = defaultdict(int)

class Client(commands.Bot):
    """
    Custom Discord bot client with dynamic cog loading and slash command synchronization.
    
    Attributes:
        cogslist (List[str]): List of cog extensions to load on startup
    """
    def __init__(self):
        """
        Initialize the bot with custom settings:
        - Mentions and '>' as command prefixes
        - All intents enabled
        - Case-insensitive commands
        """
        super().__init__(
            command_prefix=commands.when_mentioned_or('>'),
            intents=discord.Intents.all(),
            case_insensitive=True
        )
        # List of cog extensions to load
        # Add your cogs here
        self.cogslist = [
            "cogs.example",
            #"cogs.yourCogs"
        ]

    async def setup_hook(self):
        """
        Set up bot by loading extensions and synchronizing slash commands.
        """
        # Load all specified cogs
        for ext in self.cogslist:
            try:
                await self.load_extension(ext)
                ext_name = ext.split('.')[-1]
                print(f"[INFO] Extension '{ext_name}' loaded successfully.")
            except Exception as e:
                print(f"[ERROR] Failed to load extension '{ext}': {e}")
        
        print("Synchronizing slash commands...")
        try:
            synced = await self.tree.sync()
            print(f"[INFO] Synchronized {len(synced)} slash commands.")
        except Exception as e:
            print(f"[ERROR] Error synchronizing slash commands: {e}")

    async def on_ready(self):
        """
        Log bot startup information when the bot is ready.
        """
        current_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        prefix = (Back.BLACK + Fore.GREEN + current_time + Back.RESET + Fore.WHITE + Style.BRIGHT)
        print(prefix + " Logged in as " + Fore.YELLOW + self.user.name)
        print(prefix + " Bot ID " + Fore.YELLOW + str(self.user.id))
        print(prefix + " Discord version " + Fore.YELLOW + discord.__version__)
        print(prefix + " Python version " + Fore.YELLOW + str(platform.python_version()))
        print(prefix + " Slash commands synchronized " + Fore.YELLOW + str(len(self.tree.get_commands())) + " commands")

# Create bot client instance
client = Client()

# Run the bot
client.run(TOKEN)
