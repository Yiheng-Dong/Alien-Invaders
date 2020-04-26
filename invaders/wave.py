"""
Subcontroller module for Alien Invaders

This module contains the subcontroller to manage a single level or wave in the Alien
Invaders game.  Instances of Wave represent a single wave.  Whenever you move to a
new level, you are expected to make a new instance of the class.

The subcontroller Wave manages the ship, the aliens and any laser bolts on screen.
These are model objects.  Their classes are defined in models.py.

Most of your work on this assignment will be in either this module or models.py.
Whether a helper method belongs in this module or models.py is often a complicated
issue.  If you do not know, ask on Piazza and we will answer.

Name: Yiheng Dong yd83, Zeyi Qiu zq35
Date: November 30, 2018
"""
from game2d import *
from consts import *
from models import *
import random

# PRIMARY RULE: Wave can only access attributes in models.py via getters/setters
# Wave is NOT allowed to access anything in app.py (Subcontrollers are not permitted
# to access anything in their parent. To see why, take CS 3152)


class Wave(object):
    """
    This class controls a single level or wave of Alien Invaders.

    This subcontroller has a reference to the ship, aliens, and any laser bolts on screen.
    It animates the laser bolts, removing any aliens as necessary. It also marches the
    aliens back and forth across the screen until they are all destroyed or they reach
    the defense line (at which point the player loses). When the wave is complete, you
    should create a NEW instance of Wave (in Invaders) if you want to make a new wave of
    aliens.

    If you want to pause the game, tell this controller to draw, but do not update.  See
    subcontrollers.py from Lecture 24 for an example.  This class will be similar to
    than one in how it interacts with the main class Invaders.

    #UPDATE ME LATER
    INSTANCE ATTRIBUTES:
        _ship:   the player ship to control [Ship]
        _aliens: the 2d list of aliens in the wave [rectangular 2d list of Alien or None]
        _bolts:  the laser bolts currently on screen [list of Bolt, possibly empty]
        _dline:  the defensive line being protected [GPath]
        _lives:  the number of lives left  [int >= 0]
        _time:   The amount of time since the last Alien "step" [number >= 0]

    As you can see, all of these attributes are hidden.  You may find that you want to
    access an attribute in class Invaders. It is okay if you do, but you MAY NOT ACCESS
    THE ATTRIBUTES DIRECTLY. You must use a getter and/or setter for any attribute that
    you need to access in Invaders.  Only add the getters and setters that you need for
    Invaders. You can keep everything else hidden.

    You may change any of the attributes above as you see fit. For example, may want to
    keep track of the score.  You also might want some label objects to display the score
    and number of lives. If you make changes, please list the changes with the invariants.

    LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
        _direction: the direction of aliens' march [int, 1 for right, -1 for left]
        _aliensdown: whether the aliens have been moved down after they touch the edge [bool]
        _key: whether 'S' key has been pressed or not [bool]
        _boltstep: the random steps of aliens between each bolt [int, 1 <= _boltstep <= BOLT_RATE]
        _alienstep: the number of steps aliens march after last alien's bolt [int, 0 <= _alienstep <= _boltstep]
        _shipsound: the sound effect when the ship bolts [Sound]
        _aliensound: the sound effect when an alien bolts [Sound]
        _shipexplode: the sound effect when the ship is hit by bolt [Sound]
        _alienexplode: the sound effect when an alien is hit by bolt [Sound]
        _score: the score summed as the player fires aliens [int >= 0]
        _alienspeed: the speed of aliens march [float]
    """

    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    def getAliens(self):
        """
        Returns self._aliens (the 2d list of aliens in the wave).
        """
        return self._aliens

    def getShip(self):
        """
        Returns self._ship (the ship to control).
        """
        return self._ship

    def getBolts(self):
        """
        Returns self._bolts (the laser bolts currently on screen).
        """
        return self._bolts

    def getLives(self):
        """
        Returns self._lives (the number of lives left).
        """
        return self._lives

    def getScore(self):
        """
        Returns self._score (the score summed as the player fires aliens).
        """
        return self._score

    def getSound(self):
        """
        Returns self._shipsound (the sound of the ship).
        """
        return self._shipsound

    def setSound(self):
        """
        Sets the sounds produced by ship, alien, ship explosion and alien
        explosion with the respective sound files.
        """
        self._shipsound = Sound('pew1.wav')
        self._aliensound = Sound('pew2.wav')
        self._shipexplode = Sound('blast1.wav')
        self._alienexplode = Sound('pop1.wav')

    # INITIALIZER (standard form) TO CREATE SHIP AND ALIENS
    def __init__(self):
        """
        Initializer: Create a wave with all attributes set in determined values.
        """
        self._aliens = self._aliensList()
        self._ship = Ship(GAME_WIDTH/2,SHIP_BOTTOM+SHIP_HEIGHT/2,SHIP_WIDTH,
            SHIP_HEIGHT,'ship.png')
        self._time = 0
        self._direction = 1
        self._aliensdown = True
        self._bolts = []
        self._key = False
        self._boltstep = random.randint(1,BOLT_RATE)
        self._alienstep = 0
        self._lives = SHIP_LIVES
        self._score = 0
        self._alienspeed = ALIEN_SPEED
        self.setSound()

    # UPDATE METHOD TO MOVE THE SHIP, ALIENS, AND LASER BOLTS
    def isWinning(self):
        """
        Returns: True if there is no aliens on the screen; False otherwise

        Determines whether the player is wining
        """
        for row in self.getAliens():
            for alien in row:
                if not alien is None:
                    return False
        return True

    def isLosing(self):
        """
        Returns: True if the most bottom alien touches the defense line;
        False otherwise

        Determines whether the game is losing
        """
        mostbottom = self._determineBottomAlien()
        if mostbottom.bottom <= DEFENSE_LINE:
            return True
        return False

    def updateShip(self,input):
        """
        This method checks for a 'left' or 'right' key press, and if there is
        one, move the ship left or right. However, the ship cannot be moved
        outside the screen.

        Parameter input: the user input, used to control the ship and
        change state
        Precondition: instance of GInput [GInput]
        """
        if not self._ship is None:
            self._shipCollision()
            if not self._ship is None:
                if input.is_key_down('left') and self._ship.x >= SHIP_WIDTH/2:
                    self._ship.x -= SHIP_MOVEMENT
                if (input.is_key_down('right') and
                    self._ship.x <= GAME_WIDTH-SHIP_WIDTH/2):
                    self._ship.x += SHIP_MOVEMENT

    def updateAliens(self,dt):
        """
        Moves the aliens in the respective direction (left, right or down)

        Parameter dt: The time in seconds since last update
        Precondition: dt is a number (int or float)
        """
        self._aliensCollision()
        self._time += dt
        if self._time >= self._alienspeed:
            mostleft = self._determineLeftAlien()
            mostright = self._determineRightAlien()
            if (GAME_WIDTH-mostright.right <= ALIEN_H_SEP
                or mostleft.left <= ALIEN_H_SEP):
                self._handleEdge()
            else:
                for row in self.getAliens():
                    for alien in row:
                        if not alien is None:
                            alien.x += self._direction*ALIEN_H_WALK
            self._time = 0
            self._alienstep += 1

    def updateBolts(self,input):
        """
        Generates, moves and removes the laser bolts fired by the ship and aliens.

        Parameter input: the user input, used to control the ship and change state
        Precondition: instance of GInput [GInput]
        """
        check = False
        i = 0
        while i < len(self._bolts):
            if self._bolts[i].bottom >= GAME_HEIGHT or self._bolts[i].top <= 0:
                del self._bolts[i]
            else:
                i += 1
        self._aliensBolt()
        for bolt in self._bolts:
            bolt.y += bolt.getVelocity()
            check = (check or bolt.isPlayerBolt())
        self._shipBolt(input,check)

    def setNewShip(self):
        """
        Creates a new ship with the same setting as in the beginning
        """
        self._ship = Ship(GAME_WIDTH/2,SHIP_BOTTOM+SHIP_HEIGHT/2,SHIP_WIDTH,
            SHIP_HEIGHT,'ship.png')

    def stopSound(self):
        """
        Mutes all the sounds created by ships, aliens, ship collision and
        alien collision
        """
        self._shipsound = None
        self._aliensound = None
        self._shipexplode = None
        self._alienexplode = None

    # DRAW METHOD TO DRAW THE SHIP, ALIENS, DEFENSIVE LINE AND BOLTS
    def drawAliens(self,view):
        """
        Draws the aliens to the view

        Parameter view: the game view, used in drawing
        Precondition: instance of GView [GView]
        """
        for row in self.getAliens():
            for alien in row:
                if not alien is None:
                    alien.draw(view)

    def drawShip(self,view):
        """
        Draws the ship to the view

        Parameter view: the game view, used in drawing
        Precondition: instance of GView [GView]
        """
        if not self.getShip() is None:
            self.getShip().draw(view)

    def drawBolts(self,view):
        """
        Draws the bolts to the view

        Parameter view: the game view, used in drawing
        Precondition: instance of GView [GView]
        """
        for bolt in self.getBolts():
            bolt.draw(view)

    # HELPER METHODS FOR COLLISION DETECTION
    def _shipCollision(self):
        """
        Determines if there is a collision between the bolt fired from the
        aliens and the ship; if so, sets self._ship to None and reduces
        self._lives by 1
        """
        for bolt in self._bolts:
            if self._ship.collides(bolt):
                self._ship = None
                if not self._shipexplode is None:
                    self._shipexplode.play()
                self._bolts.remove(bolt)
                self._lives -= 1
                return

    def _aliensCollision(self):
        """
        Determines if there is a collision between the bolt fired from the ship
        and the aliens; if so, removes the alien and changes self._alienspeed
        """
        for bolt in self._bolts:
            for row in range(ALIEN_ROWS):
                for col in range(ALIENS_IN_ROW):
                    if (not self.getAliens()[row][col] is None and
                        self.getAliens()[row][col].collides(bolt)):
                        self._score += 100*(ALIEN_ROWS-row)
                        self._aliens[row][col] = None
                        if not self._aliensound is None:
                            self._alienexplode.play()
                        self._bolts.remove(bolt)
                        self._alienspeed = self._alienspeed*0.98
                        return

    def _aliensList(self):
        """
        Returns: a 2D list of the aliens
        """
        result = []
        width = ALIEN_WIDTH
        height = ALIEN_HEIGHT
        for a in range(ALIEN_ROWS):
            result.insert(0,[])
            y = GAME_HEIGHT-ALIEN_CEILING-(ALIEN_ROWS-a-1)*(ALIEN_HEIGHT+
                ALIEN_V_SEP)-ALIEN_HEIGHT/2
            while a > len(ALIEN_IMAGES)*2-1:
                a -= len(ALIEN_IMAGES)*2
            if a/2 < 1:
                source = 'alien1.png'
            elif a/2 < 2:
                source = 'alien2.png'
            else:
                source = 'alien3.png'
            for b in range(ALIENS_IN_ROW):
                x = b*(ALIEN_H_SEP+ALIEN_WIDTH)+(ALIEN_H_SEP+ALIEN_WIDTH/2)
                result[0].append(Alien(x,y,width,height,source))
        return result

    def _determineBottomAlien(self):
        """
        Returns: the most bottom alien

        Method to determine the most bottom alien
        """
        for row in range(ALIEN_ROWS):
            for col in range(ALIENS_IN_ROW):
                if not self.getAliens()[ALIEN_ROWS-1-row][col] is None:
                    return self.getAliens()[ALIEN_ROWS-1-row][col]

    def _determineLeftAlien(self):
        """
        Returns: the most left alien

        Method to determine the most left alien
        """
        for col in range(ALIENS_IN_ROW):
            for row in range(ALIEN_ROWS):
                if not self.getAliens()[row][col] is None:
                    return self.getAliens()[row][col]

    def _determineRightAlien(self):
        """
        Returns: the most right alien

        Method to determine the most right alien
        """
        for col in range(ALIENS_IN_ROW):
            for row in range(ALIEN_ROWS):
                if not self.getAliens()[row][ALIENS_IN_ROW-1-col] is None:
                    return self.getAliens()[row][ALIENS_IN_ROW-1-col]

    def _handleEdge(self):
        """
        Moves the aliens down when it reaches the left or right ends
        """
        if self._aliensdown == False:
            for row in self.getAliens():
                for alien in row:
                    if not alien is None:
                        alien.y -= ALIEN_V_WALK
            self._direction = (-1)*self._direction
            self._aliensdown = True
        else:
            for row in self.getAliens():
                for alien in row:
                    if not alien is None:
                        alien.x += self._direction*ALIEN_H_WALK
            self._aliensdown = False

    def _aliensBolt(self):
        """
        Generates the bolt fired by the alien
        """
        k = ALIEN_ROWS-1
        if self._alienstep == self._boltstep:
            aliencol = random.randint(0,ALIENS_IN_ROW-1)
            checkII = False
            for row in range(ALIEN_ROWS):
                if not self._aliens[row][aliencol] is None:
                    checkII = checkII or True
            while not checkII:
                aliencol = random.randint(0,ALIENS_IN_ROW-1)
                for row in range(ALIEN_ROWS):
                    if not self._aliens[row][aliencol] is None:
                        checkII = checkII or True
            while self._aliens[k][aliencol] is None:
                k -= 1
            alienBolt = Bolt(self._aliens[k][aliencol].x,
                self._aliens[k][aliencol].y-ALIEN_HEIGHT/2,BOLT_WIDTH,
                BOLT_HEIGHT,'black',-BOLT_SPEED)
            self._bolts.append(alienBolt)
            if not self._aliensound is None:
                self._aliensound.play()
            self._boltstep = random.randint(1,BOLT_RATE)
            self._alienstep = 0

    def _shipBolt(self,input,check):
        """
        Generates the bolt fired by the ship

        Parameter input: the user input
        Precondition: instance of GInput [GInput]

        Parameter check: the boolean value of whether there is a bolt fired by
        the ship showed on the screen
        Precondition: boolean variable [bool]
        """
        if not check and not self._ship is None:
            current = input.is_key_down('spacebar')
            newBolt = Bolt(self._ship.x,SHIP_BOTTOM+SHIP_HEIGHT+BOLT_HEIGHT/2,
                BOLT_WIDTH,BOLT_HEIGHT,'black',BOLT_SPEED)
            if current and self._key == False:
                self._bolts.append(newBolt)
                if not self._shipsound is None:
                    self._shipsound.play()
            self._key = current
