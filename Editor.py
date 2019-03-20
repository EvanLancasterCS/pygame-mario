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
erasing = False
showFPS = True

recentSnapshot = [] # Snapshot after entering play mode after being in editor mode;
                    # Consists of array of tuples(pos, blockE, reward) 

pygame.font.init()
editorFont = pygame.font.SysFont('Tahoma', 12)

# Inputs: GameState game
# 
# Results: Sets recentSnapshot to consist of all blocks in game.blockList
def setSnapshot(game):
    global recentSnapshot
    recentSnapshot = []
    for block in game.blockList:
        recentSnapshot.append((block.gridPos,block.blockE,block.reward))

# Inputs: GameState game
# 
# Results: Sets game.blockList to recentSnapshot
def restoreSnapshot(game):
    global recentSnapshot
    game.blockList = []
    game.chunks = {}
    for blockInfo in recentSnapshot:
        game.addBlock(blockInfo[0],blockInfo[1])
        block = game.getBlock(blockInfo[0])
        block.reward = blockInfo[2]
    

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

# Results: Returns true if there is enough blocks for a next page
def canNextPage():
    maxPage = math.floor(len(CONST.BlockInfo.keys()) / CONST.OptionsPageLength) - 1
    return cOptionsPage <= maxPage

# Results: Returns true if can previous page
def canPrevPage():
    return cOptionsPage > 0

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
#         GameState game
#         Blocks blockE
#         tuple(x,y) pos
#
# Results: draws blockE to screen at pos
def drawFakeBlock(display, game, blockE, pos):
    blockSlug = CONST.BlockInfo[blockE][0]
    if not blockE in game.loadedImgs:
        game.loadedImgs[blockE] = pygame.image.load('Sprites/Blocks/' + blockSlug + '.png')
        game.loadedImgs[blockE] = pygame.transform.scale(game.loadedImgs[blockE], (CONST.BlockSize, CONST.BlockSize))
    display.blit(game.loadedImgs[blockE], pos)

# Inputs: pygame display
#         GameState game
#         Blocks blockE
#         tuple(x,y) gridPos
#
# Results: draws blockE to screen at gridpos
def drawFakeBlockGridPos(display, game, blockE, gridPos):
    realPos = Graphics.getOnScreenPos((gridPos[0]*CONST.BlockSize, gridPos[1]*CONST.BlockSize), game.myPlayer.cameraPos)
    drawFakeBlock(display, game, blockE, realPos)

# Inputs: pygame display
#         GameState game
#
# Results: draws all hidden rewards infront of appropriate blocks
def drawRewards(display, game):
    cameraChunk = game.blockToChunk(Graphics.screenToGrid((CONST.ScreenSizeX/2,0), game.myPlayer.cameraPos)[0])
    nearby = []
    for i in range(-CONST.DrawDistance, CONST.DrawDistance+1):
        nearby.extend(game.getChunkBlocks(cameraChunk+i))
    for block in nearby:
        if block.reward != None:
            drawFakeBlockGridPos(display, game, block.reward, (block.gridPos[0], block.gridPos[1]+0.1))

# Inputs: pygame display
#         tuple(x,y) cameraPos
#         GameState game
#         string FPS
#         Boolean mouseUp
#
# Results: draws available blocks to top of screen
#          returns enum Blocks of currently moused over, None if none moused
def drawOptions(display, cameraPos, game, fps, mouseUp):
    global cOptionsPage
    blocks = getCurrentPageBlocks()
    
    xPadding = 10
    yPadding = 10
    blockPadding = 5
    
    currXPos = 0
    mouseOver = None
    
    regularPageColor = (50, 200, 50)
    mouseOverPageColor = (125, 225, 125)
    
    if canPrevPage():
        mColor = regularPageColor
        pos = (xPadding, 2*yPadding + CONST.BlockSize)
        size = (75, 15)
        
        if (Graphics.isMouseOverArea(pos, (pos[0]+size[0],pos[1]+size[1]))):
            mColor = mouseOverPageColor
            if mouseUp:
                cOptionsPage -= 1
        
        pygame.draw.rect(display, mColor, pygame.Rect(pos[0], pos[1], size[0], size[1]))
        
        textSurf = editorFont.render('PREV', False, (0, 0, 0))
        display.blit(textSurf, (pos[0]+23, pos[1]))
    
    if canNextPage():
        mColor = regularPageColor
        pos = (xPadding + 80, 2*yPadding + CONST.BlockSize)
        size = (75, 15)
        
        if (Graphics.isMouseOverArea(pos, (pos[0]+size[0],pos[1]+size[1]))):
            mColor = mouseOverPageColor
            if mouseUp:
                cOptionsPage += 1
        
        pygame.draw.rect(display, mColor, pygame.Rect(pos[0], pos[1], size[0], size[1]))
        textSurf = editorFont.render('NEXT', False, (0, 0, 0))
        display.blit(textSurf, (pos[0]+23, pos[1]))
    
    
    # Iterate through current page's blocks
    for blockE in blocks:
        # Draw blockE choice to screen
        pos = (currXPos+xPadding, yPadding)
        drawFakeBlock(display, game, blockE, pos)
        
        # Check if mouse is currently over block choice
        if (Graphics.isMouseOverArea(pos, (pos[0]+CONST.BlockSize, pos[1]+CONST.BlockSize))):
            pygame.draw.rect(display, (200, 50, 50), pygame.Rect(pos[0], pos[1], CONST.BlockSize, CONST.BlockSize), 2)
            mouseOver = blockE
        elif blockE == cSelectedBlock:
            pygame.draw.rect(display, (50, 50, 200), pygame.Rect(pos[0], pos[1], CONST.BlockSize, CONST.BlockSize), 4)
        
        # Increment xPos for next loop
        currXPos += CONST.BlockSize + blockPadding
    
    # Draws square for eraser indicator if active
    if erasing:
        pos = (cameraPos[0]+(CONST.ScreenSizeX/2)-CONST.BlockSize-xPadding, cameraPos[1]+(CONST.ScreenSizeY/2) - yPadding,0)
        pos = Graphics.getOnScreenPos(pos, cameraPos)
        pos = (round(pos[0],0), round(pos[1],0))
        pygame.draw.rect(display, (255, 125, 125), pygame.Rect(pos[0], pos[1], CONST.BlockSize, CONST.BlockSize))
    
    # Draws FPS text in upper right if set active
    if showFPS:
        strFPS = str(fps)
        strFPS = strFPS[11:13]
        textSurf = editorFont.render('FPS: ' + strFPS, False, (0, 0, 0))
        display.blit(textSurf, (CONST.ScreenSizeX-CONST.BlockSize*1.5, yPadding))
    
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
    game.removeBlock(gridPos)
    
# Inputs: GameState game
#
# Results: Moves camera based on keyboard inputs
def checkInput(game):
    keys = pygame.key.get_pressed()
    
    speed = 10
    if keys[pygame.K_LSHIFT]:
        speed *= 2
    
    if keys[pygame.K_d]:
        game.myPlayer.forceMove((speed, 0))
    if keys[pygame.K_a] and game.myPlayer.pos[0] > 0:
        game.myPlayer.forceMove((-speed, 0))
    if keys[pygame.K_w]:
        game.myPlayer.forceMove((0, speed))
    if keys[pygame.K_s] and game.myPlayer.pos[1] > 0:
        game.myPlayer.forceMove((0, -speed))


# Inputs: pygame display
#         GameState game
#         boolean[] mouseInfo = {mouseDown, mouseUp}
#
# Results: draws full options menu & checks for input
def draw(display, game, mouse1Info, fps):
    global cSelectedBlock
    global cSelectedArea
    global mouseHeld
    
    checkInput(game)
    game.draw(display, False)
    drawRewards(display, game)
    
    mouseDown = mouse1Info[0]
    mouseUp = mouse1Info[1]
    if mouseDown:
        mouseHeld = True
    if mouseUp:
        mouseHeld = False

    cameraPos = game.myPlayer.cameraPos
    option = drawOptions(display,cameraPos,game,fps,mouseUp)
    
    canPlace = True
    
    if option == None and cSelectedBlock != None: # If nothing is moused over and no block is chosen, draw mouseover on grid pos of mouse
        drawMouseover(display,cameraPos)
    elif option != None and mouseUp: # If something is moused over and mouse is up, set canPlace to false and change current block to option
        canPlace = False
        cSelectedBlock = option
    elif cSelectedBlock == None: # If no block is selected, don't place a block
        canPlace = False
    
    # Sets up draw area and draws thikk boi
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
            
            cThickness = None
            cColor = None
            
            if erasing:
                cThickness = 5
                cColor = (255, 0, 0)
            else:
                cThickness = 1
                cColor = (255, 50, 50)
                
            pygame.draw.rect(display, cColor, pygame.Rect(info[0][0], info[0][1], info[1][0], info[1][1]), cThickness)
    
    # Places blocks / Erases blocks based on current selected area
    if canPlace and mouseUp:
        pos1 = cSelectedArea[0]
        pos2 = cSelectedArea[1]
        info = calculateBoxPos(pos1, pos2, cameraPos)
        pos = info[0]
        size = info[1]
        pos = Graphics.screenToGrid(pos, cameraPos)
        size = (size[0]/CONST.BlockSize, -size[1]/CONST.BlockSize)
        size = (math.floor(size[0])-1, math.floor(size[1])-1)
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
        
        block = game.getBlock((minX, minY))

        if erasing:
            for x in range(minX, maxX):
                for y in range(minY, maxY):
                    game.removeBlock((x, y))
        elif block != None and (minX == maxX-1 and minY == maxY-1 and block.blockE == CONST.Blocks.emptyQuestionBlock or CONST.BlockInfo[block.blockE][1] == CONST.BlockTypes.reward):
            block.reward = cSelectedBlock
            block.blockE = CONST.Blocks.questionBlock
        else:
            for x in range(minX, maxX):
                for y in range(minY, maxY):
                    game.addBlock((x, y), cSelectedBlock)
    