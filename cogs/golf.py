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
        self.levels = 3
        self.games = {}

    async def startui(self, ctx, game, level):
        game.load(level)
        await game.start_game()
        frame = await game.for_discord(await game.new_frame())
        await ctx.send("Welcome to hole " + str(level) + "!")

        await ctx.send(file=discord.File(fp=frame, filename='start.png'))
        await ctx.send(file=discord.File("./data/Degrees.png"))
        await ctx.send("Now use mg!aim [angle] [strength 1-10] to aim your ball!")

    @commands.command()
    async def start(self, ctx):
        game = Game(self.bot, ctx.author.id)
        self.games[ctx.author.id] = game

        await self.startui(ctx, game, 1)

    @commands.command()
    async def aim(self, ctx, angle: int, strength: int):
        if not 1 <= strength <= 10:
            await ctx.send("Please choose a strength between 1 and 10.")
            return

        angle = (angle * -1) + 90
        game = self.games[ctx.author.id]

        game.player.angle = angle
        game.player.velocity = strength

        px = game.player.x
        py = game.player.y

        arrowx, arrowy = tuple(np.add(cartesian(angle, strength * 4), (px, py)))
        mainline = Line(px, py, arrowx, arrowy)

        img = await game.new_frame()
        draw = ImageDraw.Draw(img)

        mainline.draw(draw)

        await ctx.send(file=discord.File(fp=await game.for_discord(img), filename='aim.png'))
        await ctx.send("Use mg!hit to hit the ball, or mg!aim to aim it again.")

    @commands.command()
    async def hit(self, ctx):
        game = self.games[ctx.author.id]

        if game.player.velocity == 0:
            await ctx.send("Please aim your ball first with mg!aim!")
            return

        stmsg = await ctx.send("Hitting the ball... (can take up to 10 seconds to make the gif :) )")

        gif = await game.hit()

        await ctx.send(file=discord.File(fp=gif, filename="shot.gif"))

        still = await game.new_frame()
        await ctx.send(file=discord.File(fp=await game.for_discord(still), filename='shot.png'))


        if game.player.render:
            await ctx.send(file=discord.File("./data/Degrees.png"))
            await stmsg.delete()
        else:
            if game.levels == self.levels:
                await ctx.send("You completed the entire course in " + str(game.hits) + " hits! Yayyy\nNow get your friends to see if they can beat you!")
                return

            await ctx.send("Congratulations, you finished this hole! Levels left to complete: " + str(self.levels - game.levels))
            await asyncio.sleep(2)
            await ctx.send("Moving onto hole " + str(game.levels + 1) + "...")
            await asyncio.sleep(1)
            await self.startui(ctx, game, game.levels + 1)


def setup(bot):
    bot.add_cog(golf(bot))