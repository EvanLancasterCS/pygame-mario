'''
    Created on 3/11/19
'''
# Graphics Constants
FPS = 60
ScreenSizeX = 1001
ScreenSizeY = 800
BlockSize = 40
AnimTickrate = 0.08

# Physics Constants
Gravity = 40 * (1 / FPS)

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
