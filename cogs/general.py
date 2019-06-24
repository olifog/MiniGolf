
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

def setup(bot):
    bot.add_cog(general(bot))