
# Game objects and functions

from .physics import Ball, Point, Line
from PIL import Image, ImageDraw
from io import BytesIO
import copy
import asyncio


class Game(object):

    def __init__(self, bot, friction=0.95):
        self.bot = bot
        self.lines = []
        self.friction = friction

        self.start = None
        self.goal = None
        self.source = None
        self.player = None
        self.base = None

        self.framespersecond = 30
        self.giflength = 6
        self.frames = []
        self.framelen = 1000 / self.framespersecond
        self.totalframes = self.framespersecond * self.giflength

    async def start_game(self):
        self.player = Ball(self, self.start.x, self.start.y, 2, 45, 10)

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
        self.source = "./levels/" + str(levelname) + "/" + str(levelname)
        self.base = Image.open(self.source + "Base.png")
        lines = open(self.source + "Lines.txt", "r").readlines()

        for l in lines:
            content = l.split(",")

            if content[0] == "Start":
                self.start = Point(content[1], content[2])

            elif content[0] == "Goal":
                gl = Line(content[1], content[2], content[3], content[4], True)
                self.goal = gl
                self.lines.append(gl)

            elif content[0] == "Line":
                self.lines.append(Line(content[1], content[2], content[3], content[4]))