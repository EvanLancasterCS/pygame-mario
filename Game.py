'''
    Created on 3/11/2019
''' 
import pygame
import sys
import GameState as GS
import Constants as CONST
from pygame.locals import *


fpsClock = pygame.time.Clock()

display = pygame.display.set_mode((CONST.ScreenSizeX, CONST.ScreenSizeY))

game = GS.Game()
for x in range(-15, 15):
    for y in range(-15, 0):
        game.addBlock((x,y), GS.Blocks.groundRock)
        
game.addBlock((4, 0), GS.Blocks.wallBrick)
game.addBlock((4, 1), GS.Blocks.wallBrick)
game.addBlock((4, 2), GS.Blocks.wallBrick)
game.addBlock((4, 3), GS.Blocks.wallBrick)
game.addBlock((1,0), GS.Blocks.wallBrick)

while True:
    display.fill((0,0,0))
    
    
    
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
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
    
    
    game.myPlayer.tick()
    game.myPlayer.draw(display)
    for block in game.blockList:
        if block.isOnScreen(game.myPlayer.cameraPos):
            block.draw(display, game.myPlayer.cameraPos)
    
    pygame.display.update()
    fpsClock.tick(CONST.FPS)