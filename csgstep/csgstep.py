
__version__ = '0.0.1'

import numpy as np

# https://dev.opencascade.org/doc/refman/html/package_gp.html
from OCC.Core.gp import (
     gp_Pnt, gp_Vec, gp_Dir, gp_Ax1, gp_Ax2, gp_Mat,
     gp_GTrsf, gp_Trsf, gp_Circ, gp_XOY, gp_OZ)

# https://dev.opencascade.org/doc/refman/html/package_brepalgoapi.html
from OCC.Core.BRepAlgoAPI import (
     BRepAlgoAPI_Fuse, BRepAlgoAPI_Common, BRepAlgoAPI_Cut)

# https://dev.opencascade.org/doc/refman/html/package_brepprimapi.html
from OCC.Core.BRepPrimAPI import (
     BRepPrimAPI_MakeBox, BRepPrimAPI_MakeSphere, BRepPrimAPI_MakeCylinder,
     BRepPrimAPI_MakePrism, BRepPrimAPI_MakeRevol)

# https://dev.opencascade.org/doc/refman/html/package_brepbuilderapi.html
from OCC.Core.BRepBuilderAPI import (
     BRepBuilderAPI_Transform, BRepBuilderAPI_GTransform,
     BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace,
     BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire)

# https://dev.opencascade.org/doc/refman/html/package_gc.html
from OCC.Core.GC import GC_MakeArcOfCircle

# splines
# https://dev.opencascade.org/doc/refman/html/package_brepoffsetapi.html
# https://dev.opencascade.org/doc/refman/html/package_geomapi.html
# https://dev.opencascade.org/doc/refman/html/package_tcolgp.html
from OCC.Core.TColgp import TColgp_Array1OfPnt
from OCC.Core.GeomAPI import GeomAPI_PointsToBSpline
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakePipe

# union
# https://dev.opencascade.org/doc/refman/html/package_bopalgo.html
# https://dev.opencascade.org/doc/refman/html/package_toptools.html
from OCC.Core.BOPAlgo import BOPAlgo_MakerVolume
from OCC.Core.TopTools import TopTools_ListOfShape

# stl and step files
from OCC.Core.Interface import Interface_Static
from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_Reader
from OCC.Core.STEPControl import STEPControl_AsIs
from OCC.Core.StlAPI import StlAPI_Writer
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.IFSelect import IFSelect_RetDone


TAU = 2 * np.pi
UX  = (1.,0.,0.)
UY  = (0.,1.,0.)
UZ  = (0.,0.,1.)


def load_step(filename):
    """Load the given STEP File.
    :param filename the path of the STEP file
    :return a Solid object of the read STEP file
    """
    step_reader = STEPControl_Reader()
    status = step_reader.ReadFile(filename)
    if status != IFSelect_RetDone:
        raise ValueError('STEP read failed.')
    step_reader.TransferRoot(1)
    return Solid(step_reader.Shape(1))


def sphere(r=1):
    """Create sphere of given radius centered at the origin.
    :param r the radius of the sphere
    :return a Solid instance of the sphere 
    """
    return Solid(BRepPrimAPI_MakeSphere(r).Shape())


def cube(s=1, center=False):
    """Create cube of given size in the z-axis.
    :param s the length of the sides of the cube as a real or 3D vector
    :param center if true center the cube at the origin, otherwise lowest edge is at the origin
    :return a Solid instance of the cube
    """
    s = s * np.ones(3)
    p = -s / 2 if center else np.zeros(3)
    return Solid(BRepPrimAPI_MakeBox(gp_Pnt(*p), *s).Shape())


def cylinder(r=1, h=1, center=False):
    """Create cylinder of given radius and height in the z-axis.
    :param h the height of the cylinder
    :param r the radius of the cylinder
    :param center if true center the cylinder on the z-axis, otherwise base is at the origin
    :return a Solid instance of the cylinder
    """
    p = gp_Pnt(0, 0, -h / 2 if center else 0)
    v = gp_Dir(*UZ)
    axes = gp_Ax2(p, v)
    return Solid(BRepPrimAPI_MakeCylinder(axes, r, h).Shape())


def circle(r=1): 
    """Create circle of given radius centered at the origin in the XY plane.
    :param r the radius of the cylinder
    :return a Solid object of the 2D circle
    """
    circ = gp_Circ(gp_XOY(), r)
    edge = BRepBuilderAPI_MakeEdge(circ).Edge()
    wire = BRepBuilderAPI_MakeWire(edge).Wire()
    return Solid(BRepBuilderAPI_MakeFace(wire).Shape())


def polygon(points):
    """Create polygon of from 2D points in the XY plane.
    :param points the points of the polygon in path order
    :return a Solid object of the 2D polygon
    """
    poly = BRepBuilderAPI_MakePolygon()
    for x, y in points:
        poly.Add(gp_Pnt(x, y, 0))
    poly.Close()
    wire = poly.Wire()
    return Solid(BRepBuilderAPI_MakeFace(wire).Shape())


def square(s=1, center=False):
    """Create square of given size in the XY plane.
    :param s the length of the sides of the square as a real or 2D vector
    :param center if true center the square at the origin, otherwise one edge is at the origin
    :return a Solid object of the 2D square
    """
    s = s * np.ones(2)
    p = s / 2 if center else np.zeros(2)
    points = np.array([
        [0, 0], [s[0], 0], 
        [s[0], s[1]], [0, s[1]]])
    return polygon(points - p)


def edge(pt1, pt2):
    """Create a segment between two points
    :param pt1 3D start point
    :param pt2 3D end point
    :return a Solid object of the 2D edge
    """
    return Shape(BRepBuilderAPI_MakeEdge(gp_Pnt(*pt1), gp_Pnt(*pt2)))


def arc(pt1, pt2, pt3):
    """Create an arc of circle defined by three points
    :param pt1 3D start point
    :param pt2 3D point on arc of circle
    :param pt3 3D end point
    :return a Solid object of the 2D edge
    """
    seg = GC_MakeArcOfCircle(gp_Pnt(*pt1), gp_Pnt(*pt2), gp_Pnt(*pt3))
    assert seg.IsDone()
    return Solid(BRepBuilderAPI_MakeEdge(seg))


class Solid:
    def __init__(self, shape=None):
        """Instantiate Solid class with a TopoDS_Shape object.
        :param shape the TopoDS_Shape object to wrap the instantiated class around
        """
        self._shape = shape 

    @property
    def shape(self):
        """Return the TopoDS_Shape object that this object wraps.
        :return the underlying TopoDS_Shape object 
        """  
        return self._shape

    def copy(self):
        """Instantiate a new Solid object with the same TopoDS_Shape object this object wraps.
        :return a copy of this object
        """  
        return Solid(self._shape)

    def write_step(self, filename, schema="AP203"):
        """Write this object to a STEP file.
        :param filename name of STEP output file
        :param schema name of STEP output schema, defaults to AP203
        """ 
        step_writer = STEPControl_Writer()
        Interface_Static.SetCVal("write.step.schema", schema) 
        # use highest representation
        step_writer.Transfer(self._shape, STEPControl_AsIs) 
        status = step_writer.Write(filename)
        if status != IFSelect_RetDone:
            raise ValueError('STEP write failed.')

    def write_stl(self, filename, mode='ascii',
                  linear_deflection=.5, angular_deflection=0.25):
        """Write this object to a STL file.
        :param filename name of STL output file
        :param mode mode of STL file, whether ascii or binary
        :param linear_deflection linear deflection value
        :param angular_deflection angular deflection value
        """
        mesh = BRepMesh_IncrementalMesh(self._shape, 
            linear_deflection, False, angular_deflection)
        mesh.Perform()
        assert mesh.IsDone()
        stl_exporter = StlAPI_Writer()
        stl_exporter.SetASCIIMode(mode == 'ascii')
        status = stl_exporter.Write(self._shape, filename)
        if not status:
            raise ValueError('STL write failed.')

    ###

    def __add__(self, solid):
        """Redirects call to the union method.
        """
        return self.union(solid)

    def __mul__(self, solid):
        """Redirects call to the intersection method.
        """
        return self.intersection(solid)

    def __sub__(self, solid):
        """Redirects call to the difference method.
        """
        return self.difference(solid)

    def mirrorX(self): 
        """Mirror this object about the X axis
        :return this object
        """
        return self.mirror(UX)

    def mirrorY(self): 
        """Mirror this object about the Y axis
        :return this object
        """
        return self.mirror(UY)

    def mirrorZ(self): 
        """Mirror this object about the Z axis
        :return this object
        """
        return self.mirror(UZ)

    def rotateX(self, a): 
        """Rotate this object around the X axis by given angle.
        :param a the angle to rotate by
        :return this object
        """
        return self.rotate(a, UX)

    def rotateY(self, a): 
        """Rotate this object around the Y axis by given angle.
        :param a the angle to rotate by
        :return this object
        """
        return self.rotate(a, UY)

    def rotateZ(self, a): 
        """Rotate this object around the Z axis by given angle.
        :param a the angle to rotate by
        :return this object
        """
        return self.rotate(a, UZ)

    def translateX(self, v): 
        """Translate this object in the X direction by given amount.
        :param v the amount to translate object by
        :return this object
        """
        return self.translate(v * np.array(UX))

    def translateY(self, v): 
        """Translate this object in the Y direction by given amount.
        :param v the amount to translate object by
        :return this object
        """
        return self.translate(v * np.array(UY))

    def translateZ(self, v): 
        """Translate this object in the Z direction by given amount.
        :param v the amount to translate object by
        :return this object
        """
        return self.translate(v * np.array(UZ))

    ###

    def union(self, solid):
        """Union this object with another Solid object.
        The method uses BOPAlgo_MakerVolume() to perform the union.
        :param solid Solid object to merge with
        :return this object
        """  
        shapes = TopTools_ListOfShape()
        if self._shape is not None:
            shapes.Append(self._shape)
        shapes.Append(solid.shape)
        mv = BOPAlgo_MakerVolume()
        mv.SetArguments(shapes)
        mv.Perform()
        self._shape = mv.Shape()
        return self

    def intersection(self, solid):
        """Intersect this object with another Solid object.
        :param solid Solid object to intersect with
        :return this object
        """
        self._shape = BRepAlgoAPI_Common(self._shape, solid.shape).Shape()
        return self

    def difference(self, solid):
        """Cut another Solid object from this object.
        :param solid Solid object to cut with
        :return this object
        """
        self._shape = BRepAlgoAPI_Cut(self._shape, solid.shape).Shape()
        return self

    def fuse(self, solid):
        """Fuse this object with another Solid object.
        The method uses BRepAlgoAPI_Fuse() to perform the union.
        :param solid Solid object to fuse together with
        :return this object
        """
        self._shape = BRepAlgoAPI_Fuse(self._shape, solid.shape).Shape()
        return self

    def mirror(self, v):
        """Mirror this object about the given axis.
        :param v 3D vector to mirror object about
        :return this object
        """
        trns = gp_Trsf()
        axis = gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(*v))
        trns.SetMirror(axis)
        self._shape = BRepBuilderAPI_Transform(self._shape, trns).Shape()
        return self

    def translate(self, v):
        """Translate this object by the given 3D vector.
        :param v 3D vector to translate object with
        :return this object
        """
        trns = gp_Trsf()
        trns.SetTranslation(gp_Vec(*v))
        self._shape = BRepBuilderAPI_Transform(self._shape, trns).Shape()
        return self

    def rotate(self, a, v):
        """Rotate this object around the given 3D vector by the given angle. 
        :param a angle to rotate object
        :param v 3D vector to rotate object around
        :return this object
        """
        trns = gp_Trsf()
        axis = gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(*v))
        trns.SetRotation(axis, a);
        self._shape = BRepBuilderAPI_Transform(self._shape, trns).Shape()
        return self

    def scale(self, v):
        """Scale this object by the given factor.
        :param v the factor to scale, given as a real or 3D vector
        :return this object
        """
        v = v * np.ones(3)
        gtrns = gp_GTrsf()
        gtrns.SetVectorialPart(gp_Mat(
            v[0], 0, 0,
            0, v[1], 0,
            0, 0, v[2]))
        self._shape = BRepBuilderAPI_GTransform(self._shape, gtrns).Shape()
        return self

    def linear_extrude(self, v):
        """Linear extrude this object in the Z direction by given amount.
        :param v the amount to linear extrude this object by
        :return this object
        """
        v = v * np.array(UZ)
        self._shape = BRepPrimAPI_MakePrism(self._shape, gp_Vec(*v)).Shape()
        return self

    def rotate_extrude(self, a=None):
        """Rotate extrude this object around the Z axis by given angle.
        The object will be rotated around the X axis by 90 degrees before being extruded.
        :param a the angle to rotate extrude this object by, defaults to 360 degrees
        :return this object
        """
        self.rotateX(np.pi / 2)
        if a is None:
            self._shape = BRepPrimAPI_MakeRevol(self._shape, gp_OZ()).Shape()
        else:
            self._shape = BRepPrimAPI_MakeRevol(self._shape, gp_OZ(), a).Shape()
        return self

    def spline_extrude(self, points):
        """Spline extrude this object along a cubic spline given by 3D points.
        :param points the 3D points to create the cubic spline from 
        :return this object
        """
        data = TColgp_Array1OfPnt(1, len(points))
        for i, p in enumerate(points):
            data.SetValue(i+1, gp_Pnt(*p))
        spline = GeomAPI_PointsToBSpline(data, 3, 3).Curve()
        edge = BRepBuilderAPI_MakeEdge(spline).Edge()
        wire = BRepBuilderAPI_MakeWire(edge).Wire()
        brep = BRepOffsetAPI_MakePipe(wire, self._shape)
        self._shape = brep.Shape()
        return self

    def helix_extrude(self, r, h, pitch, center=False):
        """Helix extrude this object by a given radius, height and pitch.
        :param radius the radius of the helix
        :param height the height of the helix
        :param pitch the pitch of the helix
        :param center if true center the helix on the z-axis, otherwise base is at the origin
        :return this object
        """
        theta = np.arctan(pitch / (TAU * r))
        self.rotateX(np.pi / 2 + theta)
        twist = TAU * h / pitch
        step = TAU / 40
        solid = Solid()
        for u1 in np.arange(0, twist, TAU):
            u2 = min(twist, u1 + TAU)
            u = np.linspace(u1, u2, int(np.ceil(u2 - u1) / step + 1))
            points = np.array([ r * np.cos(u), r * np.sin(u), u / TAU * pitch ]).T
            solid += Solid(self._shape) \
                .spline_extrude(points - points[0]) \
                .translateZ(u1 / TAU * pitch)
        solid.translateX(r)
        if center:
            solid.translateZ(-h / 2)
        self._shape = solid.shape
        return self


