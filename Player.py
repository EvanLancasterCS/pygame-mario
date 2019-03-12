'''
Created on Mar 11, 2019
'''
import Constants as CONST
import pygame
import math
import os
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
            accel /= 10
            
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
    def tick(self):
        friction = ((self.currentVelocity[0])/CONST.PlayerFriction)
        if self.currentVelocity[1] != 0: # If airborne, player should not experience friction / slow down
            friction = 0
        
        self.pos = (self.pos[0] + self.currentVelocity[0], self.pos[1] + self.currentVelocity[1])
        self.currentVelocity = (self.currentVelocity[0] - friction, self.currentVelocity[1] - CONST.Gravity)
        # TODO: Check x collision, move away, check y collision, set y velocity to 0 if collided vertically AFTER moving out of wall and move up
        
        # TEMP "UNIVERSAL" COLLISION FOR TESTING
        if self.pos[1] <= 0:
            self.pos = (self.pos[0], 0)
            self.currentVelocity = (self.currentVelocity[0], 0)
            self.grounded = True
        else:
            self.grounded = False
        
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
        return (self.pos[0]-self.cameraPos[0]+(CONST.ScreenSizeX/2), (-self.pos[1])+self.cameraPos[1]+(CONST.ScreenSizeY/2))
    
    # Results: Draws the player to screen with his current sprite
    def draw(self, display):
        display.blit(self.currentSprite, self.getOnscreenPos())