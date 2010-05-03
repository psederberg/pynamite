#
#
from __future__ import with_statement

import gtk, gobject
import cairo
from gtk import gdk
from math import pi, sqrt
import time

from action import Action, Enter, Leave, Pause, Set
from action import ActionList, parallel, serial
from action import _linear, _smooth


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
        self._active_actions = []
        self._active_action_lists = []

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
            print "Scene %d" % s
            self._scenes[s]()
            while not self._scenes[s].done:
                self._process_events()
                
            # for a in self._scenes[s]:
            #     for i in range(len(a)):
            #         actions = []
            #         if isinstance(a[i],Action):
            #             # loop over each one and do it in parallel
            #             actions.append(a[i])
            #         else:
            #             # call it
            #             a[i]()
            #     if len(actions) > 0:
            #         self._do_actions(actions)
            #     self.queue_draw()
                
    def on_key_press_event (self, widget, event):
        keyname = gtk.gdk.keyval_name(event.keyval)
        print event.hardware_keycode, event.keyval, keyname
        if event.hardware_keycode == 9:
            gtk.main_quit ()
        elif event.hardware_keycode in [65,114,116]:
            if self._paused:
                # unpause if paused
                self._paused = False
            elif self._show_started == False:
                self._show_started = True
                self._show()
        elif event.hardware_keycode in [36]:
            print self._active_action_lists
            print self._active_actions
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
            # just draw it
            a._draw(cr)
            
    def _process_events(self, sleep=0.01):
        while gtk.events_pending():
            gtk.main_iteration(False)
        time.sleep(sleep)

    def add_scene(self, scene):
        self._actions = []
        with serial(self):
            scene(self)
        self._scenes.append(self._actions.pop())

    def enter(self, *actors):
        self._actions[-1].add_action(Enter(self,*actors))
        # self._new_action.append(Enter(self,*actors))
        # if not self._in_parallel:
        #     self._new_scene.append(self._new_action)
        #     self._new_action = []
        
    def _do_enter(self, *actors):
        """
        """
        self._actors.extend(actors)
        # make sure to redraw
        #self.queue_draw()

    def leave(self, *actors):
        self._actions[-1].add_action(Leave(self,*actors))
        # self._new_action.append(Leave(self,*actors))
        # if not self._in_parallel:
        #     self._new_scene.append(self._new_action)
        #     self._new_action = []

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

    def set_var(self, actor, var, val):
        self._actions[-1].add_action(Set(self,actor,
                                         var, val))
        

    def smooth(self, actor, var,
               start_val=None, end_val=None,
               duration=1.0):
        self._actions[-1].add_action(Action(self,actor,var,
                                            start_val=start_val,
                                            end_val=end_val,
                                            duration=duration,
                                            func=_smooth))
        # self._new_action.append(Action(self,actor,var,
        #                                start_val=start_val,
        #                                end_val=end_val,
        #                                duration=duration,
        #                                func=_smooth))
        # if not self._in_parallel:
        #     self._new_scene.append(self._new_action)
        #     self._new_action = []

    def linear(self, actor, var,
               start_val=None, end_val=None,
               duration=1.0):
        self._actions[-1].add_action(Action(self,actor,var,
                                            start_val=start_val,
                                            end_val=end_val,
                                            duration=duration,
                                            func=_linear))
        # self._new_action.append(Action(self,actor,var,
        #                                start_val=start_val,
        #                                end_val=end_val,
        #                                duration=duration,
        #                                func=_linear))
        # if not self._in_parallel:
        #     self._new_scene.append(self._new_action)
        #     self._new_action = []

    def fadein(self, duration, *actors):
        with serial(self):
            for actor in actors:
                self.set_var(actor, "opacity", 0.0)
            self.enter(*actors)
            with parallel(self):
                for actor in actors:
                    self.linear(actor, "opacity", end_val=1.0,
                                duration=duration)

    def fadeout(self, duration, *actors):
        with serial(self):
            with parallel(self):
                for actor in actors:
                    self.linear(actor, "opacity", end_val=0.0,
                                duration=duration)
            
            self.leave(*actors)


    def _do_action_list(self, action_list):
        if len(self._active_action_lists) > 0:
            start_timer = False
        else:
            start_timer = True

        # add it to the list
        self._active_action_lists.append(action_list)

        if start_timer:
            gobject.timeout_add(self._action_speed,
                                self._process_active_action_lists)

    def _process_active_action_lists(self):
        """
        """
        to_remove = []
        for i,al in enumerate(self._active_action_lists):
            al.process()
            if al.done:
                to_remove.append(i)
        
        # remove the done ones
        to_remove.reverse()
        for i in to_remove:
            self._active_action_lists.pop(i)

        # see if keep going
        if len(self._active_action_lists) == 0:
            return False
        else:
            # keep going
            return True


    def _do_action(self, action):
        # Go call tick every X ms.
        if len(self._active_actions) > 0:
            start_timer = False
        else:
            start_timer = True

        # add it to the active actions
        self._active_actions.append(action)

        if start_timer:
            gobject.timeout_add( self._action_speed,
                                 self._process_active_actions)


    def _process_active_actions(self):
        """
        """
        cur_time = time.time()
        to_remove = []
        for i,action in enumerate(self._active_actions):
            # set the actor's current value
            action.set_var(cur_time)
            if action.done:
                # set to remove it from the active list
                to_remove.append(i)

        # make sure to draw after updating all the actors
        self.queue_draw()

        # remove the done ones
        to_remove.reverse()
        for i in to_remove:
            self._active_actions.pop(i)

        # see if keep going
        if len(self._active_actions) == 0:
            return False
        else:
            # keep going
            return True
        
    def wait(self):
        pass
    
    def pause(self):
        self._actions[-1].add_action(Pause(self))
        # self._new_action.append(Pause(self))
        # if not self._in_parallel:
        #     self._new_scene.append(self._new_action)
        #     self._new_action = []
        
    def _do_pause(self):
        # we're paused
        self._paused = True
        while self._paused:
            self._process_events()
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
            p.fadeout(1.0,x)
            p.fadein(1.0,y)
        p.pause()
        p.fadeout(1.0,y)
        p.pause()

    myplay.add_scene(scene1)

    def scene2(p):
        x = TextBox("Yes, it Rocks!!!")
        p.fadein(1.0,x)
        p.pause()
        p.leave()
    myplay.add_scene(scene2)

    myplay.run()


