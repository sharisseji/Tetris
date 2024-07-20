#############################################
#   Programmer: Sharisse Ji                 #
#   Date: January 09, 2023                  #
#   File Name: SharisseJi_Tetris_CLASSES.py #
#   Description: Classes for Tetris Game    #
#############################################
import pygame

# ------ COLOURS ----------#
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 127, 0)
CYAN = (0, 183, 235)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GREY = (192, 192, 192)
COLOURS = [BLACK,  RED,  GREEN,  BLUE,  ORANGE,  CYAN,  MAGENTA,  YELLOW,  WHITE]
CLRNames = ['black', 'red', 'green', 'blue', 'orange', 'cyan', 'magenta', 'yellow', 'white']
figures =  [None,     'Z',    'S',    'J',     'L',      'I',     'T',      'O',     None  ]


class Block(object):  # square: basic building block
    def __init__(self, col=1, row=1, clr=1, shadow=False):
        self.col = col  # x coordinate
        self.row = row  # y coordinate
        self.clr = clr
        self.shadow = shadow

    def __str__(self):  # print the coords and colour
        return '('+str(self.col)+','+str(self.row)+') '+CLRNames[self.clr]

    def __eq__(self, other):  # collisions with another block
        if self.col == other.col and self.row == other.row:
            return True
        return False

    def draw(self, surface, gridsize=20):  # draws the grid
        x = self.col * gridsize
        y = self.row * gridsize
        CLR = COLOURS[self.clr]
        if self.shadow is True:
            pygame.draw.rect(surface, GREY, (x, y, gridsize, gridsize), 0)
            pygame.draw.rect(surface, WHITE, (x, y, gridsize+1, gridsize+1), 1)
        else:
            pygame.draw.rect(surface, CLR, (x, y, gridsize, gridsize), 0)
            pygame.draw.rect(surface, WHITE, (x, y, gridsize+1, gridsize+1), 1)

    def moveDown(self):  # for any block
        self.row = self.row + 1

    def moveUp(self):
        self.row = self.row - 1


# --------------------------------------- #
class Cluster(object):  # collection of blocks, will make up the falling tetras and obstacles (GROUP of blocks)
    def __init__(self, col=1, row=1, blocksNo=1, shadow=False):
        self.col = col
        self.row = row
        self.shadow = shadow

        # to use in Block objects
        self.blocks = [Block()]*blocksNo  # empty list with given # of empty spaces to store multiple Block objects
        self._colOffsets = [0]*blocksNo  # list of the 4 X block coords that make up tetra
        self._rowOffsets = [0]*blocksNo  # list of the 4 Y block coords that make up tetra

        self.clr = 0  # for use in _update

    def _update(self):
        # make a GROUP of blocks using LISTS of parameters to put into class
        for i in range(len(self.blocks)):
            blockCOL = self.col+self._colOffsets[i]
            blockROW = self.row+self._rowOffsets[i]
            blockCLR = self.clr
            blockSHDW = self.shadow
            self.blocks[i] = Block(blockCOL, blockROW, blockCLR, blockSHDW)  # make Block object

    def draw(self, surface, gridsize):
        for block in self.blocks:  # draw all of the blocks in the cluster list you just made in _update
            block.draw(surface, gridsize)

    # compares if each block from one cluster conflicts with ALL blocks from another cluster
    def collides(self, other):
        for block in self.blocks:
            for obstacle in other.blocks:
                if block == obstacle:           # using __eq__
                    return True                 # only if there is location conflict
        return False                            # collision is only false at end of for loop

    def append(self, other):                    # Append all blocks from another cluster to this one
        for block in other.blocks:              # (for use in obstacles and full rows)
            self.blocks.append(block)


# --------------------------------------- #
class Obstacles(Cluster):  # Collection of tetra blocks on the playing field left from previous shapes
    def __init__(self, col=0, row=0, blocksNo = 0):
        Cluster.__init__(self, col, row, blocksNo)  # initially playing field is empty (no shapes left inside field)

    def show(self):                                 # prints coordinates of each block in obstacles for checking
        print("\nObstacle: ")
        for block in self.blocks:
            print(block)

    def findFullRows(self, top, bottom, columns):   # checks if the row is full of blocks
        fullRows = []
        rows = []
        for block in self.blocks:
            rows.append(block.row)                  # make a list with only the row numbers of all blocks

        for row in range(top, bottom):              # starting from the top (row 0), and down to the bottom
            if rows.count(row) == columns:          # if the number of blocks with certain row number
                fullRows.append(row)                # equals to the number of columns -> the row is full
        return fullRows                             # return a list with the full rows' numbers

    def removeFullRows(self, fullRows):             # if row is full, remove that row
        for row in fullRows:                        # for each full row, STARTING FROM THE TOP (fullRows are in order)
            # above: makes sure all affected tiles are being run through in the for loop
            for i in reversed(range(len(self.blocks))):  # check all obstacle blocks in REVERSE ORDER
                if self.blocks[i].row == row:       # so when popping the index doesn't go out of range
                    self.blocks.pop(i)              # remove each block that is on this row
                elif self.blocks[i].row < row:
                    self.blocks[i].moveDown()       # move down each block that is above this row


# --------------------------------------- #
class Shape(Cluster):  # used to make a tetra
    def __init__(self, col=1, row=1, clr=1, shapeShadow = False):
        Cluster.__init__(self, col, row, 4, shapeShadow)
        self.clr = clr
        self.shadow = shapeShadow                   # inherited from cluster, used in block
        self._rot = 1
        self._colOffsets = [-1, 0, 0, 1]            # inherited from cluster class
        self._rowOffsets = [-1,-1, 0, 0]            # inherited from cluster class
        self._rotate()

    def __str__(self):
        return figures[self.clr]+' ('+str(self.col)+','+str(self.row)+') '+CLRNames[self.clr]

    def _rotate(self):                              # offsets assigned starting from the farthest block from anchor
        if self.clr == 1:                           # (default rotation)
            #                   o             o o                o
            #                 o x               x o            x o          o x
            #                 o                                o              o o
            _colOffsets = [[-1,-1, 0, 0], [-1, 0, 0, 1], [ 1, 1, 0, 0], [ 1, 0, 0,-1]]
            _rowOffsets = [[ 1, 0, 0,-1], [-1,-1, 0, 0], [-1, 0, 0, 1], [ 1, 1, 0, 0]]
        elif self.clr == 2:
            #                 o                 o o           o
            #                 o x             o x             x o             x o
            #                   o                               o           o o
            _colOffsets = [[-1,-1, 0, 0], [ 1, 0, 0,-1], [ 1, 1, 0, 0], [-1, 0, 0, 1]]
            _rowOffsets = [[-1, 0, 0, 1], [-1,-1, 0, 0], [ 1, 0, 0,-1], [ 1, 1, 0, 0]]
        elif self.clr == 3:
            #                   o             o                o o
            #                   x             o x o            x           o x o
            #                 o o                              o               o
            _colOffsets = [[-1, 0, 0, 0], [-1,-1, 0, 1], [ 1, 0, 0, 0], [ 1, 1, 0,-1]]
            _rowOffsets = [[ 1, 1, 0,-1], [-1, 0, 0, 0], [-1,-1, 0, 1], [ 1, 0, 0, 0]]
        elif self.clr == 4:
            #                 o o                o             o
            #                   x            o x o             x           o x o
            #                   o                              o o         o
            _colOffsets = [[-1, 0, 0, 0], [1, 1, 0,-1], [1, 0, 0, 0], [-1, -1, 0,1]]
            _rowOffsets = [[-1,-1, 0, 1], [-1,0, 0, 0], [1, 1, 0,-1], [1, 0, 0, 0]]
        elif self.clr == 5:
            #                   o                              o
            #                   o                              x
            #                   x            o x o o           o          o o x o
            #                   o                              o
            _colOffsets = [[ 0, 0, 0, 0], [ 2, 1, 0,-1], [ 0, 0, 0, 0], [-2,-1, 0, 1]]
            _rowOffsets = [[-2,-1, 0, 1], [ 0, 0, 0, 0], [ 2, 1, 0,-1], [ 0, 0, 0, 0]]
        elif self.clr == 6:
            #                   o              o                o
            #                 o x            o x o              x o         o x o
            #                   o                               o             o
            _colOffsets = [[ 0,-1, 0, 0], [-1, 0, 0, 1], [ 0, 1, 0, 0], [ 1, 0, 0,-1]]
            _rowOffsets = [[ 1, 0, 0,-1], [ 0,-1, 0, 0], [-1, 0, 0, 1], [ 0, 1, 0, 0]]
        elif self.clr == 7:
            #                   o o            o o               o o          o o
            #                   o x            o x               o x          o x

            _colOffsets = [[-1,-1, 0, 0], [-1,-1, 0, 0], [-1,-1, 0, 0], [-1,-1, 0, 0]]
            _rowOffsets = [[ 0,-1, 0,-1], [ 0,-1, 0,-1], [ 0,-1, 0,-1], [ 0,-1, 0,-1]]

        self._colOffsets = _colOffsets[self._rot]
        self._rowOffsets = _rowOffsets[self._rot]
        self._update()

    # MOVE shape-----------------------#
    def moveLeft(self):
        self.col = self.col - 1
        self._update()

    def moveRight(self):
        self.col = self.col + 1
        self._update()

    def moveDown(self):
        self.row = self.row + 1
        self._update()

    def moveUp(self):
        self.row = self.row - 1
        self._update()

    # ROTATE shape----------------------#
    def rotateClkwise(self):
        self._rot=(self._rot+1)%4
        self._rotate()

    def rotateCntclkwise(self):
        self._rot=(self._rot-1)%4
        self._rotate()


# ---------------------------------------#
class Floor(Cluster):                               # Loads the floor blocks
    def __init__(self, col=1, row=1, blocksNo=1):
        Cluster.__init__(self, col, row, blocksNo)
        for i in range(blocksNo):
            self._colOffsets[i] = i                 # Horizontal line of blocks
        self._update()


# ---------------------------------------#
class Wall(Cluster):                                # Loads the wall blocks
    def __init__(self, col=1, row=1, blocksNo=1):
        Cluster.__init__(self, col, row, blocksNo)
        for i in range(blocksNo):                   # Vertical line of blocks
            self._rowOffsets[i] = i
        self._update()
