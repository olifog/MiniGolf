

# Holds physics classes and functions
# Angle system:

#           90
#           |
#           |
#           |
# 180 ------+------ 0
#           |
#           |
#           |
#           270

# Coordinates start from bottom left

import math
from PIL import ImageDraw, Image
from shapely.geometry import LineString


def cartesian(angle, distance):
    x = distance * math.cos(math.radians(angle))
    y = distance * math.sin(math.radians(angle))

    return x, y

def acute_diff(p1, p2):
    """Given p1 and p2 in the range 0 to 360, return acute angle difference"""
    d1 = max(p1,p2) - min(p1,p2)
    d2 = min(p1,p2) - max(p1,p2) + 360
    return min(d1, d2)


class Ball(object):

    def __init__(self, game, x, y, radius, angle, velocity=0):
        self.game = game

        self.x = x
        self.y = y

        self.radius = radius
        self.velocity = velocity
        self.angle = angle

    def move(self):
        self.x += (self.velocity * math.cos(math.radians(self.angle)))
        self.y += (self.velocity * math.sin(math.radians(self.angle)))
        self.velocity *= self.game.friction

    async def get_closest_collision(self, lines):  # Gets the closest collision of all lines, returns point + line
        clpoint = None
        clline = None
        cldist = 99999

        for line in lines:
            col = await self.get_collision_point(line)

            if col:
                dist = col.distance(Point(self.x, self.y))
                if dist < cldist:
                    clpoint = col
                    cldist = dist
                    clline = line

        if clpoint:
            return clpoint, clline

    async def bounce(self, line):  # Returns angle of bounce
        intersectangle = acute_diff(line.get_angle(), self.angle)

        return self.angle + intersectangle + 90

    async def get_collision_point(self, line):
        traj = await self.get_trajectory()

        raypoint = traj.intersect(line)

        if str(raypoint) != "GEOMETRYCOLLECTION EMPTY":
            trajangle = self.angle
            wallangle = line.get_angle()

            intersectangle = acute_diff(wallangle, trajangle)

            hyp = self.radius / math.sin(math.radians(intersectangle))

            pangle = 90-trajangle

            pointx = round(raypoint.x - (hyp * math.sin(math.radians(pangle))))
            pointy = round(raypoint.y - (hyp * math.cos(math.radians(pangle))))

            return Point(pointx, pointy)

    async def get_trajectory(self):

        # Need to know how many ticks (n) before velocity is low, 0.1
        # Current velocity x friction^n = 0.1
        # Rearranging for n:
        # friction^n = 0.1/velocity
        # n = log base friction for 0.1/velocity

        ticks = math.ceil(math.log(0.1/self.velocity, self.game.friction))

        curvel = self.velocity
        dist = curvel

        for n in range(1, ticks + 1):
            dist += curvel * (math.pow(self.game.friction, n))

        # Converting polar to cartesian to get end coords
        endx, endy = cartesian(self.angle, dist)
        endx += self.x
        endy += self.y

        return Line(self.x, self.y, endx, endy)

    def draw(self, imagedraw):
        width, height = imagedraw.im.size
        x = self.x
        y = height - self.y
        r = self.radius
        imagedraw.ellipse((x-r, y-r, x+r, y+r), fill=(220, 20, 60, 255))


class Line(object):
    def __init__(self, x1, y1, x2, y2, goal=False):
        self.goal = goal

        self.p1 = Point(x1, y1)
        self.p2 = Point(x2, y2)

    def linestring(self):
        return LineString([(self.p1.x, self.p1.y), (self.p2.x, self.p2.y)])

    def intersect(self, line):  # Get point of intersection between two lines (if exists)
        isect = self.linestring().intersection(line.linestring())
        return isect

    def get_angle(self):
        fromp1 = self.p1.angle(self.p2)
        fromp2 = self.p2.angle(self.p1)

        return min(fromp1, fromp2)

    def draw(self, imagedraw):
        width, height = imagedraw.im.size
        imagedraw.line([self.p1.x, height - self.p1.y, self.p2.x, height - self.p2.y], fill=(10, 10, 250, 255), width=2)


class Point(object):

    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)

    def __str__(self):
        return str(self.x) + ", " + str(self.y)

    def distance(self, point):
        return math.sqrt((point.x-self.x) ** 2 + (point.y-self.y) ** 2)

    def angle(self, point):
        angle = math.degrees(math.atan2(point.y - self.y, point.x - self.x))
        if angle < 0:
            angle += 360
        return angle

