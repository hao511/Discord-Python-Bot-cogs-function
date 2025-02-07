import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from typing import Dict, List, Set
from datetime import datetime, timedelta

class Poll(commands.Cog, description="Voting System"):
    """
    A Discord bot cog that provides advanced polling functionality.
    
    Supports creating polls with multiple options, single/multiple choice,
    and automatic result generation.
    """
    def __init__(self, bot):
        """
        Initialize the Poll cog.
        
        Args:
            bot (commands.Bot): The Discord bot instance
        """
        self.bot = bot
        self.active_polls: Dict[int, dict] = {}  # Stores ongoing polls
        
    @app_commands.command(name="poll", description="Create a new poll")
    @app_commands.describe(
        title="Poll title",
        options="Options (comma-separated)",
        duration="Poll duration in minutes (default 60)",
        multiple="Allow multiple choices (True/False)",
    )
    async def create_poll(
        self,
        interaction: discord.Interaction,
        title: str,
        options: str,
        duration: int = 60,
        multiple: bool = False
    ):
        """
        Create a new poll with specified parameters.
        
        Args:
            interaction (discord.Interaction): The interaction that triggered the poll
            title (str): The poll's title
            options (str): Comma-separated list of poll options
            duration (int, optional): Poll duration in minutes. Defaults to 60.
            multiple (bool, optional): Allow multiple choice. Defaults to False.
        """
        # Validate options
        option_list = [opt.strip() for opt in options.split(",")]
        if len(option_list) < 2:
            await interaction.response.send_message("At least 2 options required!", ephemeral=True)
            return
        if len(option_list) > 10:
            await interaction.response.send_message("Maximum 10 options allowed!", ephemeral=True)
            return
            
        # Create poll data structure
        poll_data = {
            "title": title,
            "options": option_list,
            "votes": {i: set() for i in range(len(option_list))},
            "multiple": multiple,
            "author_id": interaction.user.id,
            "end_time": datetime.now() + timedelta(minutes=duration),
            "channel_id": interaction.channel.id  # Store the channel where poll was started
        }
        
        # Create display embed
        embed = self.create_poll_embed(poll_data)
        
        # Create poll buttons
        view = PollView(option_list, multiple)
        
        # Send poll message
        await interaction.response.send_message(embed=embed, view=view)
        message = await interaction.original_response()
        
        # Store poll information
        self.active_polls[message.id] = poll_data
        
        # Set poll end timer
        self.bot.loop.create_task(self.end_poll_timer(message.id, duration))
        
    def create_poll_embed(self, poll_data: dict) -> discord.Embed:
        """
        Generate an embed displaying current poll status.
        
        Args:
            poll_data (dict): Dictionary containing poll information
        
        Returns:
            discord.Embed: Embed showing poll details and current votes
        """
        embed = discord.Embed(
            title=f"📊 {poll_data['title']}",
            description="Please click buttons below to vote" + 
                       ("\n(Multiple choices allowed)" if poll_data["multiple"] else ""),
            color=discord.Color.blue()
        )
        
        # Add options and vote counts
        total_votes = sum(len(votes) for votes in poll_data["votes"].values())
        
        for i, option in enumerate(poll_data["options"]):
            votes = len(poll_data["votes"][i])
            percentage = (votes / total_votes * 100) if total_votes > 0 else 0
            bar = "█" * int(percentage / 10) + "░" * (10 - int(percentage / 10))
            
            embed.add_field(
                name=f"{option}",
                value=f"{bar} {votes} votes ({percentage:.1f}%)",
                inline=False
            )
            
        # Add remaining time
        time_left = poll_data["end_time"] - datetime.now()
        minutes_left = int(time_left.total_seconds() / 60)
        embed.set_footer(text=f"Time remaining: {minutes_left} minutes")
        
        return embed
        
    async def end_poll_timer(self, message_id: int, duration: int):
        """
        Timer to automatically end the poll after specified duration.
        
        Args:
            message_id (int): ID of the poll message
            duration (int): Poll duration in minutes
        """
        await asyncio.sleep(duration * 60)
        if message_id in self.active_polls:
            await self.end_poll(message_id)
            
    async def end_poll(self, message_id: int):
        """
        Finalize and display poll results.
        
        Args:
            message_id (int): ID of the poll message to end
        """
        if message_id not in self.active_polls:
            return

        poll_data = self.active_polls[message_id]

        # Create results embed
        embed = discord.Embed(
            title=f"📊 Poll Results: {poll_data['title']}",
            color=discord.Color.green()
        )

        # Calculate total votes
        total_votes = sum(len(votes) for votes in poll_data["votes"].values())

        # Prepare option results
        option_results = []
        for i, option in enumerate(poll_data["options"]):
            votes = len(poll_data["votes"][i])
            option_results.append((i, option, votes))

        if total_votes > 0:
            # Find max votes
            max_votes = max(votes for _, _, votes in option_results)
            # Identify winning options
            winners = [res for res in option_results if res[2] == max_votes]
            # Other options
            others = [res for res in option_results if res[2] != max_votes]

            # Display winning options
            for i, option, votes in winners:
                percentage = (votes / total_votes * 100)
                bar = "█" * int(percentage / 10) + "░" * (10 - int(percentage / 10))
                embed.add_field(
                    name=f"🏆 Winning Option: {option}",
                    value=f"{bar} {votes} votes ({percentage:.1f}%)",
                    inline=False
                )
            # Add other options
            for i, option, votes in others:
                percentage = (votes / total_votes * 100)
                bar = "█" * int(percentage / 10) + "░" * (10 - int(percentage / 10))
                embed.add_field(
                    name=f"Option {i+1}: {option}",
                    value=f"{bar} {votes} votes ({percentage:.1f}%)",
                    inline=False
                )
        else:
            # If no votes
            for i, option, _ in option_results:
                embed.add_field(
                    name=f"Option {i+1}: {option}",
                    value="0 votes (0.0%)",
                    inline=False
                )

        embed.set_footer(text="Poll has ended")

        # Edit original poll message and send results
        try:
            channel = self.bot.get_channel(poll_data["channel_id"])
            message = await channel.fetch_message(message_id)
            await message.edit(embed=embed, view=None)
            await channel.send(embed=embed)
        except Exception as e:
            print(f"[ERROR] Failed to update poll results: {e}")

        # Remove poll data
        del self.active_polls[message_id]

class PollView(discord.ui.View):
    """
    A custom view for creating poll buttons dynamically.
    """
    def __init__(self, options: List[str], multiple: bool):
        """
        Initialize poll view with options.
        
        Args:
            options (List[str]): List of poll options
            multiple (bool): Whether multiple choices are allowed
        """
        super().__init__(timeout=None)
        self.options = options
        self.multiple = multiple
        
        # Add option buttons
        for i, option in enumerate(options):
            button = PollButton(i, option)
            self.add_item(button)

class PollButton(discord.ui.Button):
    """
    A custom button for voting in a poll.
    """
    def __init__(self, option_id: int, option_text: str):
        """
        Initialize a poll voting button.
        
        Args:
            option_id (int): Unique identifier for the option
            option_text (str): Text displayed on the button
        """
        super().__init__(
            style=discord.ButtonStyle.primary,
            label=option_text,
            custom_id=f"poll_{option_id}"
        )
        self.option_id = option_id
        
    async def callback(self, interaction: discord.Interaction):
        """
        Handle button click for voting.
        
        Args:
            interaction (discord.Interaction): The interaction triggered by button click
        """
        poll_cog = interaction.client.get_cog("Poll")
        if not poll_cog:
            return
            
        poll_data = poll_cog.active_polls.get(interaction.message.id)
        if not poll_data:
            await interaction.response.send_message(
                "This poll has already ended!",
                ephemeral=True
            )
            return
            
        votes = poll_data["votes"]
        user_id = interaction.user.id
        
        # Check if user already voted for this option
        if user_id in votes[self.option_id]:
            votes[self.option_id].remove(user_id)
            action = "Removed vote from"
        else:
            # Clear other votes if not multiple choice
            if not poll_data["multiple"]:
                for v in votes.values():
                    v.discard(user_id)
            votes[self.option_id].add(user_id)
            action = "Voted for"
            
        # Update display
        embed = poll_cog.create_poll_embed(poll_data)
        await interaction.message.edit(embed=embed)
        await interaction.response.send_message(
            f"You {action} option {self.option_id + 1}!",
            ephemeral=True
        )

async def setup(bot):
    """
    Setup function to add the Poll cog to the bot.
    
    Args:
        bot (commands.Bot): The Discord bot instance
    """
    await bot.add_cog(Poll(bot))
