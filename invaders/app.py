"""
Primary module for Alien Invaders

This module contains the main controller class for the Alien Invaders application. There
is no need for any additional classes in this module.  If you need more classes, 99% of
the time they belong in either the wave module or the models module. If you are unsure
about where a new class should go, post a question on Piazza.

Name: Yiheng Dong yd83, Zeyi Qiu zq35
Date: November 30, 2018
"""
from consts import *
from game2d import *
from wave import *


# PRIMARY RULE: Invaders can only access attributes in wave.py via getters/setters
# Invaders is NOT allowed to access anything in models.py

class Invaders(GameApp):
    """
    The primary controller class for the Alien Invaders application

    This class extends GameApp and implements the various methods necessary for processing
    the player inputs and starting/running a game.

        Method start begins the application.

        Method update either changes the state or updates the Play object

        Method draw displays the Play object and any other elements on screen

    Because of some of the weird ways that Kivy works, you SHOULD NOT create an
    initializer __init__ for this class.  Any initialization should be done in
    the start method instead.  This is only for this class.  All other classes
    behave normally.

    Most of the work handling the game is actually provided in the class Wave.
    Wave should be modeled after subcontrollers.py from lecture, and will have
    its own update and draw method.

    The primary purpose of this class is to manage the game state: which is when the
    game started, paused, completed, etc. It keeps track of that in an attribute
    called _state.

    INSTANCE ATTRIBUTES:
        view:   the game view, used in drawing (see examples from class)
                [instance of GView; it is inherited from GameApp]
        input:  the user input, used to control the ship and change state
                [instance of GInput; it is inherited from GameApp]
        _state: the current state of the game represented as a value from consts.py
                [one of STATE_INACTIVE, STATE_NEWWAVE, STATE_ACTIVE, STATE_PAUSED, STATE_CONTINUE, STATE_COMPLETE]
        _wave:  the subcontroller for a single wave, which manages the ships and aliens
                [Wave, or None if there is no wave currently active]
        _text:  the currently active message
                [GLabel, or None if there is no message to display]

    STATE SPECIFIC INVARIANTS:
        Attribute _wave is only None if _state is STATE_INACTIVE.
        Attribute _text is only None if _state is STATE_ACTIVE.

    For a complete description of how the states work, see the specification for the
    method update.

    You may have more attributes if you wish (you might want an attribute to store
    any score across multiple waves). If you add new attributes, they need to be
    documented here.

    LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
        _key: whether 'S' key has been pressed or not [bool]
        _soundmessage: message giving instruction on how to control sound [GLabel]
        _keySound: whether 'Q' key has been pressed or not [bool]
        _scoremessage: message displaying the score the player has got [GLabel]
    """

    # DO NOT MAKE A NEW INITIALIZER!

    # THREE MAIN GAMEAPP METHODS
    def start(self):
        """
        Initializes the application.

        This method is distinct from the built-in initializer __init__ (which you
        should not override or change). This method is called once the game is running.
        You should use it to initialize any game specific attributes.

        This method should make sure that all of the attributes satisfy the given
        invariants. When done, it sets the _state to STATE_INACTIVE and create a message
        (in attribute _text) saying that the user should press to play a game.
        """
        self._state = STATE_INACTIVE
        self._wave = None
        welcome = GLabel(x=GAME_WIDTH/2,y=GAME_HEIGHT/2,
            text="Press 'S' to Play",font_size=50,font_name='RetroGame')
        self._text = welcome
        sound = GLabel(x=GAME_WIDTH/4,y=GAME_HEIGHT-ALIEN_CEILING/2,
            text="Press 'Q' to Turn Off the Sound",font_size=15,
            font_name='RetroGame')
        self._soundmessage = sound
        score = GLabel(x=GAME_WIDTH*5/6,y=GAME_HEIGHT-ALIEN_CEILING/2,
            text='Score: ',font_size=15,font_name='RetroGame')
        self._scoremessage = score
        self._key = False
        self._keySound = False

    def update(self,dt):
        """
        Animates a single frame in the game.

        It is the method that does most of the work. It is NOT in charge of playing the
        game.  That is the purpose of the class Wave. The primary purpose of this
        game is to determine the current state, and -- if the game is active -- pass
        the input to the Wave object _wave to play the game.

        As part of the assignment, you are allowed to add your own states. However, at
        a minimum you must support the following states: STATE_INACTIVE, STATE_NEWWAVE,
        STATE_ACTIVE, STATE_PAUSED, STATE_CONTINUE, and STATE_COMPLETE.  Each one of these
        does its own thing and might even needs its own helper.  We describe these below.

        STATE_INACTIVE: This is the state when the application first opens.  It is a
        paused state, waiting for the player to start the game.  It displays a simple
        message on the screen. The application remains in this state so long as the
        player never presses a key.  In addition, this is the state the application
        returns to when the game is over (all lives are lost or all aliens are dead).

        STATE_NEWWAVE: This is the state creates a new wave and shows it on the screen.
        The application switches to this state if the state was STATE_INACTIVE in the
        previous frame, and the player pressed a key. This state only lasts one animation
        frame before switching to STATE_ACTIVE.

        STATE_ACTIVE: This is a session of normal gameplay.  The player can move the
        ship and fire laser bolts.  All of this should be handled inside of class Wave
        (NOT in this class).  Hence the Wave class should have an update() method, just
        like the subcontroller example in lecture.

        STATE_PAUSED: Like STATE_INACTIVE, this is a paused state. However, the game is
        still visible on the screen.

        STATE_CONTINUE: This state restores the ship after it was destroyed. The
        application switches to this state if the state was STATE_PAUSED in the
        previous frame, and the player pressed a key. This state only lasts one animation
        frame before switching to STATE_ACTIVE.

        STATE_COMPLETE: The wave is over, and is either won or lost.

        You are allowed to add more states if you wish. Should you do so, you should
        describe them here.

        Parameter dt: The time in seconds since last update
        Precondition: dt is a number (int or float)
        """
        self._determineState()
        if self._state == STATE_NEWWAVE:
            self._wave = Wave()
            self._state = STATE_ACTIVE
            self._text = None
        elif self._state == STATE_ACTIVE:
            self._determineSound()
            self._wave.updateBolts(self.input)
            self._wave.updateShip(self.input)
            self._wave.updateAliens(dt)
            self._determineWinOrLose()
            self._scoremessage.text = 'Score: '+str(self._wave.getScore())
        elif self._state == STATE_PAUSED:
            message = GLabel(x=GAME_WIDTH/2,y=GAME_HEIGHT/2,
                text="Press 'S' to Continue",font_size=50,font_name='RetroGame')
            self._text = message
        elif self._state == STATE_CONTINUE:
            self._wave.setNewShip()
            self._state = STATE_ACTIVE
            self._text = None

    def draw(self):
        """
        Draws the game objects to the view.

        Every single thing you want to draw in this game is a GObject.  To draw a GObject
        g, simply use the method g.draw(self.view).  It is that easy!

        Many of the GObjects (such as the ships, aliens, and bolts) are attributes in
        Wave. In order to draw them, you either need to add getters for these attributes
        or you need to add a draw method to class Wave.  We suggest the latter.  See
        the example subcontroller.py from class.
        """
        if not (self._state == STATE_INACTIVE or self._state == STATE_COMPLETE):
            self._wave.drawAliens(self.view)
            self._wave.drawShip(self.view)
            line = GPath(points=[0,DEFENSE_LINE,GAME_WIDTH,DEFENSE_LINE],
                linewidth=1,linecolor='black')
            line.draw(self.view)
            self._wave.drawBolts(self.view)
            self._soundmessage.draw(self.view)
            self._scoremessage.draw(self.view)
        if not self._text is None:
            self._text.draw(self.view)

    # HELPER METHODS FOR THE STATES GO HERE
    def _determineState(self):
        """
        Determines the current state and assigns it to self._state

        This method checks for a 's' key press, and if there is one, changes the
        state to the next value.
        """
        current = self.input.is_key_down('s')
        check = current and self._key == False
        if check:
            if self._state == STATE_INACTIVE:
                self._state = STATE_NEWWAVE
            elif self._state == STATE_PAUSED:
                self._state = STATE_CONTINUE
            elif self._state == STATE_COMPLETE:
                self.start()
        self._key = current

    def _determineSound(self):
        """
        Determines whether the sound should be turned on or turned off and the
        text showed in self._soundmessage.

        This method checks for a 'q' key press, and if there is one, change the
        state of sounds.

        If the sound is on, shows the message "Press 'Q' to Turn Off the Sound"
        on the left top corner of the screen,
        If the sound is off, shows the message "Press 'Q' to Turn On the Sound"
        on the left top corner of the screen.
        """
        current = self.input.is_key_down('q')
        check = current and self._keySound == False
        if check:
            if self._wave.getSound() is None:
                self._wave.setSound()
                self._soundmessage = GLabel(x=GAME_WIDTH/4,
                    y=GAME_HEIGHT-ALIEN_CEILING/2,
                    text="Press 'Q' to Turn Off the Sound",font_size=15,
                    font_name='RetroGame')
            else:
                self._wave.stopSound()
                self._soundmessage = GLabel(x=GAME_WIDTH/4,
                    y=GAME_HEIGHT-ALIEN_CEILING/2,
                    text="Press 'Q' to Turn On the Sound",font_size=15,
                    font_name='RetroGame')
        self._keySound = current

    def _determineWinOrLose(self):
        """
        Determines whether the player wins or loses the game

        If the player is winning, turns into STATE_COMPLETE and shows the
        message "Congratulations!\nPress'S'" on the screen.
        If the player still have lives left, turns into STATE_PAUSED.
        If the player is losing, turns into STATE_COMPLETE and shows the message
        "You Lose\nPress 'S'" on the screen.
        """
        if self._wave.isWinning():
            self._state = STATE_COMPLETE
            message = GLabel(x=GAME_WIDTH/2,y=GAME_HEIGHT/2,
                text="Congratulations!\nPress 'S'",font_size=50,
                font_name='RetroGame')
            self._text = message
        elif self._wave.getShip() is None and self._wave.getLives() > 0:
            self._state = STATE_PAUSED
        elif ((self._wave.getShip() is None and
            self._wave.getLives() <= 0) or self._wave.isLosing()):
            self._state = STATE_COMPLETE
            message = GLabel(x=GAME_WIDTH/2,y=GAME_HEIGHT/2,
                text="You Lose\nPress 'S'",font_size=50,font_name='RetroGame')
            self._text = message
