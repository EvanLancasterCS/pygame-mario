'''
    Created on 3/11/19
''' 
import pygame
import sys
import GameState as GS
import Constants as CONST
import Graphics
import math
from pygame.locals import *

fpsClock = pygame.time.Clock()

display = pygame.display.set_mode((CONST.ScreenSizeX, CONST.ScreenSizeY))
pygame.init()
game = GS.Game()
for x in range(-15, 15):
    for y in range(-1, 0):
        game.addBlock((x,y), CONST.Blocks.groundRock)
        
game.addBlock((4, 0), CONST.Blocks.wallBrick)
game.addBlock((4, 1), CONST.Blocks.wallBrick)
game.addBlock((4, 3), CONST.Blocks.wallBrick)
game.addBlock((3, 1), CONST.Blocks.mushroom)
for x in range(15):
    game.addBlock((x, 4), CONST.Blocks.wallBrick)
game.addBlock((16, -4), CONST.Blocks.groundRock)

def mousePosToGrid():
    mPos = pygame.mouse.get_pos()
    mPos = (mPos[0]-CONST.ScreenSizeX/2, mPos[1]-CONST.ScreenSizeY/2)
    mPos = (mPos[0]+game.myPlayer.cameraPos[0], -mPos[1]+game.myPlayer.cameraPos[1]+CONST.BlockSize)
    gridPos = [mPos[0]/CONST.BlockSize, mPos[1]/CONST.BlockSize]
    gridPos = (math.floor(gridPos[0]), math.floor(gridPos[1]))
    return gridPos

while True:
    display.fill((100, 120, 180))
    
    
    
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == MOUSEBUTTONDOWN:
            gridPos = mousePosToGrid()
            game.addBlock(gridPos, CONST.Blocks.wallBrick)
        if event.type == KEYDOWN:
            if event.key == pygame.K_r:
                game.myPlayer.changeState(CONST.CurrentPlayerState.Large)
            if event.key == pygame.K_t:
                game.myPlayer.changeState(CONST.CurrentPlayerState.Small)
            if event.key == pygame.K_e:
                gridPos = mousePosToGrid()
                game.addBlock(gridPos, CONST.Blocks.mushroom)
        #if event.type == KEYDOWN:
        #    if event.key == pygame.K_w:
        #        game.myPlayer.jump()
    gridPos = mousePosToGrid()
    realPos = (gridPos[0] * CONST.BlockSize, gridPos[1] * CONST.BlockSize)
    realPos = Graphics.getOnScreenPos(realPos, game.myPlayer.cameraPos)
    pygame.draw.rect(display, (200, 50, 50), pygame.Rect(realPos[0], realPos[1], CONST.BlockSize, CONST.BlockSize), 1)
    
    keys = pygame.key.get_pressed()
    moving = False
    modifier = 1
    if keys[pygame.K_LSHIFT]:
        modifier = CONST.PlayerSprintIncrease
    if keys[pygame.K_d]:
        game.myPlayer.move(1 * modifier)
        moving = True
    if keys[pygame.K_a]:
        game.myPlayer.move(-1 * modifier)
        moving = True
    if keys[pygame.K_w]:
        game.myPlayer.jump()
    if not moving:
        game.myPlayer.inputDir = 0
    
    
    game.draw(display)
    
    
    pygame.display.update()
    fpsClock.tick(CONST.FPS)