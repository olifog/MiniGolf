

# Holds physics classes and functions
# Angle system:
#
#           90
#           |
#           |
#           |
# 180 ------+------ 0
#           |
#           |
#           |
#           270
#
# Coordinates start from bottom left
#
# Coding my own simple physics system was a LOT harder than I thought it would be

import math
from shapely.geometry import LineString
import numpy as np


def cartesian(angle, distance):  # Convert polar coordinates to cartesian
    x = distance * math.cos(math.radians(angle))
    y = distance * math.sin(math.radians(angle))

    return x, y


def acute_diff(p1, p2):  # Given p1 and p2 in the range 0 to 360, return acute angle difference
    d1 = max(p1,p2) - min(p1,p2)
    d2 = min(p1,p2) - max(p1,p2) + 360
    return min(d1, d2)


class Ball(object):  # The player's ball object

    def __init__(self, game, x, y, radius, angle, velocity=0):
        # Structure
        self.game = game

        # Position
        self.x = x
        self.y = y

        # Physics
        self.radius = radius
        self.velocity = velocity
        self.angle = angle

        # Rendering
        self.render = True

    def point(self):  # Express the ball's position as a Point object
        return Point(self.x, self.y)

    async def move(self):  # Move the ball, according to its current velocity and angle
        self.x, self.y = tuple(np.add(cartesian(self.angle, self.velocity), (self.x, self.y)))
        self.velocity *= self.game.friction

    async def get_closest_collision(self, lines):  # Gets the closest collision of all lines, returns point + line
        clpoint = None
        clline = None
        cldist = 99999

        for line in lines:  # Literally just iterate through all the lines and see if its collision is closest
            col = await self.get_collision_point(line)

            if col:
                dist = col.distance(self.point())
                if dist < cldist:
                    clpoint = col
                    cldist = dist
                    clline = line

        if clpoint:
            return clpoint, clline
        else:
            return None, None

    async def bounce(self, line):  # Returns angle of bounce- warning VERY dodgy function here
        # Not entirely sure if it completely works

        self.angle = self.angle % 360  # Normalise angle

        # Get bounce angles
        wallangle = line.get_angle()
        intersectangle = acute_diff(wallangle, self.angle)

        if max(self.angle, wallangle) + intersectangle >= 360:  # Testing for straddle condition, invert it
            intersectangle *= -1

        if wallangle > self.angle:
            return self.angle + (intersectangle * 2)
        else:
            return self.angle - (intersectangle * 2)

    async def get_collision_point(self, line):  # Get the collision point of the ball with a line
        traj = await self.get_trajectory()  # Ball's current trajectory

        raypoint = traj.intersect(line)  # The trajectory's intersect with the line- this is not the collision point, as the ball has a radius

        if str(raypoint) != "GEOMETRYCOLLECTION EMPTY":
            trajangle = self.angle % 360  # Normalise angle

            wallangle = line.get_angle()  # Get wall angles
            intersectangle = acute_diff(wallangle, trajangle)

            # Get the hypotenuse of the collision triangle
            hyp = self.radius / math.sin(math.radians(intersectangle))

            pangle = 90-trajangle  # Mini angle

            pointx = round(raypoint.x - (hyp * math.sin(math.radians(pangle))))
            pointy = round(raypoint.y - (hyp * math.cos(math.radians(pangle))))

            return Point(pointx, pointy)

    async def get_trajectory(self):  # Return a line representing the ball's future potential trajectory, ignoring lines

        # Need to know how many ticks (n) before velocity is low, 0.1
        # Current velocity x friction^n = 0.1
        # Rearranging for n:
        # friction^n = 0.1/velocity
        # n = log base friction for 0.1/velocity

        ticks = math.ceil(math.log(0.1/self.velocity, self.game.friction))

        curvel = self.velocity
        dist = curvel

        for n in range(1, ticks + 1):  # Get the total distance to be travelled, based on the ticks of movement
            dist += curvel * (math.pow(self.game.friction, n))

        # Converting polar to cartesian to get end coords
        endx, endy = cartesian(self.angle, dist)
        endx += self.x
        endy += self.y

        return Line(self.x, self.y, endx, endy)

    def draw(self, imagedraw):  # Get the ball to draw itself
        if self.render:
            width, height = imagedraw.im.size
            x = self.x
            y = height - self.y
            r = self.radius
            imagedraw.ellipse((x-r, y-r, x+r, y+r), fill=(220, 20, 60, 255))


class Line(object):  # Object representing a line in the game world
    def __init__(self, x1, y1, x2, y2, goal=False, bad=False):
        self.goal = goal
        self.bad = bad

        self.p1 = Point(x1, y1)
        self.p2 = Point(x2, y2)

    def linestring(self):  # Return a shapely linestring for intersection calc
        return LineString([(self.p1.x, self.p1.y), (self.p2.x, self.p2.y)])

    def intersect(self, line):  # Get point of intersection between two lines (if exists)
        isect = self.linestring().intersection(line.linestring())
        return isect

    def get_angle(self):  # Get the line's angle
        fromp1 = self.p1.angle(self.p2)
        fromp2 = self.p2.angle(self.p1)

        return min(fromp1, fromp2)

    def draw(self, imagedraw):  # Draw the line, only currently used in the aim command- used it a lot in debugging
        width, height = imagedraw.im.size
        imagedraw.line([self.p1.x, height - self.p1.y, self.p2.x, height - self.p2.y], fill=(255, 255, 255, 255), width=2)


class Point(object):  # Simple object to represent a point in space

    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)

    def __str__(self):
        return str(self.x) + ", " + str(self.y)

    def distance(self, point):  # Get distance to another point, just uses pythagoras
        return math.sqrt((point.x-self.x) ** 2 + (point.y-self.y) ** 2)

    def angle(self, point):  # Get angle to another point
        angle = math.degrees(math.atan2(point.y - self.y, point.x - self.x))
        if angle < 0:
            angle += 360
        return angle

