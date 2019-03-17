'''
    Created on 3/11/19
'''
import pygame
import math
import Constants as CONST

# Inputs: num xMin1; num xMax1
#         num xMin2; num xMax2
#
# Results: Return True / False based on if overlapping
def isOverlapping1D(xMin1, xMax1, xMin2, xMax2):
    return xMax1 >= xMin2 and xMax2 >= xMin1




class Line:
    x1 = None
    y1 = None
    x2 = None
    y2 = None
    
    # Inputs: tuple p1(x,y)
    #         tuple p2(x,y)
    def __init__(self, p1, p2):
        self.x1 = p1[0]
        self.x2 = p2[0]
        self.y1 = p1[1]
        self.y2 = p2[1]
    
    # Inputs: Line other
    # 
    # Results: Returns (IntersectX, IntersectY) if two lines intersect
    def intersects(self, other):
        x1 = self.x1
        x2 = self.x2
        y1 = self.y1
        y2 = self.y2
        x3 = other.x1
        x4 = other.x2
        y3 = other.y1
        y4 = other.y2
        try:
            intersectX = (((x1*y2-y1*x2)*(x3-x4)-(x1-x2)*(x3*y4-y3*x4))/((x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)))
            intersectY = (((x1*y2-y1*x2)*(y3-y4)-(y1-y2)*(x3*y4-y3*x4))/((x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)))
            if (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)!=0:
                return (intersectX, intersectY)
        except:
            return (x1, y1)
    
    def getLength(self):
        nx = abs(self.x2 - self.x1)
        ny = abs(self.y2 - self.y1)
        length = math.sqrt((nx*nx) + (ny*ny))
        return length
    
    # Returns normalized vector
    def normalized(self):
        nx = abs(self.x2 - self.x1)
        ny = abs(self.y2 - self.y1)
        length = math.sqrt((nx*nx) + (ny*ny))
        if length != 0:
            return (nx/length, ny/length)
        else:
            return (0, 0)
    
    # Outputs: Returns lowest x-value
    def minX(self):
        return min(self.x1, self.x2)
    
    # Outputs: Returns highest x-value
    def maxX(self):
        return max(self.x1, self.x2)
    
    # Outputs: Returns lowest y-value
    def minY(self):
        return min(self.y1, self.y2)
    
    # Outputs: Returns highest y-value
    def maxY(self):
        return max(self.y1, self.y2)
    
    # Draws white line from x1, y1 to x2, y2
    def draw(self, display, cameraPos):
        pygame.draw.line(display, (255,255,255), (self.x1-cameraPos[0]+(CONST.ScreenSizeX/2), (-self.y1)+cameraPos[1]+(CONST.ScreenSizeY/2)+CONST.BlockSize), 
                                                 (self.x2-cameraPos[0]+(CONST.ScreenSizeX/2), (-self.y2)+cameraPos[1]+(CONST.ScreenSizeY/2)+CONST.BlockSize))
        
class BoxCollider:
    colliderPoints = None
    colliderLines = None
    static = None
    
    # Inputs: tuple pt1(x,y)
    #         tuple pt2(x,y)
    #         boolean static
    #
    # Results: Creates points for a box from x1, y1 to x2, y2 and calls self.buildLines
    def __init__(self, pt1, pt2, static):
        self.static = static
        self.updatePos(pt1, pt2)
    
    # Results: Moves current collider points to new pt1, pt2 and current line points to pt1, pt2
    def updatePos(self, pt1, pt2):
        self.colliderPoints = self.buildPoints(pt1, pt2)
        self.colliderLines = self.buildLines()
    
    # Results: Returns a tuple of points (p1, p2, p3, p4)
    def buildPoints(self, pt1, pt2):
        p1 = (pt1[0], pt1[1])
        p2 = (pt2[0], pt1[1])
        p3 = (pt1[0], pt2[1])
        p4 = (pt2[0], pt2[1])
        cPts = (p1, p2, p3, p4)
        return cPts
    
    # Results: Returns tuple (xmin1, xmax1, ymin1, ymax1)
    def getMinMax(self):
        xmin1 = min(self.colliderLines[0].minX(), self.colliderLines[2].minX())
        xmax1 = max(self.colliderLines[0].maxX(), self.colliderLines[2].maxX())
        ymin1 = min(self.colliderLines[0].minY(), self.colliderLines[2].minY())
        ymax1 = max(self.colliderLines[0].maxY(), self.colliderLines[2].maxY())
        return (xmin1, xmax1, ymin1, ymax1)
    
    # Inputs: BoxCollider other
    def checkCollision(self, other):
        myMinMax = self.getMinMax()
        otherMinMax = other.getMinMax()
        return isOverlapping1D(myMinMax[0], myMinMax[1], otherMinMax[0], otherMinMax[1]) and isOverlapping1D(myMinMax[2], myMinMax[3], otherMinMax[2], otherMinMax[3])
    
    # Results: Creates line objects from self.colliderPoints and returns
    def buildLines(self):
        cPts = self.colliderPoints
        line1 = Line(cPts[0], cPts[1])
        line2 = Line(cPts[0], cPts[2])
        line3 = Line(cPts[3], cPts[1])
        line4 = Line(cPts[3], cPts[2])
        collLines = (line1, line2, line3, line4)
        return collLines
    
    # Draws all liens to screen
    def draw(self, display, cameraPos):
        for line in self.colliderLines:
            line.draw(display, cameraPos)
        
    