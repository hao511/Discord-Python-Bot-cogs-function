import discord
from discord.ext import commands
from discord import app_commands

class CommandExamples(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    # Standard Listener Event (already present)
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Triggered when a new member joins the server"""
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(f'Welcome {member.mention}.')

    # 1. Regular Text Command (prefix-based)
    @commands.command(name="hello", help="A simple greeting command")
    async def hello(self, ctx, *, member: discord.Member = None):
        """Demonstrates a traditional text-based command
        
        This command can be invoked with a bot prefix (e.g., >hello)
        It allows optional member mention and has basic context handling
        """
        member = member or ctx.author
        if self._last_member is None or self._last_member.id != member.id:
            await ctx.send(f'Hello {member.name}~')
        else:
            await ctx.send(f'Hello {member.name}... This feels familiar.')
        self._last_member = member

    # 2. Hybrid Command (works in both text and slash command contexts)
    @commands.hybrid_command(name="ping", description="Check bot's latency")
    async def ping(self, ctx):
        """Demonstrates a hybrid command that works as both text and slash command
        
        - Can be invoked with bot prefix (>ping)
        - Can be used as a slash command (/ping)
        - Automatically syncs between text and slash interfaces
        """
        latency = round(self.bot.latency * 1000)
        await ctx.send(f'Pong! Latency is {latency}ms')

    # 3. App Command (pure slash command)
    @app_commands.command(name="userinfo", description="Get information about a user")
    async def user_info(self, interaction: discord.Interaction, member: discord.Member = None):
        """Demonstrates a pure slash command
        
        - Only works as a slash command (/userinfo)
        - Uses Discord's interaction system
        - Provides detailed user information
        """
        # Default to the user who invoked the command if no member specified
        member = member or interaction.user
        
        # Create an embed with user information
        embed = discord.Embed(
            title=f"User Information for {member.name}", 
            color=member.color
        )
        embed.add_field(name="User ID", value=member.id, inline=False)
        embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        embed.add_field(name="Roles", value=", ".join([role.name for role in member.roles[1:]]) or "No roles", inline=False)
        
        embed.set_thumbnail(url=member.display_avatar.url)
        
        # Respond to the interaction
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    """Setup function to add the CommandExamples cog to the bot"""
    await bot.add_cog(CommandExamples(bot))
