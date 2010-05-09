#
#
from __future__ import with_statement

import gtk, gobject
import cairo
from gtk import gdk
from math import pi, sqrt
import time

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
    def __init__ ( self, width, height, scenes=None,
                   action_speed=20 ):
        self.width = width
        self.height = height
        Screen.__init__( self, width, height )

        if scenes is None:
            scenes = []
        self._scenes = scenes
        self._current_scene = 0

        self._actors = []
        self._active_actions = []
        self._action_speed = action_speed

        self._paused = False

        self._show_started = False

        # start the action timer
        gobject.timeout_add( self._action_speed,
                             self._process_active_actions)

    def _show(self, start_scene=None):
        if not start_scene is None:
            self._current_scene = start_scene

        if self._current_scene < 0:
            self._current_scene = 0
            
        # call the current scene
        if self._current_scene < len(self._scenes):
            self._show_scenes(self._current_scene)


    def _show_scenes(self,s):
        for s in range(s,len(self._scenes)):
            print "Scene %d" % s
            self._current_scene = s
            self._scenes[s](time.time())
            while not self._scenes[s].done:
                self._process_events()

                                
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

        # no all the actors
        for a in self._actors:
            # just draw it
            a._draw(cr)
            
    def _process_events(self, sleep=0.01):
        while gtk.events_pending():
            gtk.main_iteration(False)
        time.sleep(sleep)

    def add_scene(self):
        self._scenes.append(self._actions.pop())

    def add_action(self, action):
        self._actions[-1].add_action(action)

    def enter(self, *actors):
        """
        """
        self._actors.extend(actors)

    def leave(self, *actors):
        if len(actors) == 0:
            # remove them all
            self._actors = []
        else:
            for a in actors:
                if a in self._actors:
                    self._actors.remove(a)

    def wait(self):
        pass
    
    def pause(self):
        # we're paused
        self._paused = True
        while self._paused:
            self._process_events()
        #raw_input()

    def _process_active_actions(self):
        """
        """
        if len(self._active_actions) > 0:
            cur_time = time.time()
            to_remove = []
            for i,action in enumerate(self._active_actions):
                # set the actor's current value
                action(cur_time)
                if action.done:
                    # set to remove it from the active list
                    to_remove.append(i)

            # make sure to draw after updating all the actors
            self.queue_draw()

            # remove the done ones
            to_remove.reverse()
            for i in to_remove:
                self._active_actions.pop(i)

        # keep going
        return True
        
# set up global play instance
global_play = Play(800,600)


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



# class MyPlay(Play):

#     def scene1(self):
#         x = TextBox("Pynamite")
#         y = TextBox("Rocks!!!")
#         self.enter(x)
#         self.pause()
#         with self.parallel():
#             self.fadeout(1.0,x)
#             self.fadein(1.0,y)
#         self.pause()
#         self.fadeout(1.0,y)
#         self.pause()

#         x = TextBox(self)
#         x.enter()
#         x.pause()

#         self.sel('.textbox').fadeIn().pause()

#         def fade1(self):
#             x.fadeout()

#         def fade2(self):
#             y.fadeout()

#         self.in_parallel(fade1, fade2)


# play = MyPlay().run()
# play.run()
