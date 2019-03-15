'''
    Created on 3/11/19
'''
import Constants as CONST
import pygame
import math
import os
import Physics2D
from enum import Enum
from pygame.locals import *
from _hashlib import new
from cgitb import small
from Constants import FPS

class PlayerAnims(Enum):
    playerIdleR = 0
    playerIdleL = 1
    playerWalkR = 2
    playerWalkL = 3
    playerFallR = 4
    playerFallL = 5

class CurrentPlayerState(Enum):
    Small = 0
    Large = 1
    

class Player:
    pos = None
    myCollider = None
    cameraPos = None
    currentSprite = None
    currentVelocity = None
    currentDir = None
    currentState = None
    loadedAnims = None
    currentAnim = None
    currentAnimFrame = None
    currentAnimTickrate = None
    currentHeight = None
    inputDir = None
    grounded = False
    jumpTime = 0
    
    def __init__(self):
        self.pos = (0, 100)
        self.cameraPos = self.pos
        self.currentHeight = CONST.PlayerSizeY
        self.loadedAnims = {}
        self.loadAnims()
        self.currentAnimTickrate = 0
        self.currentState = CurrentPlayerState.Small
        self.currentSprite = self.loadedAnims[PlayerAnims.playerIdleR, self.currentState][0]
        self.currentVelocity = (0, 0)
        self.currentDir = 1
        self.currentAnim = PlayerAnims.playerIdleR
        self.currentAnimFrame = 0
        self.inputDir = 0
        self.jumpTime = 0
        self.myCollider = Physics2D.BoxCollider(self.pos, (self.pos[0] + CONST.PlayerSizeX, self.pos[1] + self.currentHeight), False)
        
    # Inputs: CurrentPlayerState state
    #
    # Results: Changes player size / state to new
    def changeState(self, newState):
        if newState == CurrentPlayerState.Small:
            self.currentHeight = CONST.PlayerSizeY
        else:
            self.currentHeight = CONST.PlayerLargeSizeY
        self.currentState = newState
        
    # Results: Loads all player animations into loadedAnims as (key(Enum PlayerAnims, Enum CurrentPlayerState), array[pygameImg])
    def loadAnims(self):
        for animState in PlayerAnims:
            for playerState in CurrentPlayerState:
                slug = animState.name[0:len(animState.name)-1] 
                slug = slug[0:6] + playerState.name + slug[6:]
                exists = True
                i = 0
                currentAnim = []
                while exists:
                    sprite = pygame.image.load('Sprites/Player/' + slug + str(i) + '.png')
                    if playerState == CurrentPlayerState.Small:
                        sprite = pygame.transform.scale(sprite, (CONST.PlayerSizeX, CONST.PlayerSizeY))
                    else:
                        sprite = pygame.transform.scale(sprite, (CONST.PlayerSizeX, CONST.PlayerLargeSizeY))
                    if animState.name[len(animState.name)-1] == 'L':
                        sprite = pygame.transform.flip(sprite, 1, 0)
                    currentAnim.append(sprite)
                    i += 1
                    exists = os.path.isfile('Sprites/Player/' + slug + str(i) + '.png')
                self.loadedAnims[animState, playerState] = currentAnim
            
        
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
        if self.grounded:
            self.currentVelocity = (self.currentVelocity[0], self.currentVelocity[1] + CONST.PlayerJumpForce)
            self.pos = (self.pos[0], self.pos[1]+1)
            self.jumpTime = 0
        elif self.currentVelocity[1] > 0 and self.jumpTime < CONST.PlayerMaxJumpTime:
            self.currentVelocity = (self.currentVelocity[0], self.currentVelocity[1] + CONST.Gravity)
            self.jumpTime += 1 / CONST.FPS
    
    # Inputs: array potentialCollisions
    #         array *ignored, should generally only be recursively added.
    #
    # Results: Moves player based on collisions, dealing with closer first, and
    #          recalculating collisions for recently collided blocks after each movement.
    def checkCollisions(self, potentialCollisions):
        collisions = []
        
        for block in potentialCollisions:
            if self.myCollider.checkCollision(block.myCollider):
                blockPos = block.getPixelPos()
                #distance = (self.pos[0]+CONST.PlayerSizeX/2 - blockPos[0], self.pos[1]+self.currentHeight/2 - blockPos[1])
                
                
                adjustedPos = [self.pos[0], self.pos[1]]
                
                ray = Physics2D.Line((self.pos[0]+CONST.PlayerSizeX/2, self.pos[1]+self.currentHeight/2), (blockPos[0]+CONST.BlockSize/2, blockPos[1]+CONST.BlockSize/2))
                distance = (ray.x1 - ray.x2, ray.y1 - ray.y2)
                length = ray.getLength()
                norm = ray.normalized()    
                collisions.append((block, ray, length, norm, distance))
        
        # Sort collisions by closest
        new = []
        for i in range(len(collisions)):
            if len(new) == 0:
                new.append(collisions[i])
                continue
            else:
                found = False
                for j in range(len(new)):
                    if abs(collisions[i][2]) < abs(new[j][2]):
                        new.insert(j, collisions[i]) 
                        found = True
                        break
                if not found:
                    new.append(collisions[i])
        collisions = new
        
        # Deal with first collision, then recall function and redo all calculations for nearby blocks.
        if len(collisions) > 0:
            block = collisions[0][0]
            ray = collisions[0][1]
            length = collisions[0][2]
            norm = (round(collisions[0][3][0],1), round(collisions[0][3][1],1))
            distance = collisions[0][4]
            
            # This is a really ugly block of code and I'm sorry if you're trying to decode it.
            # It took me a while to all the edge cases I encountered x-x
            
            # First, it checks for if it's within the "circle of possibilities" for the player,
            # which has a radius based on current height, width, and the constant block size.
            
            # The next part determines if it should be a horizontal or vertical collision;
            # to do this it checks if the proportion of the line for horizontal / vertical is greater
            # than the other proportion. There's also specific checks for edge cases where
            # the player is moving towards a wall and they shouldn't be able to break a block
            # that is over another block.
            
            # Within the horizontal / vertical collisions, it determines whether the player
            # should be pushed towards the right or left, which is based on the
            # horizontal / vertical distance from the given block.
            
            # After it finishes all of its stuff, it moves the player and calls this function
            # again with a smaller array of potential blocks.
            
            requiredDist = math.sqrt((self.currentHeight / 2)**2 + (CONST.PlayerSizeX / 2)**2) + CONST.BlockSize
            if length <= requiredDist:
                if norm[0] > norm[1] or (norm[1] > norm[0] and distance[1] >= 0 and block.myGame.blockExistsAtPos((block.gridPos[0], block.gridPos[1]+2)) and self.currentState == CurrentPlayerState.Large): # Right / Left Collision
                    if distance[0] < 0: # Right-side collision
                        adjustedPos[0] += (-distance[0] - (CONST.BlockSize / 2) - (CONST.PlayerSizeX/2))
                        self.currentVelocity = (self.currentVelocity[0]*0.9, self.currentVelocity[1])
                    elif distance[0] > 0: # Left-side collision
                        adjustedPos[0] += (-distance[0] + (CONST.PlayerSizeX/2) + (CONST.PlayerSizeX/2)) 
                        self.currentVelocity = (self.currentVelocity[0]*0.9, self.currentVelocity[1])
                elif norm[1] > norm[0] and abs(distance[0]) < CONST.PlayerSizeX: # Up / Down Collision
                    if distance[1] <= 0 and self.currentVelocity[1] > 0: # Up Collision
                        if self.currentState == CurrentPlayerState.Small or not block.myGame.blockExistsAtPos((block.gridPos[0], block.gridPos[1]-2)):
                            adjustedPos[1] += (-distance[1] - (CONST.BlockSize/2) - (self.currentHeight/2))
                            self.currentVelocity = (self.currentVelocity[0], 0)
                            block.interactBelow(self.currentState.value)
                    elif distance[1] >= 0 and self.currentVelocity[1] <= 0 and not block.myGame.blockExistsAtPos((block.gridPos[0], block.gridPos[1]+1)): # Down Collision
                        if self.currentState == CurrentPlayerState.Small or not block.myGame.blockExistsAtPos((block.gridPos[0], block.gridPos[1]+2)):
                            adjustedPos[1] += (-distance[1] + (CONST.BlockSize/2) + (self.currentHeight/2))
                            self.grounded = True
                            self.currentVelocity = (self.currentVelocity[0], 0)
                
                self.pos = (adjustedPos[0], adjustedPos[1])
                self.myCollider.updatePos(self.pos, (self.pos[0] + CONST.PlayerSizeX, self.pos[1] + self.currentHeight))
                
            potentialBlocks = []
            for i in range(1, len(collisions)):
                potentialBlocks.append(collisions[i][0])
            
            self.checkCollisions(potentialBlocks)
                    
    # Should be called once a frame
    # Inputs: array potentialCollision of blocks to check for collisions with
    #
    # Results: Moves the player based on velocity,
    #          Reduces velocity based on friction,
    #          Calls checkCollisions with input potentialCollisions
    #          Calls setAnim
    #          Updates camera position
    def tick(self, potentialCollisions):
        friction = ((self.currentVelocity[0])/CONST.PlayerFriction)
        if self.currentVelocity[1] != 0: # If airborne, player should not experience friction / slow down
            friction = 0
        
        self.pos = (self.pos[0] + self.currentVelocity[0], self.pos[1] + self.currentVelocity[1])
        self.myCollider.updatePos(self.pos, (self.pos[0] + CONST.PlayerSizeX, self.pos[1] + self.currentHeight))
        
        self.grounded = False
        self.checkCollisions(potentialCollisions)
    
        if not self.grounded:
            self.currentVelocity = (self.currentVelocity[0], self.currentVelocity[1] - CONST.Gravity)#(self.currentVelocity[0] - friction, self.currentVelocity[1] - CONST.Gravity)
        else:
            self.currentVelocity = (self.currentVelocity[0] - friction, self.currentVelocity[1])
        
        if self.currentVelocity[1] < -CONST.MaxFallSpeed:
            self.currentVelocity = (self.currentVelocity[0], -CONST.MaxFallSpeed)
        
        #if abs(self.currentVelocity[0]) <= 0.001:
        #    self.currentVelocity = (0, self.currentVelocity[1])
        
        self.currentAnimTickrate += 1 / CONST.FPS

        if abs(self.currentVelocity[0]) > (CONST.MaxPlayerSpeed / 2) + 0.1:
            self.currentAnimTickrate += 1 / CONST.FPS
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
            animSheet = self.loadedAnims[self.currentAnim, self.currentState]
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
            animSheet = self.loadedAnims[self.currentAnim, self.currentState]
            self.currentAnimFrame %= len(animSheet)
        
        
        self.currentSprite = animSheet[self.currentAnimFrame]
        
    # Results: Returns on-screen position of the player
    def getOnscreenPos(self):
        return (self.pos[0]-self.cameraPos[0]+(CONST.ScreenSizeX/2), (-self.pos[1])+self.cameraPos[1]+(CONST.ScreenSizeY/2) - (self.currentHeight-CONST.BlockSize))
    
    # Results: Draws the player to screen with his current sprite
    def draw(self, display):
        display.blit(self.currentSprite, self.getOnscreenPos())