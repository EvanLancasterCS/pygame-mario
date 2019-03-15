'''
    Created on 3/11/19
''' 
import pygame
import sys
import GameState as GS
import Constants as CONST
from pygame.locals import *
from Player import CurrentPlayerState

fpsClock = pygame.time.Clock()

display = pygame.display.set_mode((CONST.ScreenSizeX, CONST.ScreenSizeY))

game = GS.Game()
for x in range(-15, 15):
    for y in range(-1, 0):
        game.addBlock((x,y), GS.Blocks.groundRock)
        
game.addBlock((4, 0), GS.Blocks.wallBrick)
game.addBlock((4, 1), GS.Blocks.wallBrick)
game.addBlock((4, 3), GS.Blocks.wallBrick)
for x in range(15):
    game.addBlock((x, 4), GS.Blocks.wallBrick)
game.addBlock((16, -4), GS.Blocks.groundRock)

while True:
    display.fill((100, 120, 180))
    
    
    
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == MOUSEBUTTONDOWN:
            mPos = pygame.mouse.get_pos()
            mPos = (mPos[0]-CONST.ScreenSizeX/2, mPos[1]-CONST.ScreenSizeY/2)
            mPos = (mPos[0]+game.myPlayer.cameraPos[0], -mPos[1]+game.myPlayer.cameraPos[1]+CONST.BlockSize)
            gridPos = [int(mPos[0]/CONST.BlockSize), int(mPos[1]/CONST.BlockSize)]
            if gridPos[0] < 0:
                gridPos[0] -= 1
            if gridPos[1] < 0:
                gridPos[1] -= 1
            game.addBlock(gridPos, GS.Blocks.wallBrick)
        if event.type == KEYDOWN:
            if event.key == pygame.K_r:
                game.myPlayer.changeState(CurrentPlayerState.Large)
        #if event.type == KEYDOWN:
        #    if event.key == pygame.K_w:
        #        game.myPlayer.jump()
                
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