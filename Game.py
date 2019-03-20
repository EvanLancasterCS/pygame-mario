'''
    Created on 3/11/19
''' 
import pygame
import sys
import GameState as GS
import Constants as CONST
import Graphics
import math
import Editor
from pygame.locals import *

fpsClock = pygame.time.Clock()

display = pygame.display.set_mode((CONST.ScreenSizeX, CONST.ScreenSizeY))
pygame.init()
pygame.font.init()
game = GS.Game()

gType = 1

for x in range(0, 3):
    for y in range(0, 2):
        game.addBlock((x, y), CONST.Blocks.groundRock)

while True:
    display.fill((100, 120, 180))
    mouseDown = False
    mouseUp = False

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            mouseDown = True
        if event.type == MOUSEBUTTONUP and event.button == 1:
            mouseUp = True
        if event.type == KEYDOWN:
            if event.key == pygame.K_r:
                game.myPlayer.changeState(CONST.CurrentPlayerState.Large)
            if event.key == pygame.K_t:
                game.myPlayer.changeState(CONST.CurrentPlayerState.Small)
            if event.key == pygame.K_s:
                game.myPlayer.crouch()
            if event.key == pygame.K_q:
                Editor.erasing = not Editor.erasing
            if event.key == pygame.K_TAB:
                if gType == 1:
                    gType = 0
                    Editor.setSnapshot(game)
                else:
                    gType = 1
                    Editor.restoreSnapshot(game)
        if event.type == KEYUP:
            if event.key == pygame.K_s:
                game.myPlayer.uncrouch()

    
    keys = pygame.key.get_pressed()
    moving = False
    modifier = 1
    
    if gType == 0:
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
    
    if gType == 0:
        game.draw(display)
    elif gType == 1:
        Editor.draw(display, game, [mouseDown, mouseUp], fpsClock)
        
    
    #game.draw(display)
    #Editor.draw(display, game, [mouseDown, mouseUp], fpsClock)
    
    pygame.display.update()
    fpsClock.tick(CONST.FPS)