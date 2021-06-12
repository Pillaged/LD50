import inspect
import logging
import os
import sys
from importlib import import_module

import pygame

import prepare

logger = logging.getLogger(__name__)


class State:
    rect = pygame.Rect((0, 0), prepare.SCREEN_SIZE)
    transparent = False  # ignore all background/borders
    force_draw = False  # draw even if completely under another state

    def __init__(self, client):
        """ Do not override this unless there is a special need.

        All init for the State, loading of config, images, etc should
        be done in State.startup or State.resume, not here.

        :returns: None
        """
        self.client = client
        self.start_time = 0.0
        self.current_time = 0.0
        self.animations = pygame.sprite.Group()  # only animations and tasks
        self.sprites = pygame.sprite.Group()  # all sprites that draw on the screen

    @property
    def name(self):
        return self.__class__.__name__

    def update(self, time_delta):
        self.animations.update(time_delta)

    def draw(self, surface):
        pass

    def startup(self, **kwargs):
        pass

    def resume(self):
        pass

    def pause(self):
        pass

    def cleanup(self):
        pass

class StateManager:

    def __init__(self):
        self.done = False
        self.current_time = 0.0
        self.package = ""
        self._state_queue = list()
        self._state_stack = list()
        self._state_dict = dict()
        self._state_resume_set = set()
        self._remove_queue = list()

    def auto_state_discovery(self):
        """ Scan a folder, load states found in it, and register them
        """
        state_folder = os.path.join(prepare.LIBDIR, *self.package.split(".")[0:])
        exclude_endings = (".py", ".pyc", ".pyo", "__pycache__")
        logger.debug("loading game states from {}".format(state_folder))
        for folder in os.listdir(state_folder):
            if any(folder.endswith(end) for end in exclude_endings):
                continue
            for state in self.collect_states_from_path(folder):
                self.register_state(state)

    def register_state(self, state):
        name = state.__name__
        logger.debug("loading state: {}".format(state.__name__))
        self._state_dict[name] = state

    @staticmethod
    def collect_states_from_module(import_name):
        """ Given a module, return all classes in it that are a game state
        """
        classes = inspect.getmembers(sys.modules[import_name], inspect.isclass)

        for c in (i[1] for i in classes):
            if issubclass(c, State):
                yield c

    def collect_states_from_path(self, folder):
        """ Load a state from disk, but do not register it
        """
        try:
            import_name = self.package + '.' + folder
            import_module(import_name)
            yield from self.collect_states_from_module(import_name)
        except Exception as e:
            template = "{} failed to load or is not a valid game package"
            logger.error(e)
            logger.error(template.format(folder))
            raise

    def query_all_states(self):
        """ Return a dictionary of all loaded states

        Keys are state names, values are State classes

        :returns: dictionary of all loaded states
        :rtype: Dict
        """
        return self._state_dict.copy()

    def queue_state(self, state, **kwargs):
        """ Queue a state to be pushed after the top state is popped or replaced

        Use this to chain execution of states, without causing a
        state to get instanced before it is on top of the stack.

        :param state:
        :returns:
        """
        self._state_queue.append((state, kwargs))

    def pop_state(self, state=None):
        """ Pop some state.  Default is the current one.  The previously running state will resume.

        If there is a queued state, then that state will be resumed, not the previous!
        Game loop will end if the last state is popped.

        :param state: The state to remove from stack.  Use None (or omit) for current state.
        :returns: None
        """
        # handle situation where there is a queued state
        if self._state_queue:
            state, kwargs = self._state_queue.pop(0)
            self.replace_state(state, **kwargs)
            return

        # no queued state, so proceed as normal
        if state is None:
            index = 0
        elif state in self._state_stack:
            index = self._state_stack.index(state)
        else:
            logger.critical("Attempted to pop state when state was not active.")
            raise RuntimeError

        try:
            previous = self._state_stack.pop(index)
        except IndexError:
            logger.critical("Attempted to pop state when no state was active.")
            raise RuntimeError

        previous.pause()
        previous.cleanup()

        if index == 0 and self._state_stack:
            self.current_state.resume()
        elif index and self._state_stack:
            pass
        else:
            self.done = True

    def push_state(self, state_name, **kwargs):
        """ Pause currently running state and start new one.

        :param state_name: name of state to start
        :returns: instanced State
        """
        try:
            state = self._state_dict[state_name]
        except KeyError:
            logger.critical('Cannot find state: {}'.format(state_name))
            raise RuntimeError

        previous = self.current_state
        logger.debug("resetting controls due to state change")
        self.release_controls()

        if previous is not None:
            previous.pause()

        instance = state(self)
        self._state_stack.insert(0, instance)

        instance.controller = self
        instance.startup(**kwargs)
        self._state_resume_set.add(instance)

        return instance

    def replace_state(self, state_name, **kwargs):
        """ Replace the currently running state with a new one

        This is essentially, just a push_state, followed by pop_state(running_state).
        This cannot be used to replace states in the middle of the stack.

        :param state_name: name of state to start
        :returns: New instance
        """
        previous = self._state_stack[0]
        instance = self.push_state(state_name, **kwargs)
        self.pop_state(previous)
        return instance

    @property
    def state_name(self):
        """ Name of state currently running
        :returns: string
        :rtype: String
        """
        return self._state_stack[0].name

    @property
    def current_state(self):
        """ The currently running state

        :returns: State
        """
        try:
            return self._state_stack[0]
        except IndexError:
            return None

    @property
    def active_states(self):
        """ Return list of states that are active

        :returns: List of states currently active
        :rtype: List
        """
        return self._state_stack[:]
