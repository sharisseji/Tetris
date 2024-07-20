#############################################
#   Programmer: Sharisse Ji                 #
#   Date: January 09, 2023                  #
#   File Name: SharisseJi_Tetris_MAIN.py    #
#   Description: Tetris main program        #
#############################################

# GAMEPLAY KEYS:
# <- and -> = move left and right
# up key = rotate tetra
# space = send tetra into spot
# c = "hold" the tetra and switch it with the tetra currently in hold
# v = pause

# IMPORT
from SharisseJi_Tetris_CLASSES import *
from random import randint
from math import sqrt
import pygame
import time

pygame.init()

# LOAD GAME SCREEN
HEIGHT = 600
WIDTH = 800
GRIDSIZE = HEIGHT//24
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# ----------------------------------#
#   SETUP VARIABLES                 #--------------------
# ----------------------------------#

# MUSIC AND SOUND EFFECTS--------------------------------
# will be added in Replit version

# FONTS--------------------------------------------------
font = pygame.font.Font("PhoenixiansBold.ttf", 50)

# IMAGES-------------------------------------------------
introBG = pygame.image.load("Tetris_IntroScreen.png")
introBG = pygame.transform.scale(introBG, (WIDTH, HEIGHT))
gameBG = pygame.image.load("Tetris_GamePlay.png")
gameBG = pygame.transform.scale(gameBG, (WIDTH, HEIGHT))
endBG = pygame.image.load("Tetris_EndScreen.png")
endBG = pygame.transform.scale(endBG, (WIDTH, HEIGHT))
pauseMenu = pygame.image.load("PauseMenu.png")
pauseMenu = pygame.transform.scale(pauseMenu, (WIDTH, HEIGHT))

playHover = pygame.image.load("PlayButton_Hover.png")
playHover = pygame.transform.scale(playHover, (184, 79))  # size of hovered play button image (184, 79)

pauseResumeHover = pygame.image.load("Pause_ResumeButton.png")
pauseResumeHover = pygame.transform.scale(pauseResumeHover, (228, 80))

pauseExitHover = pygame.image.load("Pause_ExitButton.png")
pauseExitHover = pygame.transform.scale(pauseExitHover, (228, 75))

endHover = pygame.image.load("ExitButton_Hover.png")
endHover = pygame.transform.scale(endHover, (184, 79))

# BUTTONS------------------------------------------------
playButton = pygame.Rect(310, 365, 184, 79)  # rectangular button area to detect clicks (not drawn)
pauseResumeButton = pygame.Rect(284, 254, 228, 80)
pauseExitButton = pygame.Rect(284, 362, 228, 75)


# GAME SCREEN DIMENSIONS----------------------------------
COLUMNS = 10
ROWS = 20
LEFT = 11
RIGHT = LEFT + COLUMNS
MIDDLE = LEFT + COLUMNS//2
TOP = 1
FLOOR = TOP + ROWS

# COLOURS-------------------------------------------------
GREY = (192, 192, 192)
DARKGREY = (20,20,20)
RED = (255, 0, 0)
WHITE = (255,255,255)
pause = False


# ----------------------------------#
#   GAME VARIABLES                  #----------------------
# ----------------------------------#

# BORDER VARIABLES-----------------------------------------
floor = Floor(LEFT, FLOOR, COLUMNS)
ceiling = Floor(LEFT, TOP, COLUMNS)
leftWall = Wall(LEFT-1, TOP, ROWS)
rightWall = Wall(RIGHT, TOP, ROWS)
obstacles = Obstacles(LEFT, FLOOR)

# SHAPE VARIABLES------------------------------------------
shapeNo = randint(1, 7)                                     # will be discarded after first turn
tetra = Shape(MIDDLE, 2, shapeNo)
shadow = Shape(MIDDLE, 2, shapeNo, True)

nextShapeNo = randint(1, 7)                                 # loads the tetra under "next"
nextTetra = Shape(RIGHT+6, 5, nextShapeNo)                  # nextTetra will always be the next tetra, never current

holdShapeNo = 0                                             # not yet assigned as hold command is not ture
holdTetra = 0
currentShapeNo = 0                                          # temporary holder of current tetra shape value
turn1 = True
onHold = False
holdUsed = False

# GAME SCREENS----------------------------------------------
introPlay = True
gamePlay = False
endPlay = False

# SCORING---------------------------------------------------
timer = 0
score = 0
speed = 10
tetris = False
level = 1


# --------------------#
#   FUNCTIONS         #--------------------------------------
# --------------------#
# SCREEN DRAWING FUNCTIONS-----------------------------------
def introScreen():                                              # draws the intro screen
        screen.blit(introBG, (0, 0))
        if playButton.collidepoint(cursorX, cursorY) is True:
            screen.blit(playHover, (310, 365))
        pygame.display.update()


def redrawScreen():
    if pause is True:
        pauseScreen()
    else:
        screen.blit(gameBG, (0, 0))
        drawGrid()

        printScore = font.render(str(score), 1, WHITE)
        screen.blit(printScore, (100, 247))

        printLevel = font.render(str(level), 1, WHITE)
        screen.blit(printLevel, (130, 355))

        printTime = font.render(str(timer//10), 1, WHITE)
        screen.blit(printTime, (110, 465))
        shadow.draw(screen, GRIDSIZE)
        tetra.draw(screen, GRIDSIZE)
        nextTetra.draw(screen, GRIDSIZE)

        if onHold is True:
            holdTetra.draw(screen, GRIDSIZE)
        obstacles.draw(screen, GRIDSIZE)                        # draw the object obstacles on screen
        pygame.display.update()


def endScreen():
    screen.blit(endBG, (0, 0))
    if playButton.collidepoint(cursorX, cursorY) is True:
        screen.blit(endHover, (310, 365))
    pygame.display.update()


def pauseScreen():
    screen.blit(pauseMenu, (0, 0))
    (cursorX, cursorY) = pygame.mouse.get_pos()
    if pauseResumeButton.collidepoint(cursorX, cursorY) is True:
        screen.blit(pauseResumeHover, (284, 254))
    if pauseExitButton.collidepoint(cursorX, cursorY) is True:
        screen.blit(pauseExitHover, (284, 362))
    pygame.display.update()


def drawGrid():  # draws faint gray lines in play screen
    for x in range(LEFT*GRIDSIZE, RIGHT*GRIDSIZE, GRIDSIZE):    # draw vertical
        pygame.draw.line(screen, DARKGREY, (x, TOP*GRIDSIZE), (x, FLOOR*GRIDSIZE))

    for y in range(TOP*GRIDSIZE, FLOOR*GRIDSIZE, GRIDSIZE):     # draw horizontal
        pygame.draw.line(screen, DARKGREY, (LEFT*GRIDSIZE, y), (RIGHT*GRIDSIZE, y))

    pygame.display.update()


# GAME PLAY FUNCTIONS-----------------------------------------
def distance(x1, y1, x2, y2):
    return sqrt((x1 - x2)**2 + (y1 - y2)**2)


def moveShadow():
    shadow.row = 1                                              # make the shadow respawn above before moving it
    shadow._update()
    while not (shadow.collides(floor) or shadow.collides(obstacles)):
        shadow.moveDown()
    shadow.moveUp()


def leftMove():
    tetra.moveLeft()
    shadow.moveLeft()
    moveShadow()


def rightMove():
    tetra.moveRight()
    shadow.moveRight()
    moveShadow()


def Score():
    # 0-1000 - level 1: starting speed (10)
    if 2000 > score >= 1000:    # after 1000 - level 2
        speed = 9
        level = 2
    elif 3000 > score >= 2000:  # after 2000- level 3
        speed = 8
        level = 3
    elif 4000 > score >= 3000:  # after 3000 - level 4: medium speed
        speed = 7
        level = 4
    elif 5000 > score >= 4000:  # after 4000 - level 5
        speed = 6
        level = 5
    elif 6000 > score >= 5000:  # after 5000 = level 6
        speed = 5
        level = 6
    elif 7000 > score >= 6000:  # after 5000 - level 7: fastest speed!
        speed = 4
        level = 7


# --------------------------------- #
#   GAMEPLAY                        #
# --------------------------------- #
# SCREEN 1: INTRO--------------------------------------------------

while introPlay:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            introPlay = False
            gamePlay = False
            endPlay = False
        (cursorX, cursorY) = pygame.mouse.get_pos()
        if playButton.collidepoint(cursorX, cursorY) is True:
            if event.type == pygame.MOUSEBUTTONDOWN:
                introPlay = False
                gamePlay = True
    introScreen()

# SCREEN 2: GAME PLAY----------------------------------------------
while gamePlay is True:
    (cursorX, cursorY) = pygame.mouse.get_pos()

    # TIMER
    timer = pygame.time.get_ticks() // 100
    time.sleep(0.08)

    # IN THE CASE OF KEY PRESSED EVENT
    for event in pygame.event.get():
        if event.type == pygame.QUIT:                                     # if game is exited
            gamePlay = False
            introPlay = False
            endPlay = False

        # KEY PRESSED
        if pause is True:
            if pauseResumeButton.collidepoint(cursorX, cursorY) is True:  # if resume button is clicked
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pause = False

            if pauseExitButton.collidepoint(cursorX, cursorY) is True:    # if exit button is clicked
                if event.type == pygame.MOUSEBUTTONDOWN:
                    gamePlay = False
                    endPlay = False

        if event.type == pygame.KEYDOWN:                                  # if pause button is clicked (V key)
            if event.key == pygame.K_v:
                pause = True

            if event.key == pygame.K_UP:  # rotate
                tetra.rotateClkwise()
                shadow.rotateClkwise()
                moveShadow()
                if tetra.collides(leftWall) or tetra.collides(rightWall) or tetra.collides(floor) or tetra.collides(obstacles):
                    tetra.rotateCntclkwise()  # if rotating while colliding with the wall, don't rotate
                    shadow.rotateCntclkwise()
                    moveShadow()

            if event.key == pygame.K_LEFT:
                leftMove()
                if tetra.collides(leftWall):
                    rightMove()
            if event.key == pygame.K_RIGHT:
                rightMove()
                if tetra.collides(rightWall):
                    leftMove()

            if event.key == pygame.K_SPACE:
                while not (tetra.collides(floor) or tetra.collides(obstacles)):
                    tetra.moveDown()
                tetra.moveUp()
                obstacles.append(tetra)

                currentShapeNo = nextShapeNo
                tetra = Shape(MIDDLE, 2, nextShapeNo)  # generates new next shape
                shadow = Shape(MIDDLE, 2, nextShapeNo, True)

                nextShapeNo = randint(1, 7)
                nextTetra = Shape(RIGHT+5, 5, nextShapeNo)
                turn1 = False
                holdUsed = False

            if event.key == pygame.K_c and holdUsed is False:
                if onHold is False:  # if this is the first time clicking C and NO tetra is on hold
                    if turn1 is True:
                        holdShapeNo = shapeNo
                        turn1 = False
                    else:
                        holdShapeNo = currentShapeNo
                    holdTetra = Shape(LEFT-6, 5, holdShapeNo)  # draw the new hold tetra

                    currentShapeNo = nextShapeNo
                    tetra = Shape(MIDDLE, 2, nextShapeNo)  # generates new next shape
                    shadow = Shape(MIDDLE, 2, nextShapeNo, True)

                    nextShapeNo = randint(1, 7)
                    nextTetra = Shape(RIGHT+5, 5, nextShapeNo)
                    onHold = True
                else:
                    tetra = Shape(MIDDLE, 2, holdShapeNo)  # draw the old hold tetra (now tetra) in the game screen
                    shadow = Shape(MIDDLE, 2, holdShapeNo, True)
                    holdShapeNo = currentShapeNo
                    holdTetra = Shape(LEFT-6, 5, holdShapeNo)
                holdUsed = True

    moveShadow()

    # IF THERE IS NO EVENT -----------------------------------
    if timer % speed == 0:
        tetra.moveDown()
        if pause is True:
            tetra.moveUp()
        if tetra.collides(floor) or tetra.collides(obstacles):  # ADD TETRA TO OBSTACLES
            tetra.moveUp()
            obstacles.append(tetra)

            currentShapeNo = nextShapeNo
            tetra = Shape(MIDDLE, 2, nextShapeNo)  # generates new next shape
            shadow = Shape(MIDDLE, 2, nextShapeNo, True)

            nextShapeNo = randint(1, 7)
            nextTetra = Shape(RIGHT+5, 5, nextShapeNo)
            turn1 = False
            holdUsed = False

    if obstacles.collides(ceiling):
        gamePlay = False
        endPlay = True

    # FIND OUT IF ROWS ARE FULL OR NOT
    fullRows = obstacles.findFullRows(TOP, FLOOR, COLUMNS)  # finds full rows, removes their blocks from the obstacles
    if len(fullRows) == 4:  # tetris score
        score += len(fullRows)*200
    else:
        score += len(fullRows)*100
    obstacles.removeFullRows(fullRows)
    # obstacles.show()
    Score()
    redrawScreen()
    pygame.time.delay(speed)


# SCREEN 3: GAME OVER
while endPlay is True:
    endScreen()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            endPlay = False
        (cursorX, cursorY) = pygame.mouse.get_pos()
        # print((cursorX, cursorY))
        if playButton.collidepoint(cursorX, cursorY) is True:
            if event.type == pygame.MOUSEBUTTONDOWN:
                endPlay = False
pygame.quit()
