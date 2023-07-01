# Please install wxpython before running.  Use pythonw to execute.

from OCC.Display.SimpleGui import init_display
from csgstep import *

width = 50
height = 70
thickness = 30
neck_radius = thickness / 4
neck_height = height / 10

p1 = (-width / 2., 0, 0)       
p2 = (-width / 2., -thickness / 4., 0)
p3 = (0, -thickness / 2., 0)
p4 = (width / 2., -thickness / 4., 0)
p5 = (width / 2., 0, 0)

solid = segment(p1, p2) + \
        circular_arc(p2, p3, p4) + \
        segment(p4, p5)
solid += solid.mirror([1,0,0])
solid = solid.face().linear_extrude(height)
solid += cylinder(r=neck_radius, h=neck_height).translateZ(height)

display, start_display, add_menu, add_function_to_menu = init_display()
display.DisplayShape(solid.shape)
display.FitAll()
start_display()

