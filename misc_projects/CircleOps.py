class CircleOps:
    PI = 3.14
    def __init__(self):
        print("Welcome to CircleOps")

class getCircleArea(CircleOps):

    def __init__(self, radius):
        CircleOps.__init__(self)
        self.radius = radius
        area = self.PI * radius * radius
        print(area)

class getCirclePerimeter(CircleOps):

    def __init__(self, radius):
        CircleOps.__init__(self)
        self.radius = radius
        perimeter = self.PI * radius * 2
        print(perimeter)

class getSectorArea(CircleOps):

    def __init__(self, radius,angle):
        CircleOps.__init__(self)
        self.radius = radius
        self.angle = angle
        sectorarea = self.PI * radius * (angle/360)
        print(sectorarea)

circlearea = getCircleArea(5)
circleperimeter = getCirclePerimeter(5)
circlesectorarea = getSectorArea(5,10)