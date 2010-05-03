#
#
from __future__ import with_statement

import gtk, gobject
import cairo
from gtk import gdk
from math import pi, sqrt
import time

from action import Action, Enter, Leave, Pause, _linear, _smooth


class parallel:
    def __init__(self, play):
        self.play = play
    def __enter__(self):
        self.start_val = self.play._in_parallel
        self.start_action = self.play._new_action
        self.play._new_action = []
        self.play._in_parallel = True
    def __exit__(self, type, value, tb):
        self.play._new_scene.append(self.play._new_action)
        self.play._new_action = self.start_action
        self.play._in_parallel = self.start_val

class serial:
    def __init__(self, play):
        self.play = play
    def __enter__(self):
        self.start_val = self.play._in_parallel
        self.start_action = self.play._new_action
        self.play._new_action = []
        self.play._in_parallel = False
    def __exit__(self, type, value, tb):
        self.play._new_action = self.start_action
        self.play._in_parallel = self.start_val

class Screen( gtk.DrawingArea ):
    """ This class is a Drawing Area"""
    def __init__( self, w, h ):
        # init the drawing area
        super( Screen, self ).__init__( )
        
        # Old fashioned way to connect 
        self.connect ( "expose_event", self.do_expose_event )
        
        # set the size
        self.width, self.height = w, h
        self.set_size_request ( w, h )


    ## When expose event fires, this is run
    def do_expose_event( self, widget, event ):
        self.cr = self.window.cairo_create( )
        ## Call our draw function to do stuff.
        self._draw( )

    def run(self):
        window = gtk.Window( )
        window.connect( "delete-event", gtk.main_quit )
        window.connect ( "key-press-event", self.on_key_press_event)
                
        self.show( )
        window.add( self )
        window.present( )
        gtk.main( )

    def on_key_press_event (self, widget, event):
        pass

class Play(Screen):
    def __init__ ( self, width, height, scenes=None, speed=20 ):
        self.width = width
        self.height = height
        Screen.__init__( self, width, height )

        if scenes is None:
            scenes = []
        self._scenes = scenes
        self._current_scene = 0

        self._actors = []
        self._active_actors = []

        self._action_speed = speed

        self._paused = False

        self._show_started = False

    def _show(self, start_scene=None):
        if not start_scene is None:
            self._current_scene = start_scene

        if self._current_scene < 0:
            self._current_scene = 0
            
        # call the current scene
        if self._current_scene < len(self._scenes):
            self._show_scenes(self._current_scene)
        self._current_scene += 1

        # recursive
        #self._show()

    def _show_scenes(self,s):
        for s in range(s,len(self._scenes)):
            for a in self._scenes[s]:
                for i in range(len(a)):
                    actions = []
                    if isinstance(a[i],Action):
                        # loop over each one and do it in parallel
                        actions.append(a[i])
                    else:
                        # call it
                        a[i]()
                if len(actions) > 0:
                    self._do_actions(actions)
                self.queue_draw()
                
    def on_key_press_event (self, widget, event):
        keyname = gtk.gdk.keyval_name(event.keyval)
        print event.hardware_keycode, event.keyval, keyname
        if event.hardware_keycode == 9:
            gtk.main_quit ()
        elif event.hardware_keycode in [65,36,114,116]:
            if self._paused:
                # unpause if paused
                self._paused = False
            elif self._show_started == False:
                self._show_started = True
                self._show()
        elif event.hardware_keycode in [111,113]:
            # go back to previous slide
            # HOW?
            self._current_scene -= 1
            pass
        
    def _draw( self ):
        # draw the background
        cr = self.cr
        
        cr.scale(self.width, self.height)
        cr.rectangle(0, 0, 1, 1)
        cr.set_source_rgb(0, 1, 1)
        cr.fill()

        for a in self._actors:
            if a in self._active_actors:
                # pass in the time of current time, too
                a._draw(cr, t=self._current_time)
            else:
                # just draw it
                a._draw(cr)
            
    def _process_events(self):
        while gtk.events_pending():
            gtk.main_iteration(False)

    def add_scene(self, scene):
        self._new_scene = []
        self._new_action = []
        self._in_parallel = False
        scene(self)
        self._scenes.append(self._new_scene)

    def enter(self, *actors):
        self._new_action.append(Enter(self,*actors))
        if not self._in_parallel:
            self._new_scene.append(self._new_action)
            self._new_action = []
        
    def _do_enter(self, *actors):
        """
        """
        self._actors.extend(actors)
        # make sure to redraw
        #self.queue_draw()

    def leave(self, *actors):
        self._new_action.append(Leave(self,*actors))
        if not self._in_parallel:
            self._new_scene.append(self._new_action)
            self._new_action = []

    def _do_leave(self, *actors):
        if len(actors) == 0:
            # remove them all
            self._actors = []
        else:
            for a in actors:
                if a in self._actors:
                    self._actors.remove(a)
        # make sure to redraw
        #self.queue_draw()

    def smooth(self, actor, var,
               start_val=None, end_val=None,
               duration=1.0):
        self._new_action.append(Action(self,actor,var,
                                       start_val=start_val,
                                       end_val=end_val,
                                       duration=duration,
                                       func=_smooth))
        if not self._in_parallel:
            self._new_scene.append(self._new_action)
            self._new_action = []

    def linear(self, actor, var,
               start_val=None, end_val=None,
               duration=1.0):
        self._new_action.append(Action(self,actor,var,
                                       start_val=start_val,
                                       end_val=end_val,
                                       duration=duration,
                                       func=_linear))
        if not self._in_parallel:
            self._new_scene.append(self._new_action)
            self._new_action = []

    def fadein(self, actor, duration=1.0):
        actor.opacity=0.0
        self.enter(actor)
        self.linear(actor, "opacity", end_val=1.0,
                    duration=duration)

    def fadeout(self, actor, duration=1.0):
        self.linear(actor, "opacity", end_val=0.0,
                    duration=duration)
        self.leave(actor)

    def _do_actions(self, actions):
        # Go call tick every X ms.
        self._action_timer_running = True
        print actions
        gobject.timeout_add( self._action_speed,
                             self._tick,
                             actions,
                             time.time())
        while self._action_timer_running:
            self._process_events()
            time.sleep(.01)

    def _tick ( self, actions, start_time ):
        """This invalidates the screen, causing the expose event to fire."""
        t = time.time() - start_time
        done = []
        for action in actions:
            done.append(action.set_var(t))
        done = all(done)
        self.queue_draw()
        if done:
            self._action_timer_running = False
        return not done # Causes timeout to tick again.
        
    def wait(self):
        pass
    
    def pause(self):
        self._new_action.append(Pause(self))
        if not self._in_parallel:
            self._new_scene.append(self._new_action)
            self._new_action = []
        
    def _do_pause(self):
        # we're paused
        self._paused = True
        while self._paused:
            self._process_events()
            time.sleep(.01)
        #raw_input()


if __name__ == "__main__":
    myplay = Play( 800, 600 )

    from actor import TextBox
    def scene1(p):
        x = TextBox("Pynamite")
        y = TextBox("Rocks!!!")
        p.enter(x)
        p.pause()
        with parallel(p):
            p.fadein(y)
            p.fadeout(x)
        p.pause()
    myplay.add_scene(scene1)

    def scene2(p):
        x = TextBox("Rocks!!!")
        p.fadein(x)
        p.pause()
        p.leave()
    myplay.add_scene(scene2)

    #myplay.run()


