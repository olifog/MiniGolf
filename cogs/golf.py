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
    async def start(self, ctx, name):
        self.game = Game(self.bot)
        self.game.load(name)

        await self.game.start_game()
        frame = await self.game.for_discord(await self.game.new_frame())

        await ctx.send(file=discord.File(fp=frame, filename='render.png'))




def setup(bot):
    bot.add_cog(golf(bot))