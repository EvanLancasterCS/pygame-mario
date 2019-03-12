'''
    Created on 3/11/19
'''
import pygame
import sys
import Constants as CONST
import Player
import Physics2D
from enum import Enum
from pygame.locals import *

class Blocks(Enum):
    groundRock = 0
    wallBrick = 1

class BlockTypes(Enum):
    unbreakable = 0
    breakable = 1
    reward = 2

BlockInfo = {
    Blocks.groundRock: ("ground-rock",BlockTypes.unbreakable),
    Blocks.wallBrick: ("wall-brick",BlockTypes.breakable)
    }

class Block:
    gridPos = None
    blockE = None
    myGame = None
    myCollider = None # TODO - Only give specified blocks colliders for better performance
    
    # Inputs: tuple gridPos(x, y)
    #         Enum from Blocks
    #         Game myGame
    def __init__(self, gridPos, blockE, myGame):
        self.gridPos = gridPos
        self.blockE = blockE
        self.myGame = myGame
        pPos = self.getPixelPos()
        self.myCollider = Physics2D.BoxCollider(pPos, (pPos[0]+CONST.BlockSize, pPos[1]+CONST.BlockSize), True)
        
    # Results: Returns the position in real pixels of block
    def getPixelPos(self):
        return (self.gridPos[0]*CONST.BlockSize, self.gridPos[1]*CONST.BlockSize)
    
    # Inputs: tuple cameraPos(x, y)
    #
    # Results: Returns the position of the block relative to screen
    def getOnScreenPos(self, cameraPos):
        myPos = self.getPixelPos()
        return (myPos[0]-cameraPos[0]+(CONST.ScreenSizeX/2), (-myPos[1])+cameraPos[1]+(CONST.ScreenSizeY/2))
    
    # Inputs: tuple cameraPos(x, y)
    #
    # Results: Returns true if on 
    def isOnScreen(self, cameraPos):
        pos = self.getOnScreenPos(cameraPos)
        if pos[0] <= CONST.ScreenSizeX and pos[0]+CONST.BlockSize >= 0 and pos[1] <= CONST.ScreenSizeY and pos[1]+32 >= 0:
            return True
        return False
    
    def interactBelow(self):
        if BlockInfo[self.blockE][1] == BlockTypes.breakable:
            self.myGame.blockList.remove(self)
    
    # Inputs: display from pygame
    #         tuple cameraPos(x, y)
    #
    # Results: Draws self to screen based on camera position
    def draw(self, display, cameraPos):
        pos = self.getOnScreenPos(cameraPos)
        myImg = self.myGame.loadedImgs[self.blockE]
        display.blit(myImg, pos)

class Game:
    blockList = None
    loadedImgs = None
    myPlayer = None
    
    # Inputs: 
    def __init__(self):
        self.blockList = []
        self.loadedImgs = {}
        self.myPlayer = Player.Player()
        
    # Inputs: Enum from Blocks
    #         tuple pos(x, y)
    #
    # Results: Adds new block object to blockList and, if slug is not found in loadedImgs,
    #          loads the block's image.
    def addBlock(self, pos, blockE):
        blockSlug = BlockInfo[blockE][0]
        if not blockE in self.loadedImgs:
            self.loadedImgs[blockE] = pygame.image.load('Sprites/Blocks/' + blockSlug + '.png')
            self.loadedImgs[blockE] = pygame.transform.scale(self.loadedImgs[blockE], (CONST.BlockSize, CONST.BlockSize))
        self.blockList.append(Block(pos, blockE, self))
        
        