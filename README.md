
![](res/cubeminus.png)

# csgstep

A constructive solid geometry python library for OpenCASCADE.  The API is based on the OpenSCAD and SolidPython API.  The library can read and write STEP files.

## Examples

Create a cube that has a sphere subtracted from it:

```python
from csgstep import cube, sphere
solid = cube(center=True) - sphere(.65)
solid.write_stl('cube.stl')    
solid.write_step('cube.stp')    
```

Create a helix:

```python
from csgstep import circle
pitch = .3
solid = circle(.1)
solid = solid.helix_extrude(r=8, h=3.1 * pitch, pitch=pitch, center=True)
solid.write_stl('helix.stl')    
solid.write_step('helix.stp')    
```
        
Create a pipe:

```python
from csgstep import circle
solid = circle(.2).spline_extrude([(0, 0, 0),(0, 1, 2),(0, 2, 3)])
solid.write_stl('pipe.stl')    
solid.write_step('pipe.stp')    
```

## Dependencies

The library depends on pythonocc-core and numpy.  To install pythonocc-core, I used anaconda and ran "conda install -c conda-forge pythonocc-core".

To install csgstep run "pip install ." in this directory, or the equivalent.  It will bring in numpy.

## Notes

All method functions (not properties) of Solid return a new Solid object.  So remember to always 
assign the result of a method, otherwise it will be lost.

The rotate method here is different from the OpenSCAD rotate method.  The first argument is the angle to rotate and the second argument is the vector to rotate around.

I also added a new extrude method called spline_extrude.  It takes a list of points as its only argument.  These points are converted into a cubic spline which is then used to extrude a solid.  An example of spline_extrude is the helix_extrude method which creates a helix from a solid.

# csgstep API

<code>csgstep.<b>load\_step</b>(filename)</code>  
Load the given STEP File.  
**filename** the path of the STEP file  
**returns** a Solid object of the 3D shape  

<code>csgstep.<b>cube</b>(s=1, center=False)</code>  
Create a cube of given size in the z-axis.  
**s** the length of the sides of the cube as a real or 3D vector  
**center** if true center the cube at the origin, otherwise the lowest edge is at the origin  
**returns** a Solid object of the 3D shape  

<code>csgstep.<b>sphere</b>(r=1)</code>  
Create a sphere of given radius centered at the origin.  
**r** the radius of the sphere  
**returns** a Solid object of the 3D shape  

<code>csgstep.<b>cylinder</b>(r=1, h=1, center=False)</code>  
Create a cylinder of given radius and height in the z-axis.  
**h** the height of the cylinder  
**r** the radius of the cylinder  
**center** if true center the cylinder on the z-axis, otherwise the base is at the origin  
**returns** a Solid object of the 3D shape  

<code>csgstep.<b>circle</b>(r=1)</code>  
Create a circle of given radius centered at the origin in the XY plane.  
**r** the radius of the circle  
**returns** a Solid object of the 2D face  

<code>csgstep.<b>square</b>(s=1, center=False)</code>  
Create a square of given size in the XY plane.  
**s** the length of the sides of the square as a real or 2D vector  
**center** if true center the square at the origin, otherwise one edge is at the origin  
**returns** a Solid object of the 2D face  

<code>csgstep.<b>polygon</b>(points)</code>  
Create a polygon from 2D points in the XY plane.  
**points** the points of the polygon in path order  
**returns** a Solid object of the 2D face  

<code>class csgstep.<b>Solid</b>(self, shape=None)</code>  
Instantiate Solid class with a TopoDS\_Shape object.  
**shape** the TopoDS\_Shape object to wrap the instantiated class around  

Instances of the <code>csgstep.<b>Solid</b></code> class have the following methods:   

<code>Solid.<b>shape</b></code>
Return the TopoDS\_Shape object that this Solid object wraps.  
**returns** the underlying TopoDS\_Shape object  

<code>Solid.<b>write\_step</b>(self, filename, schema='AP203')</code>  
Write this solid to a STEP file.  
**filename** name of STEP output file  
**schema** name of STEP output schema, defaults to AP203  

<code>Solid.<b>write\_stl</b>(self, filename, mode='ascii', linear\_deflection=0.5, angular\_deflection=0.25)</code>  
Write this solid to a STL file.  
**filename** name of STL output file  
**mode** mode of STL file, whether ascii or binary  
**linear\_deflection** linear deflection value  
**angular\_deflection** angular deflection value  

<code>Solid.<b>\_\_add\_\_</b>(self, solid)</code>  
Redirects call to the union method.

<code>Solid.<b>\_\_mul\_\_</b>(self, solid)</code>  
Redirects call to the intersection method.

<code>Solid.<b>\_\_sub\_\_</b>(self, solid)</code>  
Redirects call to the difference method.

<code>Solid.<b>mirrorX</b>(self)</code>  
Mirror this solid about the X axis.  
**returns** a new Solid object  

<code>Solid.<b>mirrorY</b>(self)</code>  
Mirror this solid about the Y axis.  
**returns** a new Solid object  

<code>Solid.<b>mirrorZ</b>(self)</code>  
Mirror this solid about the Z axis.  
**returns** a new Solid object  

<code>Solid.<b>rotateX</b>(self, a)</code>  
Rotate this solid around the X axis by given angle.  
**a** the angle to rotate by  
**returns** a new Solid object  

<code>Solid.<b>rotateY</b>(self, a)</code>  
Rotate this solid around the Y axis by given angle.  
**a** the angle to rotate by  
**returns** a new Solid object  

<code>Solid.<b>rotateZ</b>(self, a)</code>  
Rotate this solid around the Z axis by given angle.  
**a** the angle to rotate by  
**returns** a new Solid object  

<code>Solid.<b>translateX</b>(self, v)</code>  
Translate this solid in the X direction by given amount.  
**v** the amount to translate object by  
**returns** a new Solid object  

<code>Solid.<b>translateY</b>(self, v)</code>  
Translate this solid in the Y direction by given amount.  
**v** the amount to translate object by  
**returns** a new Solid object  

<code>Solid.<b>translateZ</b>(self, v)</code>  
Translate this solid in the Z direction by given amount.  
**v** the amount to translate object by  
**returns** a new Solid object  

<code>Solid.<b>union</b>(self, solid)</code>  
Union this solid with another Solid object.  
**solid** Solid object to merge with  
**returns** a new Solid object  

<code>Solid.<b>intersection</b>(self, solid)</code>  
Intersect this solid with another Solid object.  
**solid** Solid object to intersect with  
**returns** a new Solid object  

<code>Solid.<b>difference</b>(self, solid)</code>  
Cut another solid from this Solid object.  
**solid** Solid object to cut with  
**returns** a new Solid object  

<code>Solid.<b>mirror</b>(self, v)</code>  
Mirror this solid about the given axis.  
**v** the 3D vector to mirror object about  
**returns** a new Solid object  

<code>Solid.<b>translate</b>(self, v)</code>  
Translate this solid by the given 3D vector.  
**v** the 3D vector to translate object with  
**returns** a new Solid object  

<code>Solid.<b>rotate</b>(self, a, v)</code>  
Rotate this solid around the given 3D vector by the given angle.  
**a** angle to rotate object  
**v** the 3D vector to rotate object around  
**returns** a new Solid object  

<code>Solid.<b>scale</b>(self, v)</code>  
Scale this solid by the given factor.  
**v** the factor to scale, given as a real or 3D vector  
**returns** a new Solid object  

<code>Solid.<b>linear\_extrude</b>(self, v)</code>  
Linear extrude this 2D face in the Z direction by given amount.  
**v** the amount to linear extrude by  
**returns** a new Solid object  

<code>Solid.<b>rotate\_extrude</b>(self, a=None)</code>  
Rotate extrude this 2D face around the Z axis by given angle.
The object will be rotated around the X axis by 90 degrees before being extruded.  
**a** the angle to rotate extrude by, defaults to 360 degrees  
**returns** a new Solid object  

<code>Solid.<b>spline\_extrude</b>(self, points)</code>  
Spline extrude this 2D face along a cubic spline given by 3D points.  
**points** the 3D points to create the cubic spline from   
**returns** a new Solid object  

<code>Solid.<b>helix\_extrude</b>(self, r, h, pitch, center=False)</code>  
Helix extrude this 2D face by a given radius, height and pitch.  
**radius** the radius of the helix  
**height** the height of the helix  
**pitch** the pitch of the helix  
**center** if true center the helix on the z-axis, otherwise base is at the origin  
**returns** a new Solid object  

<code>Solid.<b>fillet</b>(self, r)</code>  
Fillet edges of the solid by the given radius.  
**radius** the radius to fillet edges by  
**returns** a new Solid object  

<code>csgstep.<b>segment</b>(pt1, pt2)</code>  
Create a line segment between two points.  
**pt1** the 3D start point  
**pt2** the 3D end point  
**returns** a Wire object  

<code>csgstep.<b>circular\_arc</b>(pt1, pt2, pt3)</code>  
Create an arc of circle defined by three points.  
**pt1** the 3D start point  
**pt2** the 3D point on arc of circle  
**pt3** the 3D end point  
**returns** a Wire object  

<code>class csgstep.<b>Wire</b>(self, shape=None)</code>  
Instantiate Wire class with a TopoDS\_Shape object.  
**shape** the TopoDS\_Shape object to wrap the instantiated class around  

Instances of the <code>csgstep.<b>Wire</b></code> class have the following methods:   

<code>Wire.<b>shape</b></code>
Return the TopoDS\_Shape object that this Wire object wraps.  
**returns** the underlying TopoDS\_Shape object  

<code>Wire.<b>\_\_add\_\_</b>(self, solid)</code>  
Redirects call to the add method.

<code>Wire.<b>add</b>(self, wire)</code>  
Add this wire to another Wire object.  
**wire** Wire object to add  
**returns** a new Wire object  

<code>Wire.<b>mirror</b>(self, v)</code>  
Mirror this wire about the given axis.  
**v** the 3D vector to mirror wire about  
**returns** a new Wire object  

<code>Wire.<b>face</b>(self)</code>  
Create a 2D face from the Wire object.  
**returns** a Solid object of the 2D face  


