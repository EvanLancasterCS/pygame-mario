'''
    Created on 3/18/19
'''
import Constants as CONST
import Graphics
import math
import pygame

cOptionsPage = 0 # Current page
cSelectedBlock = None # Current block
mouseHeld = False
cSelectedArea = [] # Currently selected area

# Inputs: tuple(x,y) cameraPos
#
# Results: Returns tuple(x,y) gridpos of mouse
def mousePosToGrid(cameraPos):
    mPos = pygame.mouse.get_pos()
    mPos = (mPos[0]-CONST.ScreenSizeX/2, mPos[1]-CONST.ScreenSizeY/2)
    mPos = (mPos[0]+cameraPos[0], -mPos[1]+cameraPos[1]+CONST.BlockSize)
    gridPos = [mPos[0]/CONST.BlockSize, mPos[1]/CONST.BlockSize]
    gridPos = (math.floor(gridPos[0]), math.floor(gridPos[1]))
    return gridPos

# Inputs: pygame display
#         tuple(x,y) cameraPos
#
# Results: draws indicator around current moused over grid position
def drawMouseover(display, cameraPos):
    gridPos = mousePosToGrid(cameraPos)
    realPos = (gridPos[0] * CONST.BlockSize, gridPos[1] * CONST.BlockSize)
    realPos = Graphics.getOnScreenPos(realPos, cameraPos)
    pygame.draw.rect(display, (200, 50, 50), pygame.Rect(realPos[0], realPos[1], CONST.BlockSize, CONST.BlockSize), 1)

# Results: Returns array of enum Blocks that should be displayed
def getCurrentPageBlocks():
    blocks = []
    minimum = cOptionsPage * CONST.OptionsPageLength
    maximum = (cOptionsPage+1) * CONST.OptionsPageLength
    cIndex = 0
    for key in CONST.BlockInfo.keys():
        if cIndex >= minimum and cIndex < maximum:
            blocks.append(key)
        elif cIndex >= maximum:
            break
        cIndex += 1
    return blocks

# Inputs: pygame display
#         tuple(x,y) cameraPos
#         GameState game
#
# Results: draws available blocks to top of screen
#          returns enum Blocks of currently moused over, None if none moused
def drawOptions(display, cameraPos, game):
    blocks = getCurrentPageBlocks()
    
    xPadding = 10
    yPadding = 10
    blockPadding = 5
    
    currXPos = 0
    mouseOver = None
    for blockE in blocks:
        blockSlug = CONST.BlockInfo[blockE][0]
        if not blockE in game.loadedImgs:
            game.loadedImgs[blockE] = pygame.image.load('Sprites/Blocks/' + blockSlug + '.png')
            game.loadedImgs[blockE] = pygame.transform.scale(game.loadedImgs[blockE], (CONST.BlockSize, CONST.BlockSize))
        pos = (cameraPos[0]-(CONST.ScreenSizeX/2) + currXPos + xPadding, cameraPos[1]+(CONST.ScreenSizeY/2) - yPadding,0)
        pos = Graphics.getOnScreenPos(pos, cameraPos)
        pos = (round(pos[0],0), round(pos[1],0))
        display.blit(game.loadedImgs[blockE], pos)
        if (Graphics.isMouseOverArea(pos, (pos[0]+CONST.BlockSize, pos[1]+CONST.BlockSize))):
            pygame.draw.rect(display, (200, 50, 50), pygame.Rect(pos[0], pos[1], CONST.BlockSize, CONST.BlockSize), 2)
            mouseOver = blockE
        elif blockE == cSelectedBlock:
            pygame.draw.rect(display, (50, 50, 200), pygame.Rect(pos[0], pos[1], CONST.BlockSize, CONST.BlockSize), 4)
        currXPos += CONST.BlockSize + blockPadding
    return mouseOver

# Inputs: tuple(x,y) pos1
#         tuple(x,y) pos2
#
# Results: Returns position and size of given box pos1 to pos2
#          tuple (pos, size)
def calculateBoxPos(pos1, pos2, cameraPos):
    pos1 = (pos1[0] * CONST.BlockSize, pos1[1] * CONST.BlockSize)
    pos2 = (pos2[0] * CONST.BlockSize, pos2[1] * CONST.BlockSize)
    pos1 = Graphics.getOnScreenPos(pos1, cameraPos)
    pos2 = Graphics.getOnScreenPos(pos2, cameraPos)
    size = (pos2[0] - pos1[0], pos2[1] - pos1[1])
    if pos2[0] >= pos1[0]:
        size = (size[0] + CONST.BlockSize, size[1])
    else:
        pos1 = (pos1[0] + CONST.BlockSize, pos1[1])
        size = (size[0] - CONST.BlockSize, size[1])
    if pos2[1] >= pos1[1]:
        size = (size[0], size[1] + CONST.BlockSize)
    else:
        pos1 = (pos1[0], pos1[1] + CONST.BlockSize)
        size = (size[0], size[1] - CONST.BlockSize)
    return (pos1, size)

# Inputs: tuple(x,y) gridPos
#         GameState game
#
# Results: Removes block if exists at gridPos
def removeBlock(gridPos, game):
    if game.blockExistsAtPos(gridPos):
        b = None
        for block in game.blockList:
            if block.gridPos[0] == gridPos[0] and block.gridPos[1] == gridPos[1]:
                b = block
                break
        game.blockList.remove(b) 

# Inputs: pygame display
#         GameState game
#         boolean[] mouseInfo = {mouseDown, mouseUp}
#
# Results: draws full options menu & checks for input
def draw(display, game, mouse1Info):
    global cSelectedBlock
    global cSelectedArea
    global mouseHeld
    
    mouseDown = mouse1Info[0]
    mouseUp = mouse1Info[1]
    if mouseDown:
        mouseHeld = True
    if mouseUp:
        mouseHeld = False

    cameraPos = game.myPlayer.cameraPos
    option = drawOptions(display,cameraPos,game)
    
    canPlace = True
    
    if option == None and cSelectedBlock != None:
        drawMouseover(display,cameraPos)
    elif option != None and mouseUp:
        canPlace = False
        cSelectedBlock = option
    elif cSelectedBlock == None:
        canPlace = False
    
    if cSelectedBlock != None and canPlace:
        if mouseDown:
            cSelectedArea = []
            mPos = mousePosToGrid(cameraPos)
            mPos = (mPos[0], mPos[1])
            cSelectedArea.append(mPos)
        if mouseUp:
            mPos = mousePosToGrid(cameraPos)
            mPos = (mPos[0]+1, mPos[1]+1)
            cSelectedArea.append(mPos)
        if mouseHeld:
            pos1 = cSelectedArea[0]
            pos2 = mousePosToGrid(cameraPos)
            info = calculateBoxPos(pos1, pos2, cameraPos)
            
            pygame.draw.rect(display, (200, 50, 50), pygame.Rect(info[0][0], info[0][1], info[1][0], info[1][1]), 1)
    
    if canPlace and mouseUp:
        pos1 = cSelectedArea[0]
        pos2 = cSelectedArea[1]
        info = calculateBoxPos(pos1, pos2, cameraPos)
        pos = info[0]
        size = info[1]
        pos = Graphics.screenToGrid(pos, cameraPos)
        print(pos)
        print(size)
        size = (size[0]/CONST.BlockSize, -size[1]/CONST.BlockSize)
        size = (math.floor(size[0])-1, math.floor(size[1])-1)
        print(size)
        if size[0] == 0:
            size = (-2, size[1])
            pos = (pos[0]+1, pos[1])
        x1 = pos[0]
        x2 = pos[0]+size[0]
        y1 = pos[1]
        y2 = pos[1]+size[1]
        minX = min(x1, x2)
        maxX = max(x1, x2)
        minY = min(y1, y2)
        maxY = max(y1, y2)
        
        for x in range(minX, maxX):
            for y in range(minY, maxY):
                game.addBlock((x, y), cSelectedBlock)
    