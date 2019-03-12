'''
Created on Mar 11, 2019
'''
import Constants as CONST
import pygame
import math
import os
import Physics2D
from enum import Enum
from pygame.locals import *

class PlayerAnims(Enum):
    playerIdleR = 0
    playerIdleL = 1
    playerWalkR = 2
    playerWalkL = 3
    playerFallR = 4
    playerFallL = 5


class Player:
    pos = None
    myCollider = None
    cameraPos = None
    currentSprite = None
    currentVelocity = None
    currentDir = None
    loadedAnims = None
    currentAnim = None
    currentAnimFrame = None
    currentAnimTickrate = None
    inputDir = None
    grounded = False
    jumpTime = 0
    
    def __init__(self):
        self.pos = (0, 100)
        self.cameraPos = self.pos
        self.loadedAnims = {}
        self.currentAnimTickrate = 0
        self.loadAnims()
        self.currentSprite = self.loadedAnims[PlayerAnims.playerIdleR][0]
        self.currentVelocity = (0, 0)
        self.currentDir = 1
        self.currentAnim = PlayerAnims.playerIdleR
        self.currentAnimFrame = 0
        self.inputDir = 0
        self.jumpTime = 0
        self.myCollider = Physics2D.BoxCollider(self.pos, (self.pos[0] + CONST.PlayerSizeX, self.pos[1] + CONST.PlayerSizeY), False)
        
    # Results: Loads all player animations into loadedAnims as (Enum PlayerAnims, array[pygameImg])
    def loadAnims(self):
        for animState in PlayerAnims:
            slug = animState.name[0:len(animState.name)-1]
            exists = True
            i = 0
            currentAnim = []
            while exists:
                sprite = pygame.image.load('Sprites/Player/' + slug + str(i) + '.png')
                sprite = pygame.transform.scale(sprite, (CONST.PlayerSizeX, CONST.PlayerSizeY))
                if animState.name[len(animState.name)-1] == 'L':
                    sprite = pygame.transform.flip(sprite, 1, 0)
                currentAnim.append(sprite)
                i += 1
                exists = os.path.isfile('Sprites/Player/' + slug + str(i) + '.png')
            self.loadedAnims[animState] = currentAnim
            
        
    # Inputs: integer dir, -1 or 1
    #
    # Results: Change of velocity 
    def move(self, dir):
        if self.grounded:
            self.inputDir = dir / abs(dir)
            if dir != self.currentDir:#and dir != 0:
                self.currentDir = dir / abs(dir)
        
        accel = dir*CONST.PlayerAcceleration
        
        if self.currentVelocity[1] != 0: # If airborne, player should have less control
            accel /= CONST.PlayerAirStruggle
            
        cv = self.currentVelocity
        cv = (cv[0]+accel, cv[1])
        if abs(cv[0]) > abs(CONST.MaxPlayerSpeed):
            cv = (CONST.MaxPlayerSpeed * (dir/abs(dir)), cv[1])
        self.currentVelocity = cv
    
    # Results: If can jump, adds jumpforce to curr y velocity
    def jump(self):
        # TODO: check if can jump
        if self.grounded:
            self.currentVelocity = (self.currentVelocity[0], self.currentVelocity[1] + CONST.PlayerJumpForce)
            self.pos = (self.pos[0], self.pos[1]+1)
            self.jumpTime = 0
        elif self.currentVelocity[1] > 0 and self.jumpTime < CONST.PlayerMaxJumpTime:
            self.currentVelocity = (self.currentVelocity[0], self.currentVelocity[1] + CONST.Gravity)
            self.jumpTime += 1 / CONST.FPS
        
    
    # Should be called once a frame
    #
    # Results: Moves the player based on velocity,
    #          Reduces velocity based on friction,
    #          Updates whether the player is grounded,
    #          Calls setAnim
    #          Updates camera position
    def tick(self, potentialCollisions):
        friction = ((self.currentVelocity[0])/CONST.PlayerFriction)
        if self.currentVelocity[1] != 0: # If airborne, player should not experience friction / slow down
            friction = 0
        
        self.pos = (self.pos[0] + self.currentVelocity[0], self.pos[1] + self.currentVelocity[1])
        self.myCollider.updatePos(self.pos, (self.pos[0] + CONST.PlayerSizeX, self.pos[1] + CONST.PlayerSizeY))
        
        # TODO: Check x collision, move away, check y collision, set y velocity to 0 if collided vertically AFTER moving out of wall and move up
        
        self.grounded = False
        for block in potentialCollisions:
            if self.myCollider.checkCollision(block.myCollider):
                blockPos = block.getPixelPos()
                distance = (self.pos[0] - blockPos[0], self.pos[1] - blockPos[1])
                
                adjustedPos = [self.pos[0], self.pos[1]]
                
                ray = Physics2D.Line((self.pos[0]+CONST.PlayerSizeX/2, self.pos[1]+CONST.PlayerSizeY/2), (blockPos[0]+CONST.BlockSize/2, blockPos[1]+CONST.BlockSize/2))
                
                norm = ray.normalized()
                
                if norm[0] > norm[1] + 0.25:
                    self.currentVelocity = (0, self.currentVelocity[1])
                    if distance[0] < 0:
                        adjustedPos[0] += (-distance[0] - CONST.PlayerSizeX)# - CONST.BlockSize)
                    else:
                        adjustedPos[0] += (-distance[0] + CONST.PlayerSizeX)
                elif norm[1] > norm[0] + 0.25:
                    if distance[1] < 0:
                        adjustedPos[1] += (-distance[1] - (CONST.BlockSize))
                        self.currentVelocity = (self.currentVelocity[0], 0)
                        block.interactBelow()
                    else:
                        adjustedPos[1] += (-distance[1] + (CONST.BlockSize))
                        self.grounded = True
                        self.currentVelocity = (self.currentVelocity[0], 0)
                    
                self.pos = (adjustedPos[0], adjustedPos[1])
                self.myCollider.updatePos(self.pos, (self.pos[0] + CONST.PlayerSizeX, self.pos[1] + CONST.PlayerSizeY))
    
        if not self.grounded:
            self.currentVelocity = (self.currentVelocity[0], self.currentVelocity[1] - CONST.Gravity)#(self.currentVelocity[0] - friction, self.currentVelocity[1] - CONST.Gravity)
        else:
            self.currentVelocity = (self.currentVelocity[0] - friction, self.currentVelocity[1])
            
        if self.currentVelocity[1] > CONST.MaxFallSpeed:
            self.currentVelocity = (self.currentVelocity[0], CONST.MaxFallSpeed)
        
        self.currentAnimTickrate += 1
        
        if abs(self.currentVelocity[0]) > (CONST.MaxPlayerSpeed / 2) + 0.1:
            self.currentAnimTickrate += 1
        if self.currentAnimTickrate >= CONST.AnimTickrate:
            self.setAnim()
            self.currentAnimTickrate = 0
        self.cameraPos = self.pos # TODO: Camera smoothing, handling corners so that the camera never shows negative coordinates
    
    # Results: Sets or increments the player's animation frame
    def setAnim(self):
        prefState = None
        dirToString = {-1 : 'L', 1 : 'R'}
        stringDir = dirToString[self.currentDir]
        animState = None
        animSheet = None
        
        if not self.grounded:
            for state in PlayerAnims:
                if state.name == "playerFall" + stringDir:
                    animState = state
                    break
            self.currentAnim = animState
            animSheet = self.loadedAnims[self.currentAnim]
            self.currentAnimFrame = 0
        else:
            if self.inputDir == 0:
                prefState = "playerIdle" + stringDir
            elif self.inputDir != 0:
                prefState = "playerWalk" + stringDir
            for state in PlayerAnims:
                if state.name == prefState:
                    animState = state
                    break
            if self.currentAnim != animState:
                self.currentAnimFrame = 0
            self.currentAnim = animState
            
            self.currentAnimFrame += 1
            animSheet = self.loadedAnims[self.currentAnim]
            self.currentAnimFrame %= len(animSheet)
        
        
        self.currentSprite = animSheet[self.currentAnimFrame]
        
    # Results: Returns on-screen position of the player
    def getOnscreenPos(self):
        return (self.pos[0]-self.cameraPos[0]+(CONST.ScreenSizeX/2), (-self.pos[1])+self.cameraPos[1]+(CONST.ScreenSizeY/2) - (CONST.PlayerSizeY-CONST.BlockSize))
    
    # Results: Draws the player to screen with his current sprite
    def draw(self, display):
        display.blit(self.currentSprite, self.getOnscreenPos())