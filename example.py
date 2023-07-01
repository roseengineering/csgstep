# Please install wxpython before running.  Use pythonw to execute.

from OCC.Display.SimpleGui import init_display
from csgstep import cube, sphere

solid = cube(center=True) - sphere(.65)
solid.write_stl('cubeminus.stl')    
solid.write_step('cubeminus.stp')    

display, start_display, add_menu, add_function_to_menu = init_display()
display.DisplayShape(solid.shape)
display.FitAll()
start_display()

