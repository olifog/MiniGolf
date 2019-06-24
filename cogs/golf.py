import discord
from discord.ext import commands
import asyncio
from utils.game import Game
from utils.physics import Line, cartesian
import numpy as np
from PIL import Image, ImageDraw


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
        await ctx.send(file=discord.File("./data/Degrees.png"))

    @commands.command()
    async def aim(self, ctx, angle: int, strength: int):
        angle = (angle * -1) + 90
        self.game.player.angle = angle
        self.game.player.velocity = strength

        px = self.game.player.x
        py = self.game.player.y

        arrowx, arrowy = tuple(np.add(cartesian(angle, strength * 4), (px, py)))
        mainline = Line(px, py, arrowx, arrowy)

        img = await self.game.new_frame()
        draw = ImageDraw.Draw(img)

        mainline.draw(draw)

        await ctx.send(file=discord.File(fp=await self.game.for_discord(img), filename='render.png'))




def setup(bot):
    bot.add_cog(golf(bot))