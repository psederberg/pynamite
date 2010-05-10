#
from __future__ import with_statement

import time

from play import global_play

# interpolation functions
def _linear(start_val, end_val, duration, t):
    return (end_val-start_val)*t/duration + start_val

def _smooth(start_val, end_val, duration, t):
    return (end_val-start_val)*(3*(t/duration)**2-2*(t/duration)**3) + start_val

_interp_func = {"linear": _linear,
                "smooth": _smooth}

class Action(object):
    """
    """
    play = global_play
    done = False
    start_time = None
    
    def _process(self, cur_time):
        raise NotImplemented()
        
    def __call__(self, cur_time):
        if not self.start_time is None:
            # just eval the desired function
            if not self.done:
                self._process(cur_time)
        else:
            # initialize the processing
            self.done = False
            self.start_time = cur_time
            self._process(cur_time)
            if not self.done:
                # add it to the active actions until done
                self.play._active_actions.append(self)
            else:
                # it's done, so ensure drawing
                self.play.queue_draw()

class Set(Action):
    def __init__(self,actor,var,val,duration=0.0,func="linear"):
        self.actor = actor
        self.var = var
        self.end_val = val
        self.duration = duration
        self.func = _interp_func[func]
    def _process(self, cur_time):
        # calc the value based on the time
        t = cur_time - self.start_time
        if t >= self.duration:
            #self.var = self.end_val
            setattr(self.actor,self.var,self.end_val)
            self.done = True
        else:
            if t==0.0:
                self.start_val = getattr(self.actor,self.var)
            # eventually use this
            # self.var = self.func(self.start_val,
            #                      self.end_val,
            #                      self.duration, t)
            setattr(self.actor,self.var,
                    self.func(self.start_val,
                              self.end_val,
                              self.duration, t))
            #self.done = False

def linear(actor, var, val, duration=1.0):
    global_play.add_action(Set(actor,var,val,
                               duration=duration,
                               func="linear"))
def smooth(actor, var, val, duration=1.0):
    global_play.add_action(Set(actor,var,val,
                               duration=duration,
                               func="smooth"))

# classes for property setting
class set_to(object):
    def __init__(self, val, duration=1.0, func="linear"):
        self.val = val
        self.duration = duration
        self.func = func
class smooth_to(set_to):
    def __init__(self, val, duration=1.0):
        self.val = val
        self.duration = duration
        self.func = "smooth"
class linear_to(set_to):
    def __init__(self, val, duration=1.0):
        self.val = val
        self.duration = duration
        self.func = "linear"

class ActionList(Action):
    def __init__(self):
        self.actions = []
        if len(self.play._actions) == 0:
            self.parent = None
        else:
            self.parent = self.play._actions[-1]
        self.current_action = 0
    def add_action(self, action):
        self.actions.append(action)
    def __enter__(self):
        # make self the current action
        self.play._actions.append(self)
    def __exit__(self, type, value, tb):
        # append this list of actions
        if not self.parent is None:
            self.parent.add_action(self.play._actions.pop())

class parallel(ActionList):
    def _process(self, cur_time):
        # process the actions in parallel
        done = []
        for a in self.actions:
            if a.start_time is None:
                # start it all at same passed in time
                a(cur_time)
            # see if we're done
            done.append(a.done)
        # we're only done when they all are
        self.done = all(done)

        # make sure to queue the drawing
        #self.play.queue_draw()

class serial(ActionList):
    def _process(self, cur_time):
        # start that action if not done
        for i in range(self.current_action,len(self.actions)):
            a = self.actions[i]
            if a.start_time is None:
                # start it (ignore time passed in)
                a(time.time())
            if not a.done:
                # must break and come back
                break

            # make sure to queue the drawing
            #self.play.queue_draw()
            
        # update the current action
        self.current_action = i

        # update when we are done
        if self.actions[-1].done:
            self.done = True

class Enter(Action):
    def __init__(self, *actors):
        self.actors = actors
    def _process(self, cur_time):
        self.play.enter(*(self.actors))
        self.done = True
def enter(*actors):
    global_play.add_action(Enter(*actors))
    
class Leave(Action):
    def __init__(self, *actors):
        self.actors = actors
    def _process(self, cur_time):
        self.play.leave(*(self.actors))
        self.done = True
def leave(*actors):
    global_play.add_action(Leave(*actors))

class Pause(Action):
    def _process(self, cur_time):
        self.play.pause()
        self.done = True
def pause():
    global_play.add_action(Pause())


def fadein(duration, *actors):
    with serial():
        for actor in actors:
            #actor.set_opacity(0.0)
            actor.opacity = 0.0
        enter(*actors)
        with parallel():
            for actor in actors:
                #actor.set_opacity(1.0, duration=duration, func="linear")
                actor.opacity = linear_to(1.0, duration=duration)


def fadeout(duration, *actors):
    with serial():
        with parallel():
            for actor in actors:
                #actor.set_opacity(0.0, duration=duration, func="linear")
                actor.opacity = linear_to(0.0, duration=duration)
        leave(*actors)

def add_scene(scene):
    global_play._actions = []
    with serial():
        scene()
    global_play.add_scene()

