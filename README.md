
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
solid.helix_extrude(r=8, h=3.1 * pitch, pitch=pitch, center=True)
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

The rotate method is different from the OpenSCAD rotate method.  The first argument is the angle to rotate and the second argument is the vector to rotate around.

I also added a new extrude method called spline_extrude.  It takes a list of points as its only argument.  These points are converted into a cubic spline which is then used to extrude a 2D solid.  An example of spline_extrude is the helix_extrude method which creates a helix from a 2D solid.

# csgstep API

<code>csgstep.<b>circle</b>(r=1)</code>  
Create circle of given radius centered at the origin in the XY plane.  
**r** the radius of the cylinder  
**returns** a 2D Solid object of the circle  

<code>csgstep.<b>cube</b>(s=1, center=False)</code>  
Create cube of given size in the z-axis.  
**s** the length of the sides of the cube as a real or 3D vector  
**center** if true center the cube at the origin, otherwise lowest edge is at the origin  
**returns** a Solid instance of the cube  

<code>csgstep.<b>cylinder</b>(r=1, h=1, center=False)</code>  
Create cylinder of given radius and height in the z-axis.  
**h** the height of the cylinder  
**r** the radius of the cylinder  
**center** if true center the cylinder on the z-axis, otherwise base is at the origin  
**returns** a Solid instance of the cylinder  

<code>csgstep.<b>load\_step</b>(filename)</code>  
Load the given STEP File.  
**filename** the path of the STEP file  
**returns** a Solid object of the read STEP file  

<code>csgstep.<b>polygon</b>(points)</code>  
Create polygon of from 2D points in the XY plane.  
**points** the points of the polygon in path order  
**returns** a 2D Solid object of the polygon  

<code>csgstep.<b>sphere</b>(r=1)</code>  
Create sphere of given radius centered at the origin.  
**r** the radius of the sphere  
**returns** a Solid instance of the sphere  

<code>csgstep.<b>square</b>(s=1, center=False)</code>  
Create square of given size in the XY plane.  
**s** the length of the sides of the square as a real or 2D vector  
**center** if true center the square at the origin, otherwise one edge is at the origin  
**returns** a 2D Solid object of the square  

<code>class csgstep.<b>Solid</b>(self, shape=None)</code>  
Instantiate Solid class with a TopoDS\_Shape object.  
**shape** the TopoDS\_Shape object to wrap the instantiated class around  

Instances of the <code>csgstep.<b>Solid</b></code> class have the following methods:   

<code>Solid.<b>write\_step</b>(self, filename, schema='AP203')</code>  
Write this object to a STEP file.  
**filename** name of STEP output file  
**schema** name of STEP output schema, defaults to AP203  

<code>Solid.<b>write\_stl</b>(self, filename, mode='ascii', linear\_deflection=0.5, angular\_deflection=0.25)</code>  
Write this object to a STL file.  
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

<code>Solid.<b>rotateX</b>(self, a)</code>  
Rotate this object around the X axis by given angle.  
**a** the angle to rotate by  
**returns** this object  

<code>Solid.<b>rotateY</b>(self, a)</code>  
Rotate this object around the Y axis by given angle.  
**a** the angle to rotate by  
**returns** this object  

<code>Solid.<b>rotateZ</b>(self, a)</code>  
Rotate this object around the Z axis by given angle.  
**a** the angle to rotate by  
**returns** this object  

<code>Solid.<b>translateX</b>(self, v)</code>  
Translate this object in the X direction by given amount.  
**v** the amount to translate object by  
**returns** this object  

<code>Solid.<b>translateY</b>(self, v)</code>  
Translate this object in the Y direction by given amount.  
**v** the amount to translate object by  
**returns** this object  

<code>Solid.<b>translateZ</b>(self, v)</code>  
Translate this object in the Z direction by given amount.  
**v** the amount to translate object by  
**returns** this object  

<code>csgstep.<b>shape</b></code>
Return the TopoDS\_Shape object that this object wraps.  
**returns** the underlying TopoDS\_Shape object  

<code>Solid.<b>copy</b>(self)</code>  
Instantiate a new Solid object with the same TopoDS\_Shape object this object wraps.  
**returns** a copy of this object  

<code>Solid.<b>union</b>(self, solid)</code>  
Union this object with another Solid object.  
**solid** Solid object to merge with  
**returns** this object  

<code>Solid.<b>fuse</b>(self, solid)</code>  
Fuse this object with another Solid object.  
**solid** Solid object to fuse together with  
**returns** this object  

<code>Solid.<b>intersection</b>(self, solid)</code>  
Intersect this object with another Solid object.  
**solid** Solid object to intersect with  
**returns** this object  

<code>Solid.<b>difference</b>(self, solid)</code>  
Cut another Solid object from this object.  
**solid** Solid object to cut with  
**returns** this object  

<code>Solid.<b>translate</b>(self, v)</code>  
Translate this object by the given 3D vector.  
**v** 3D vector to translate object with  
**returns** this object  

<code>Solid.<b>rotate</b>(self, a, v)</code>  
Rotate this object around the given 3D vector by the given angle.  
**a** angle to rotate object  
**v** 3D vector to rotate object around  
**returns** this object  

<code>Solid.<b>scale</b>(self, v)</code>  
Scale this object by the given factor.  
**v** the factor to scale, given as a real or 3D vector  
**returns** this object  

<code>Solid.<b>linear\_extrude</b>(self, v)</code>  
Linear extrude this 2D object in the Z direction by given amount.  
**v** the amount to linear extrude this object by  
**returns** this object  

<code>Solid.<b>rotate\_extrude</b>(self, a=None)</code>  
Rotate extrude this 2D object around the Z axis by given angle.
The 2D object will be rotated around the X axis by 90 degrees before being extruded.  
**a** the angle to rotate extrude this object by, defaults to 360 degrees  
**returns** this object  

<code>Solid.<b>spline\_extrude</b>(self, points)</code>  
Spline extrude this 2D object along a cubic spline given by 3D points.  
**points** the 3D points to create the cubic spline from   
**returns** this object  

<code>Solid.<b>helix\_extrude</b>(self, r, h, pitch, center=False)</code>  
Helix extrude this 2D object by a given radius, height and pitch.  
**radius** the radius of the helix  
**height** the height of the helix  
**pitch** the pitch of the helix  
**center** if true center the helix on the z-axis, otherwise base is at the origin  
**returns** this object  


