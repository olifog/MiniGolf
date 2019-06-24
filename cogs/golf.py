import discord
from discord.ext import commands
import asyncio
from utils.game import Game


class golf(commands.Cog):
    """Game commands"""

    def __init__(self, bot):
        self.bot = bot
        self.game = None

    @commands.command()
    async def test(self, ctx):
        self.game = Game(self.bot)
        self.game.load("1")

        gif = await self.game.start_game()

        await ctx.send(file=discord.File(fp=gif, filename='render.gif'))




def setup(bot):
    bot.add_cog(golf(bot))