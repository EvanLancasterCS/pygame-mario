'''
    Created on 3/11/19
'''
from enum import Enum
# Graphics Constants
FPS = 60
ScreenSizeX = 1000
ScreenSizeY = 800
BlockSize = 40
AnimTickrate = 0.08
DrawDistance = 4

# Editor Constants
OptionsPageLength = 8

# Physics Constants
Gravity = 40 * (1 / FPS)
ChunkSize = 4

# Player Constants
PlayerSizeX = 38
PlayerSizeY = 40
PlayerLargeSizeY = 60

MaxPlayerSpeed = 4.1
MaxFallSpeed = 26
PlayerAirStruggle = 4
PlayerSprintIncrease = 2
PlayerAcceleration = 24 * (1 / FPS)
PlayerFriction = 6
PlayerJumpForce = 7
PlayerMaxJumpTime = 0.25

# Enums

class CurrentPlayerState(Enum):
    Small = 0
    Large = 1

class Blocks(Enum):
    groundRock = 0
    wallBrick = 1
    mushroom = 2

class BlockTypes(Enum):
    unbreakable = 0 # Block Info Format: (string slug, BlockTypes type)
    breakable = 1   # Block Info Format: (string slug, BlockTypes type)
    reward = 2      # Block Info Format: 
    powerup = 3     # Block Info Format: (string slug, BlockTypes type, CurrentPlayerState state, Boolean moving, Boolean gravity)

BlockInfo = {
    Blocks.groundRock: ("ground-rock",BlockTypes.unbreakable),
    Blocks.wallBrick: ("wall-brick",BlockTypes.breakable),
    Blocks.mushroom: ("mushroom",BlockTypes.powerup,CurrentPlayerState.Large,True,True)
    }

