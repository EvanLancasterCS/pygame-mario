'''
    Created on 3/12/19
'''
import Constants as CONST
import pygame
import math
from pygame.locals import *

# Inputs: pygame image img
#
# Results: tuple of four 1/4th rect areas of img
def splitImage(img):
    divisions = 2
    areas = []
    width, height = img.get_width()/divisions, img.get_height()/divisions
    for y in range(divisions):
        for x in range(divisions):
            area = pygame.Rect((x, y), (width, height))
            areas.append(area)
    return areas

# Results: Returns modified position for drawing on screen
def getOnScreenPos(pos, cameraPos):
    return (pos[0]-cameraPos[0]+(CONST.ScreenSizeX/2), (-pos[1])+cameraPos[1]+(CONST.ScreenSizeY/2))

# Results: Returns screen pos to grid pos
def screenToGrid(pos, cameraPos):
    pos = (pos[0]+cameraPos[0]-(CONST.ScreenSizeX/2), (-pos[1])+cameraPos[1]+(CONST.ScreenSizeY/2))
    gridPos = [pos[0]/CONST.BlockSize, pos[1]/CONST.BlockSize]
    gridPos = (math.floor(gridPos[0]), math.floor(gridPos[1])+1)
    return gridPos
    
# Inputs: tuple(x,y) pos1
#         tuple(x,y) pos2
#
# Results: Returns true / false based on if cursor is in the square from x1, y1 to x2, y2
def isMouseOverArea(pos1, pos2):
    mPos = pygame.mouse.get_pos()
    
    if mPos[0] >= pos1[0] and mPos[1] >= pos1[1] and mPos[0] <= pos2[0] and mPos[1] <= pos2[1]:
        return True
    return False