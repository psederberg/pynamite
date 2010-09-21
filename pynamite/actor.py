#
#

import cairo
import pangocairo

from math import pi, sqrt

from play import global_play
from action import Set, enter, leave, fadein, fadeout

class Actor(object):
    """
    """
    play = global_play

    opacity = 1.0
        
    cx = .5
    cy = .5
    
    def __init__(self):
        self.rect = None
    
    def _draw(self,cr):
        """
        """
        raise NotImplemented()

    # wrap setting of vars in actions
    def set(self, var, val, duration=0.0, func="linear"):
        self.play.add_action(Set(self,var,val,
                                 duration=duration, func=func))
        
    def set_opacity(self, val, duration=0.0,func="linear"):
        self.set("opacity", val, duration=duration, func=func)

    def set_cx(self, val, duration=0.0, func="linear"):
        self.set("cx", val, duration=duration, func=func)

    def set_cy(self, val, duration=0.0, func="linear"):
        self.set("cy", val, duration=duration, func=func)

    def enter(self):
        enter(self)

    def leave(self):
        leave(self)

    def fadein(self, duration):
        fadein(duration, self)

    def fadeout(self, duration):
        fadeout(duration, self)



class Stuff(Actor):
    def _draw(self, cr):

        cr.set_line_width(0.01)

        cr.rectangle(0, 0, 1, 1)
        cr.set_source_rgb(1, 1, 1)
        cr.fill()

        cr.move_to(0.75, 0.5)                     #moveto
        cr.rel_curve_to(-0.25, -0.125, -0.25, 0.125, -0.5, 0)  #curveto

        path = list(cr.copy_path_flat())

        cr.set_line_width(max(cr.device_to_user_distance(3, 3)))
        cr.set_source_rgb(0, 0.6, 0)
        cr.stroke()


class TextBox(Actor):
    """
    """
    def __init__(self, text, font="Helvetica"):
        super( TextBox, self ).__init__( )

        self.text = text
        self.font = font
        
    def _draw(self, cr):

        
        cr.select_font_face(self.font,
                            cairo.FONT_SLANT_NORMAL,
                            cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(0.1)

        px = max(cr.device_to_user_distance(1, 1))
        fascent, fdescent, fheight, fxadvance, fyadvance = cr.font_extents()
        xbearing, ybearing, width, height, xadvance, yadvance = \
                cr.text_extents(self.text)
        x = self.cx - xbearing - width / 2
        y = self.cy - fdescent + fheight / 2

        # text
        cr.move_to(x, y)
        cr.set_source_rgba(0, 0, 0, self.opacity)
        cr.show_text(self.text)

class GradientBox(Actor):

    def _draw(self, cr):

        # gradient
        radial = cairo.RadialGradient(0.25, 0.25, 0.1,  0.5, 0.5, 0.5) #gradient
        radial.add_color_stop_rgba(0,  1.0, 0.8, 0.8, self.opacity)                   #gradient
        radial.add_color_stop_rgba(1,  0.9, 0.0, 0.0, self.opacity)                   #gradient
                                                                       #gradient
        for i in range(1, 10):                                         #gradient
            for j in range(1, 10):                                     #gradient
                cr.rectangle(i/10.0 - 0.04, j/10.0 - 0.04, 0.08, 0.08) #gradient
        cr.set_source(radial)                                          #gradient
        cr.fill()                                                      #gradient
                                                                       #gradient
        linear = cairo.LinearGradient(0.25, 0.35, 0.75, 0.65)          #gradient
        linear.add_color_stop_rgba(0.00,  1, 1, 1, 0*self.opacity)                  #gradient
        linear.add_color_stop_rgba(0.25,  0, 1, 0, 0.5*self.opacity)                #gradient
        linear.add_color_stop_rgba(0.50,  1, 1, 1, 0*self.opacity)                  #gradient
        linear.add_color_stop_rgba(0.75,  0, 0, 1, 0.5*self.opacity)                #gradient
        linear.add_color_stop_rgba(1.00,  1, 1, 1, 0*self.opacity)                  #gradient
                                                                       #gradient
        cr.rectangle(0.0, 0.0, 1, 1)                                   #gradient
        cr.set_source(linear)                                          #gradient
        cr.fill()                                                      #gradient

