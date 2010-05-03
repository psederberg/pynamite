


def _linear(start_val, end_val, duration, t):
    return (end_val-start_val)*t/duration + start_val

def _smooth(start_val, end_val, duration, t):
    return (end_val-start_val)*(3*(t/duration)**2-2*(t/duration)**3) + start_val

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
        if start_val is None:
            # get it from the current var
            #start_val = var
            start_val = getattr(actor,var)
        self.start_val = start_val
        self.end_val = end_val
        self.duration = duration
        self.func = func
    def set_var(self, t):
        # calc the value based on the time
        if t > self.duration:
            #self.var = self.end_val
            setattr(self.actor,self.var,self.end_val)
            return True
        else:
            # self.var = self.func(self.start_val,
            #                      self.end_val,
            #                      self.duration, t)
            setattr(self.actor,self.var,
                    self.func(self.start_val,
                              self.end_val,
                              self.duration, t))
            return False
    def __call__(self):
        self.play._do_action(self)
        
class Enter():
    def __init__(self, play, *actors):
        self.play = play
        self.actors = actors
    def __call__(self):
        self.play._do_enter(*(self.actors))
        return False

class Leave():
    def __init__(self, play, *actors):
        self.play = play
        self.actors = actors
    def __call__(self):
        self.play._do_leave(*(self.actors))
        return False
    
class Pause():
    def __init__(self, play):
        self.play = play
    def __call__(self):
        self.play._do_pause()
        return False
