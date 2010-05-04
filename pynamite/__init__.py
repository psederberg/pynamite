

from play import Play

global_play = Play(800,600)

# set up some actions
enter = global_play.enter
leave = global_play.leave
set_var = global_play.set_var
fadeout = global_play.fadeout
fadein = global_play.fadein
pause = global_play.pause
linear = global_play.linear
smooth = global_play.smooth

# serial/parallel
parallel = global_play.parallel
serial = global_play.parallel
in_parallel = global_play.in_parallel
in_serial = global_play.in_parallel

# run it
add_scene = global_play.add_scene
run = global_play.run

