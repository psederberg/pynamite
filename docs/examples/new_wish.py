
from __future__ import with_statement

from pynamite import *
from pynamite.actor import TextBox


def true_wish():
    # define some actors
    x = TextBox("Jubba")
    y = TextBox("Wubba")
    f = Flame()
    
    # turn some into a group
    g = Group(x,y)

    # set some starting opacities
    g.opacity = 0.0

    # bring out the group
    g.enter()

    # fade in and out at same time, while showing fire
    with parallel():
        # smooth takes start, end, and duration
        x.opacity = smooth_to(.5,duration=2.0)
        y.opacity = smooth_to(.5,duration=2.0)
        # the flame can burn
        with serial():
            # enter the flame
            f.enter()
            # wait a sec to start
            wait(1.0)
            # burn the flame for a sec
            f.burn(1.0)
            # then leave
            f.leave()

    # Wait for keypress before continuing
    pause()
    
    # group leaves the stage
    g.leave()
