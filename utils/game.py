
# Game objects and functions

from .physics import Ball, Point, Line
from PIL import Image, ImageDraw
from io import BytesIO
import copy
import math
import asyncio


class Game(object):

    def __init__(self, bot, playerid, friction=0.97):
        self.bot = bot
        self.lines = []
        self.friction = friction
        self.playerid = playerid
        self.hits = 0
        self.levels = 0

        self.start = None
        self.goal = None
        self.source = None
        self.player = None
        self.base = None

        self.framespersecond = 30
        self.frames = []
        self.extraseconds = 2
        self.framelen = 1000 / self.framespersecond

    async def start_game(self):
        self.player = Ball(self, self.start.x, self.start.y, 3, 45, 10)

    async def getclcol(self):
        nexthit, nextline = await self.player.get_closest_collision(self.lines)

        dist = 9999
        if nexthit:
            dist = self.player.point().distance(nexthit)

        return nexthit, nextline, dist

    async def hit(self):
        self.hits += 1
        self.frames = []
        ticks = math.ceil(math.log(0.1 / self.player.velocity, self.friction))  # ticks before ball is stationary

        nexthit, nextline, dist = await self.getclcol()

        dist = 9999
        if nexthit:
            dist = self.player.point().distance(nexthit)

        for n in range(0, ticks):
            if self.player.velocity > dist:
                if nextline.goal:
                    self.player.render = False
                    self.levels += 1
                    await self.new_frame()
                    break

                if nextline.bad:
                    self.player.x = self.start.x
                    self.player.y = self.start.y
                    self.player.velocity = 0
                    self.player.angle = 0
                    await self.new_frame()
                    break

                self.player.x = nexthit.x
                self.player.y = nexthit.y

                self.player.angle = await self.player.bounce(nextline)
                self.player.x += (self.player.velocity - dist) * math.cos(math.radians(self.player.angle))
                self.player.y += (self.player.velocity - dist) * math.sin(math.radians(self.player.angle))
                nexthit, nextline, dist = await self.getclcol()
                await self.new_frame()

            dist -= self.player.velocity
            await self.player.move()
            await self.new_frame()

        for x in range(0, self.extraseconds * self.framespersecond):
            self.frames.append(self.frames[-1].copy())

        return await self.render_gif()

    async def new_frame(self):
        image = copy.copy(self.base)
        draw = ImageDraw.Draw(image)

        self.player.draw(draw)
        self.frames.append(image)

        return image

    async def for_discord(self, frame):
        byteio = BytesIO()
        frame.save(byteio, format='PNG')

        return BytesIO(byteio.getvalue())

    async def render_gif(self):
        byteio = BytesIO()
        self.frames[0].save(byteio, format='GIF', append_images=self.frames[1:], save_all=True, duration=self.framelen, loop=0)
        self.frames = []

        return BytesIO(byteio.getvalue())

    def load(self, levelname):
        self.lines = []
        self.source = "./levels/" + str(levelname) + "/" + str(levelname)
        self.base = Image.open(self.source + "Base.png")
        lines = open(self.source + "Lines.txt", "r").readlines()

        for l in lines:
            content = l.split(",")

            if content[0] == "Start":
                self.start = Point(content[1], content[2])

            elif content[0] == "Goal":
                gl = Line(content[1], content[2], content[3], content[4], goal=True)
                self.goal = gl
                self.lines.append(gl)

            elif content[0] == "Line":
                self.lines.append(Line(content[1], content[2], content[3], content[4]))

            elif content[0] == "Bad":
                self.lines.append(Line(content[1], content[2], content[3], content[4], bad=True))