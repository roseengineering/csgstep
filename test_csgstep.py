

import unittest
from csgstep import *
import numpy as np

class CSGStepTestCase(unittest.TestCase):

  def test_readwrite(self):
    s = cube()
    s.write_step('/tmp/out.stp')
    s = load_step('/tmp/out.stp')
    s.write_step('/dev/null', schema="AP203")
    s.write_stl('/dev/null', mode='binary')
    s.write_stl('/dev/null', linear_deflection=1, angular_deflection=0.5)

  def test_prim(self):
    Solid()
    sphere()
    cube()
    cylinder()
    ellipse(1, 2)
    ellipse(2, 1)
    # ellipse(1, 1)
    circle()
    square()
    cone()
    wedge()

    cube(center=True)
    cylinder(center=True)
    square(center=True)
    cone(center=True)

    cube(s=1)
    cone(r1=1, r2=0, h=1)
    # cone(r1=1, r2=1, h=1)
    cone(r1=2, r2=1, h=1)
    square(s=1)
    sphere(r=1)
    cylinder(r=1, h=1)
    circle(r=1)
    cube(s=(1,2,3))
    square(s=(1,2))
    polygon([[0,0], [1,1], [0,1]])

  def test_algo(self):
    cube() - sphere()
    cube() + sphere()
    cube() * sphere()
    cube().difference(sphere())
    cube().union(sphere())
    cube().intersection(sphere())

  def test_transform(self):
    cube().rotateX(a=np.pi/4)
    cube().rotateY(a=np.pi/4)
    cube().rotateZ(a=np.pi/4)
    cube().rotate(a=np.pi/4, v=(1,1,1))
    cube().translateX(v=1)
    cube().translateY(v=1)
    cube().translateZ(v=1)
    cube().translate(v=(1,1,1))
    cube().scale(v=2)
    cube().scale(v=(2,2,2))
    cube().mirror(v=(1,1,1))
    cube().mirrorX()
    cube().mirrorY()
    cube().mirrorZ()

  def test_misc(self):
    s = square()
    s += s
    s = square()
    assert(s._shape == s.shape)

  def test_extrudes(self):
    square().linear_extrude(2)
    square().translateX(2).rotate_extrude()
    square().translateX(2).rotate_extrude(a=np.pi/4)
    square().spline_extrude([(0,0,0),(0,1,2),(0,2,3)])
    square(.1, center=True).helix_extrude(r=8, h=5.1, pitch=1)
    circle().linear_extrude(2)
    circle().translateX(2).rotate_extrude()
    circle().translateX(2).rotate_extrude(a=np.pi/4)
    circle().spline_extrude([(0,0,0),(0,1,2),(0,2,3)])
    circle(.1).helix_extrude(r=8, h=5.1, pitch=1)
    points = [[0,0],[1,1],[0,1]]
    polygon(points).linear_extrude(2)
    polygon(points).translateX(2).rotate_extrude()
    polygon(points).translateX(2).rotate_extrude(a=np.pi/4)
    polygon(points).spline_extrude([(0,0,0),(0,1,2),(0,2,3)])
    polygon(points).scale(.1).helix_extrude(r=8, h=5.1, pitch=1)

if __name__ == "__main__":
    unittest.main()



