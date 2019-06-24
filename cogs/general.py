
import discord
from discord.ext import commands
from datetime import datetime
import humanize

class general(commands.Cog):
    """General commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """Check the ping and latency of the bot"""
        process_time = round(((datetime.utcnow() - ctx.message.created_at).total_seconds()) * 1000)
        e = discord.Embed(color=discord.Color.blue())

        e.add_field(
            name="**Latency:**",
            value=f"{round(self.bot.latency * 1000)}ms"
        )
        e.add_field(
            name="**Process time:**",
            value=f"{process_time}ms",
            inline=False
        )

        await ctx.send(embed=e)

    @commands.command()
    async def invite(self, ctx):
        """Sends the bot's invite link"""
        invite = f"https://discordapp.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=314432&scope=bot"
        message = f"**Here's the invite:**   *(needs the permissions to send images etc.)*\n<{invite}>"
        await ctx.send(message)

    @commands.command()
    async def info(self, ctx):
        """View bot info"""
        owner = "Moose#0064"
        invite = f"https://discordapp.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=314432&scope=bot"
        uptime = humanize.naturaltime(self.bot.uptime)
        source = "https://github.com/OliMoose/MiniGolf"

        e = discord.Embed(title="MiniGolf", color=discord.Color.blue())
        e.add_field(name="Owner:", value=owner)
        e.add_field(name="Invite:", value=f"[Invite here]({invite})")
        e.add_field(name="Uptime:", value=f"Been up since {uptime}")
        e.add_field(name="Source:", value=f"{source}")
        await ctx.send(embed=e)

    @commands.command()
    async def source(self, ctx):
        """Sends link to Github source"""
        await ctx.send("https://github.com/OliMoose/MiniGolf")

def setup(bot):
    bot.add_cog(general(bot))