#

import time

def _linear(start_val, end_val, duration, t):
    return (end_val-start_val)*t/duration + start_val

def _smooth(start_val, end_val, duration, t):
    return (end_val-start_val)*(3*(t/duration)**2-2*(t/duration)**3) + start_val

class ActionList():
    def __init__(self, play):
        self.play = play
        self.actions = []
        if len(self.play._actions) == 0:
            self.parent = None
        else:
            self.parent = self.play._actions[-1]
        self.done = False
        self.current_action = 0
    def add_action(self, action):
        self.actions.append(action)
    def __enter__(self):
        # make self the current action
        self.play._actions.append(self)
    def __exit__(self, type, value, tb):
        # append this parallel list of actions
        if not self.parent is None:
            self.parent.add_action(self.play._actions.pop())
    def process(self):
        raise NotImplemented()
    def __call__(self):
        self.done = False
        self.current_action = 0
        for i in range(len(self.actions)):
            self.actions[i].done = False
            self.actions[i].started = False
        self.play._do_action_list(self)
        self.started = True
        
class parallel(ActionList):
    def process(self):
        if not self.done:
            cur_time = time.time()
            # process the actions in parallel
            done = []
            for a in self.actions:
                if not a.started:
                    if isinstance(a, Action):
                        # do the action with start time
                        a(cur_time)
                    else:
                        # just call the untimed action
                        a()
                # see if we're done
                done.append(a.done)
            # we're only done when they all are
            self.done = all(done)

            # make sure to queue the drawing
            self.play.queue_draw()
        
class serial(ActionList):
    def process(self):
        # process the actions in serial
        if not self.done:
            # start that action if not done
            for i in range(self.current_action,len(self.actions)):
                a = self.actions[i]
                if not a.started:
                    if isinstance(a, Action):
                        # do the action with start time
                        a(time.time())
                    else:
                        # just call the untimed action
                        a()
                if not a.done:
                    # must break and come back
                    break
                
                # make sure to queue the drawing
                self.play.queue_draw()
            self.current_action = i
            
            if self.actions[-1].done:
                self.done = True
                
class Action(object):
    """
    Uses attributes until we have objects.
    """
    def __init__(self, play, actor, var,
                 start_val=None, end_val=None,
                 duration=0.0, func=_linear):
        self.play = play
        self.actor = actor
        self.var = var
        self.start_val = start_val
        self.end_val = end_val
        self.duration = duration
        self.func = func
        self.done = False
        self.started = False
    def set_var(self, cur_time):
        # calc the value based on the time
        t = cur_time - self.start_time
        if t > self.duration:
            #self.var = self.end_val
            setattr(self.actor,self.var,self.end_val)
            self.done = True
        else:
            # self.var = self.func(self.start_val,
            #                      self.end_val,
            #                      self.duration, t)
            setattr(self.actor,self.var,
                    self.func(self.start_val,
                              self.end_val,
                              self.duration, t))
            self.done = False

    def __call__(self, start_time):
        if self.start_val is None:
            # get it from the current var
            #start_val = var
            self.start_val = getattr(self.actor,self.var)
        self.done = False
        self.start_time = start_time
        self.play._do_action(self)
        self.started = True
        
class Enter():
    def __init__(self, play, *actors):
        self.play = play
        self.actors = actors
        self.done = False
        self.started = False
    def __call__(self):
        self.done = False
        self.play._do_enter(*(self.actors))
        self.started = True
        self.done = True

class Leave():
    def __init__(self, play, *actors):
        self.play = play
        self.actors = actors
        self.done = False
        self.started = False
    def __call__(self):
        self.done = False
        self.play._do_leave(*(self.actors))
        self.started = True
        self.done = True
    
class Pause():
    def __init__(self, play):
        self.play = play
        self.done = False
        self.started = False
    def __call__(self):
        self.done = False
        self.play._do_pause()
        self.started = True
        self.done = True

class Set():
    def __init__(self,play,actor,var,val):
        self.play = play
        self.actor = actor
        self.var = var
        self.val = val
    def __call__(self):
        self.done = False
        setattr(self.actor,self.var,self.val)
        self.started = True
        self.done = True
