'''
    Created on 3/11/19
'''
import pygame
import sys
import Constants as CONST
import Player
import Physics2D
import Graphics
import random
import math
from enum import Enum
from pygame.locals import *
from _operator import pos
from Constants import ChunkSize
from pygame import camera

class Block:
    gridPos = None
    chunkPos = None
    blockE = None
    myGame = None
    activeCollider = None
    myCollider = None       # TODO - Only give specified blocks colliders for better performance
    currentParticles = None # Particles are an array of size 5 (img, rect, pos, velocity, lifetime)
    animProgress = None
    currentAnimAdd = None
    currentVelocity = None
    reward = None
    
    # Inputs: tuple gridPos(x, y)
    #         Enum from Blocks
    #         Game myGame
    def __init__(self, gridPos, blockE, myGame):
        self.gridPos = gridPos
        self.chunkPos = myGame.blockToChunk(gridPos[0])
        self.blockE = blockE
        self.myGame = myGame
        self.activeCollider = True
        pPos = self.getPixelPos()
        self.myCollider = Physics2D.BoxCollider(pPos, (pPos[0]+CONST.BlockSize, pPos[1]+CONST.BlockSize), True)
        self.currentParticles = []
        self.animProgress = 1
        self.currentAnimAdd = 0
        self.currentVelocity = (0,0)
        if CONST.BlockInfo[self.blockE][1] == CONST.BlockTypes.powerup and CONST.BlockInfo[self.blockE][3]:
            self.currentVelocity = (0.05, 0)
        if CONST.BlockInfo[self.blockE][1] == CONST.BlockTypes.reward:
            self.reward = CONST.Blocks.mushroom
    
    # Results: sets activeCollider to true or false based on if enclosed by 4 blocks
    def setColliderActivity(self):
        if self.myGame.blockExistsAtPos((self.gridPos[0], self.gridPos[1]+1)) and \
                        self.myGame.blockExistsAtPos((self.gridPos[0], self.gridPos[1]-1)) and \
                        self.myGame.blockExistsAtPos((self.gridPos[0]+1, self.gridPos[1])) and \
                        self.myGame.blockExistsAtPos((self.gridPos[0]-1, self.gridPos[1])):
            self.activeCollider = False
        else:
            self.activeCollider = True
            
    # Inputs: tuple newPos(x, y)
    #
    # Results: Moves gridpos and collider to new x,y
    def move(self, newPos):
        self.gridPos = newPos
        nChunk = self.myGame.blockToChunk(self.gridPos[0])
        if nChunk != self.chunkPos and self in self.myGame.chunks[self.chunkPos]:
            self.myGame.chunks[self.chunkPos].remove(self)
            self.chunkPos = nChunk
            if self.chunkPos in self.myGame.chunks:
                self.myGame.chunks[self.chunkPos].append(self)
            else:
                self.myGame.chunks[self.chunkPos] = [self]
                
        rPos = self.getPixelPos()
        if not CONST.BlockInfo[self.blockE][1] == CONST.BlockTypes.powerup:
            self.myCollider.updatePos(rPos, (rPos[0]+CONST.BlockSize, rPos[1]+CONST.BlockSize))
        else:
            self.myCollider.updatePos((rPos[0]+2, rPos[1]), (rPos[0]+CONST.BlockSize-2, rPos[1]+CONST.BlockSize-4))
        
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
    
    # Inputs: CurrentPlayerState currentState
    #
    # Results: Based on block type;
    #          powerup: removes self from game
    def interact(self, currentState):
        if CONST.BlockInfo[self.blockE][1] == CONST.BlockTypes.powerup:
            chunkPos = self.myGame.blockToChunk(self.gridPos[0])
            self.myGame.chunks[chunkPos].remove(self)
            self.myGame.blockList.remove(self)
            
    # Inputs: CurrentPlayerState currentState
    #
    # Results: Based on block type;
    #          Breakable: Removes self from list and creates chunk particles
    def interactBelow(self, currentState):
        self.animProgress = 0
        self.currentAnimAdd = 0
        if CONST.BlockInfo[self.blockE][1] == CONST.BlockTypes.breakable and currentState != CONST.CurrentPlayerState.Small:
            rects = Graphics.splitImage(self.myGame.loadedImgs[self.blockE])
            for r in rects:
                pPos = self.getPixelPos()
                pPos = (pPos[0] + random.random()*16, pPos[1] + random.random()*16)
                yVel = random.randint(2, 3) * 4
                xVel = random.randint(1, 2)
                if xVel == 2:
                    xVel = -1
                xVel *= 4
                particle = [self.myGame.loadedImgs[self.blockE], r, pPos, (xVel, yVel), 1] # img, rect, pos, velocity, lifetime
                self.myGame.currentParticles.append(particle)
            
            chunkPos = self.myGame.blockToChunk(self.gridPos[0])
            self.myGame.chunks[chunkPos].remove(self)
            self.myGame.blockList.remove(self)
        elif self.reward != None:
            self.myGame.addBlock((self.gridPos[0], self.gridPos[1]+1), self.reward)
            self.reward = None
            slug = CONST.BlockInfo[self.blockE][0]
            slug += "-empty"
            for key in CONST.BlockInfo:
                if CONST.BlockInfo[key][0] == slug:
                    self.blockE = key
                    break
            
        
    # Results: Gets current anim progress position, adds time.deltatime to current anim time if in progress
    def getAnimPos(self):
        animTime = 0.25
        positionModifier = -125
        if self.animProgress < animTime:
            if self.animProgress < animTime/2:
                self.currentAnimAdd += (1 / CONST.FPS) * positionModifier
            else:
                self.currentAnimAdd -= (1 / CONST.FPS) * positionModifier
            self.animProgress += (1 / CONST.FPS)
        else:
            return 0
        return self.currentAnimAdd
    
    # Results: basic vertical collision & sets vert velocity to 0 when grounded.
    def checkVerticalCollision(self):
        if self.myGame.blockExistsAtPos((round(self.gridPos[0], 0), round(self.gridPos[1],0)-1)):
            self.currentVelocity = (self.currentVelocity[0], 0)
            self.gridPos = (self.gridPos[0], round(self.gridPos[1],0))
            return True
        elif self.myGame.blockExistsAtPos((round(self.gridPos[0], 0), math.floor(self.gridPos[1]))):
            self.currentVelocity = (self.currentVelocity[0], 0)
            self.gridPos = (self.gridPos[0], int(self.gridPos[1]))
            return True
        return False
    
    # Results: basic horizontal collision & reversal in velocity when hit.
    def checkHorizontalCollision(self):
        if self.currentVelocity[0] > 0:
            if self.myGame.blockExistsAtPos(((math.ceil(self.gridPos[0]), math.floor(self.gridPos[1])))):
                self.move((math.ceil(self.gridPos[0]-1), self.gridPos[1]))
                self.currentVelocity = (-self.currentVelocity[0], self.currentVelocity[1])
        elif self.currentVelocity[0] < 0:
            if self.myGame.blockExistsAtPos(((math.floor(self.gridPos[0]), math.floor(self.gridPos[1])))):
                self.move((math.floor(self.gridPos[0])+1, self.gridPos[1]))
                self.currentVelocity = (-self.currentVelocity[0], self.currentVelocity[1])
                    
    # Results: Moves block based on velocity
    #          Adds gravity if is gravity affected
    def tickVelocity(self, doGrav):
        gravity = 0
        bInfo = CONST.BlockInfo[self.blockE]
        if bInfo[1] == CONST.BlockTypes.powerup and doGrav:
            if bInfo[4]:
                gravity = CONST.Gravity
        self.currentVelocity = (self.currentVelocity[0], self.currentVelocity[1] - (gravity/100))
        if self.currentVelocity[0] != 0 or self.currentVelocity[1] != 0:
            self.move((self.gridPos[0] + self.currentVelocity[0], self.gridPos[1] + self.currentVelocity[1]))
            
    # Inputs: display from pygame
    #         tuple cameraPos(x, y)
    #
    # Results: Draws self to screen based on camera position, as well as anim position
    def draw(self, display, cameraPos):
        if CONST.BlockInfo[self.blockE][1] == CONST.BlockTypes.powerup:
            self.tickVelocity(not self.checkVerticalCollision())
            self.checkHorizontalCollision()
            
        
        pos = self.getOnScreenPos(cameraPos)
        myImg = self.myGame.loadedImgs[self.blockE]
        pos = (pos[0], pos[1] + self.getAnimPos())
        display.blit(myImg, pos)

class Game:
    blockList = None
    loadedImgs = None
    myPlayer = None
    currentParticles = None
    chunks = None
    
    # Inputs: 
    def __init__(self):
        self.currentParticles = []
        self.blockList = []
        self.loadedImgs = {}
        self.chunks = {}
        self.myPlayer = Player.Player()
        
    # Results: Draws particles in current particles.
    #          Destroys any particles that have over-stayed their welcome.
    def drawParticles(self, display, cameraPos):
        for particle in self.currentParticles:
            particle[4] -= 1 / CONST.FPS
            if particle[4] <= 0: # Remove particle if lifetime <= 0
                self.currentParticles.remove(particle)
                continue
            particle[3] = (particle[3][0] - particle[3][0]/16, particle[3][1] - (CONST.Gravity/2)) # Y Velocity - Gravity, X Velocity - Air friction
            particle[2] = (particle[2][0] + particle[3][0], particle[2][1] + particle[3][1])
            display.blit(particle[0], Graphics.getOnScreenPos(particle[2], cameraPos), particle[1])
    
    # Inputs: xPos of block
    #
    # Results: Returns chunk number of block
    def blockToChunk(self, xPos):
        chunk = math.floor(xPos / CONST.ChunkSize)
        return chunk
    
    # Inputs: int chunkNum
    #
    # Results: Returns array of blocks in chunk chunkNum
    def getChunkBlocks(self, chunkNum):
        if chunkNum in self.chunks:
            return self.chunks[chunkNum]
        return []
    
    # Inputs: tuple pos(x, y)
    #
    # Results: Returns True / False based on if there is a block at given gridpos
    def blockExistsAtPos(self, pos):
        chunkPos = self.blockToChunk(pos[0])
        chunkBlocks = self.getChunkBlocks(chunkPos)
        for block in chunkBlocks:
            if block.gridPos[0] == pos[0] and block.gridPos[1] == pos[1]:
                return True
        return False
    
    # Inputs: tuple pos(x,y)
    #
    # Results: Returns block at pos if there is one, None if there is not
    def getBlock(self, pos):
        chunkPos = self.blockToChunk(pos[0])
        chunkBlocks = self.getChunkBlocks(chunkPos)
        for block in chunkBlocks:
            if block.gridPos[0] == pos[0] and block.gridPos[1] == pos[1]:
                return block
        return None
    
    # Inputs: tuple pos(x,y)
    #
    # Results: Removes block from blockList and chunks if exists
    def removeBlock(self, pos):
        if self.blockExistsAtPos(pos):
            b = None
            for block in self.blockList:
                if block.gridPos[0] == pos[0] and block.gridPos[1] == pos[1]:
                    b = block
                    break
            chunkPos = self.blockToChunk(pos[0])
            self.chunks[chunkPos].remove(b)
            self.blockList.remove(b)
    
    # Inputs: Enum from Blocks
    #         tuple pos(x, y)
    #
    # Results: Adds new block object to blockList and, if slug is not found in loadedImgs,
    #          loads the block's image.
    def addBlock(self, pos, blockE):
        if not self.blockExistsAtPos(pos):
            blockSlug = CONST.BlockInfo[blockE][0]
            if not blockE in self.loadedImgs:
                self.loadedImgs[blockE] = pygame.image.load('Sprites/Blocks/' + blockSlug + '.png')
                self.loadedImgs[blockE] = pygame.transform.scale(self.loadedImgs[blockE], (CONST.BlockSize, CONST.BlockSize))
            b = Block(pos, blockE, self)
            self.blockList.append(b)
            chunkPos = self.blockToChunk(pos[0])
            if chunkPos in self.chunks:
                self.chunks[chunkPos].append(b)
            else:
                self.chunks[chunkPos] = [b]
    
    # Results: Draws game to screen, inputs collisions based on player chunk
    def draw(self, display):
        if self.myPlayer.pos[1] < 0:
            self.myPlayer.pos = (100, 100)
        
        potentialCollisions = []
        drawArea = []
        
        playerPos = Graphics.getOnScreenPos(self.myPlayer.pos, self.myPlayer.cameraPos)
        
        playerChunk = self.blockToChunk(Graphics.screenToGrid(playerPos, self.myPlayer.cameraPos)[0])
        cameraChunk = self.blockToChunk(Graphics.screenToGrid((CONST.ScreenSizeX/2,0), self.myPlayer.cameraPos)[0])
        
        for i in range(-1, 2):
            potentialCollisions.extend(self.getChunkBlocks(playerChunk+i))
        for i in range(-CONST.DrawDistance, CONST.DrawDistance+1):
            drawArea.extend(self.getChunkBlocks(cameraChunk+i))
        
        self.myPlayer.tick(potentialCollisions)
        self.myPlayer.draw(display)
        
        for i in range(len(drawArea)):
            block = drawArea[len(drawArea)-i-1]
            if block.isOnScreen(self.myPlayer.cameraPos):
                block.draw(display, self.myPlayer.cameraPos)
                
        self.drawParticles(display, self.myPlayer.cameraPos)
        
        