'''
    Created on 3/12/19
'''
import Constants as CONST
import pygame
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


def getOnScreenPos(pos, cameraPos):
    return (pos[0]-cameraPos[0]+(CONST.ScreenSizeX/2), (-pos[1])+cameraPos[1]+(CONST.ScreenSizeY/2))