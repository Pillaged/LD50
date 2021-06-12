from collections import defaultdict
from enum import Enum

import pygame as pg


class Button(Enum):
    HEAD = 0
    LEFT_FOOT = 1
    RIGHT_FOOT = 2
    LEFT_HAND = 3
    RIGHT_HAND = 4
    ALL_BODY = 5
    UP = 6
    RIGHT = 7
    LEFT = 8
    DOWN = 9
    INTERACT = 10
    ESCAPE = 11
    RESET = 12
    UNICODE = 1000
    QUIT = 1001
    MOUSE_LEFT = 32768


class PygameEventQueueHandler:
    """ Handle all events from the pygame event queue
    """

    def __init__(self):
        self._inputs = defaultdict(list)  # type Dict[int, List[InputHandler]]
        self._inputs[0].append(PygameKeyboardInput())
        self._inputs[0].append(PygameMouseInput())
        self._inputs[0].append(QuitInput())

    def process_events(self):
        """ Process all pygame events
        * Should never return pygame-unique events
        * All events returned should be game specific
        * This must be the only function to get events from the pygame event queue
        :returns: Iterator of game events
        """
        for pg_event in pg.event.get():
            for player, inputs in self._inputs.items():
                for player_input in inputs:
                    player_input.process_event(pg_event)

        for player, inputs in self._inputs.items():
            for player_input in inputs:
                yield from player_input.get_events()


class InputHandler:
    """ Enables basic input device with discrete inputs
    """
    event_type = None
    default_input_map = None

    def __init__(self, event_map=None):
        if event_map is None:
            assert self.default_input_map
            event_map = self.default_input_map.copy()
        self.buttons = dict()
        self.event_map = event_map
        for button in event_map.values():
            self.buttons[button] = PlayerInput(button)

    def process_event(self, pg_event):
        raise NotImplementedError

    def virtual_stop_events(self):
        """ Send virtual input events simulating released buttons/axis

        This is used to force a state to release inputs without changing input state

        :return:
        """
        for button, inp in self.buttons.items():
            if inp.held:
                yield PlayerInput(inp.button, 0, 0)

    def get_events(self):
        for inp in self.buttons.values():
            if inp.held:
                yield inp
                inp.hold_time += 1
            elif inp.triggered:
                yield inp
                inp.triggered = False

    def press(self, button, value=1):
        inp = self.buttons[button]
        inp.value = value
        if not inp.hold_time:
            inp.hold_time = 1

    def release(self, button):
        inp = self.buttons[button]
        inp.value = 0
        inp.hold_time = 0
        inp.triggered = True


class PlayerInput:
    __slots__ = ("button", "value", "hold_time", "triggered")

    def __init__(self, button, value=0, hold_time=0):
        """ Represents a single player input

        Each instance represents the state of a single input:
        * have float value 0-1
        * are "pressed" when value is above 0, for exactly one frame
        * are "held" when "pressed" for longer than zero frames

        Do not manipulate these values
        Once created, these objects will not be destroyed
        Input managers will set values on these objects
        These objects are reused between frames, do not hold references to them

        :type button: int
        :type value: float
        :type hold_time: int
        """
        self.button = button
        self.value = value
        self.hold_time = hold_time
        self.triggered = False

    def __str__(self):
        return "<PlayerInput: {} {} {} {} {}>".format(self.button, self.value, self.pressed, self.held, self.hold_time)

    @property
    def pressed(self):
        """ This is edge triggered, meaning it will only be true once!

        :rtype: bool
        """
        return bool(self.value) and self.hold_time == 1

    @property
    def held(self):
        """ This will be true as long as button is held down

        :rtype: bool
        """
        return bool(self.value)


class PygameEventHandler(InputHandler):
    def process_event(self, pg_event):
        """
        :rtype:  bool
        """
        return False


class PygameKeyboardInput(PygameEventHandler):
    default_input_map = {
        pg.K_UP: Button.UP,
        pg.K_DOWN: Button.DOWN,
        pg.K_LEFT: Button.LEFT,
        pg.K_RIGHT: Button.RIGHT,
        pg.K_w: Button.HEAD,
        pg.K_x: Button.RIGHT_FOOT,
        pg.K_a: Button.LEFT_HAND,
        pg.K_d: Button.RIGHT_HAND,
        pg.K_z: Button.LEFT_FOOT,
        pg.K_s: Button.ALL_BODY,
        pg.K_r: Button.RESET,
        pg.K_ESCAPE: Button.ESCAPE,
        None: Button.UNICODE,
    }

    def process_event(self, pg_event):
        """ Translate a pg event to an internal game event
        :type pg_event: pg.event.Event
        """
        pressed = pg_event.type == pg.KEYDOWN
        released = pg_event.type == pg.KEYUP

        if pressed or released:
            # try to get game-specific action for the key
            try:
                button = self.event_map[pg_event.key]
                if pressed:
                    self.press(button)
                else:
                    self.release(button)
            except KeyError:
                pass
            # just get unicode value
            try:
                if pressed:
                    self.release(Button.UNICODE)
                    self.press(Button.UNICODE, pg_event.unicode)
                else:
                    self.release(Button.UNICODE)
            except AttributeError:
                pass


class PygameMouseInput(PygameEventHandler):
    default_input_map = {
        pg.MOUSEBUTTONDOWN: Button.MOUSE_LEFT,
        pg.MOUSEBUTTONUP: Button.MOUSE_LEFT,
    }

    def process_event(self, pg_event):
        if pg_event.type == pg.MOUSEBUTTONDOWN:
            self.press(Button.MOUSE_LEFT, pg_event.pos)
        elif pg_event.type == pg.MOUSEBUTTONUP:
            self.release(Button.MOUSE_LEFT)


class QuitInput(PygameEventHandler):
    default_input_map = {
        pg.QUIT: Button.QUIT,
    }

    def process_event(self, pg_event):
        if pg_event.type == pg.QUIT:
            self.press(Button.QUIT)
