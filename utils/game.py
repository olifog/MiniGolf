
# Game objects and functions

from .physics import Ball, Point, Line
from PIL import Image, ImageDraw
from io import BytesIO
import copy
import math
import asyncio


class Game(object):

    def __init__(self, bot, playerid, friction=0.97):
        # Structure class vars
        self.bot = bot
        self.lines = []
        self.friction = friction
        self.playerid = playerid
        self.hits = 0
        self.levels = 0

        # Gameplay class vars
        self.start = None
        self.goal = None
        self.source = None
        self.player = None
        self.base = None

        # Rendering class vars
        self.framespersecond = 30
        self.frames = []
        self.extraseconds = 2
        self.framelen = 1000 / self.framespersecond

    async def start_game(self):  # Make the player ball
        self.player = Ball(self, self.start.x, self.start.y, 3, 0)

    async def getclcol(self):  # Get the player's closest collision, and the distance to it
        nexthit, nextline = await self.player.get_closest_collision(self.lines)

        dist = 9999
        if nexthit:
            dist = self.player.point().distance(nexthit)

        return nexthit, nextline, dist

    async def hit(self):  # Juicy hit function
        self.hits += 1
        self.frames = []

        # Need to know how many ticks (n) before velocity is low, 0.1
        # Current velocity x friction^n = 0.1
        # Rearranging for n:
        # friction^n = 0.1/velocity
        # n = log base friction for 0.1/velocity
        ticks = math.ceil(math.log(0.1 / self.player.velocity, self.friction))  # ticks before ball is stationary

        nexthit, nextline, dist = await self.getclcol()  # Get the initial closest collision, if it exists

        for n in range(0, ticks):  # For every tick as the player moves
            if self.player.velocity > dist:  # If the player will cross the next collision point next movement
                if nextline.goal:  # Whether the line is an epic finish line or nah
                    self.player.render = False
                    self.levels += 1
                    await self.new_frame()
                    break

                if nextline.bad:  # Whether the line's evil- reset the ball's position and vel
                    self.player.x = self.start.x
                    self.player.y = self.start.y
                    self.player.velocity = 0
                    self.player.angle = 0
                    await self.new_frame()
                    break

                # Warp straight to the collision point
                self.player.x = nexthit.x
                self.player.y = nexthit.y

                self.player.angle = await self.player.bounce(nextline) # Get the new angle after the bounce

                # Move the remaining left over velocity
                self.player.x += (self.player.velocity - dist) * math.cos(math.radians(self.player.angle))
                self.player.y += (self.player.velocity - dist) * math.sin(math.radians(self.player.angle))

                nexthit, nextline, dist = await self.getclcol()  # Get a new close collision point
                await self.new_frame()

            # Update distance, velocity, and frames
            dist -= self.player.velocity
            await self.player.move()
            await self.new_frame()

        # After the for loop is finished, either by fully moving or running into a special line there needs to be a few seconds of stillness
        # We can do this by simply duplicating the last frame a bunch of times
        for x in range(0, self.extraseconds * self.framespersecond):
            self.frames.append(self.frames[-1].copy())

        return await self.render_gif()  # Render the gif and return it

    async def new_frame(self):  # Generate a new frame of the current game, add it to the game's frames and return it
        image = copy.copy(self.base)
        draw = ImageDraw.Draw(image)

        self.player.draw(draw)
        self.frames.append(image)

        return image

    async def for_discord(self, frame):  # Save a frame as a discord-sendable object
        byteio = BytesIO()
        frame.save(byteio, format='PNG')

        return BytesIO(byteio.getvalue())

    async def render_gif(self):  # Render all the frames in game.frames together, return a discord-sendable object
        byteio = BytesIO()
        self.frames[0].save(byteio, format='GIF', append_images=self.frames[1:], save_all=True, duration=self.framelen, loop=0)
        self.frames = []

        return BytesIO(byteio.getvalue())

    def load(self, levelname):  # Load the specified level number
        self.lines = []
        self.source = "./levels/" + str(levelname) + "/" + str(levelname)  # Generate a new source for level files
        self.base = Image.open(self.source + "Base.png")  # Generate a new base PNG
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