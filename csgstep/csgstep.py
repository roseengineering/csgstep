
__version__ = '0.0.3'

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

# fillet
# https://dev.opencascade.org/doc/refman/html/package_brepfilletapi.html
from OCC.Core.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_EDGE

# edges
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
    :return a Solid object of the 3D shape
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
    :return a Solid object of the 3D shape
    """
    return Solid(BRepPrimAPI_MakeSphere(r).Shape())


def cube(s=1, center=False):
    """Create cube of given size in the z-axis.
    :param s the length of the sides of the cube as a real or 3D vector
    :param center if true center the cube at the origin, otherwise lowest edge is at the origin
    :return a Solid object of the 3D shape
    """
    s = s * np.ones(3)
    p = -s / 2 if center else np.zeros(3)
    return Solid(BRepPrimAPI_MakeBox(gp_Pnt(*p), *s).Shape())


def cylinder(r=1, h=1, center=False):
    """Create cylinder of given radius and height in the z-axis.
    :param h the height of the cylinder
    :param r the radius of the cylinder
    :param center if true center the cylinder on the z-axis, otherwise base is at the origin
    :return a Solid object of the 3D shape
    """
    p = gp_Pnt(0, 0, -h / 2 if center else 0)
    v = gp_Dir(*UZ)
    axes = gp_Ax2(p, v)
    return Solid(BRepPrimAPI_MakeCylinder(axes, r, h).Shape())


def circle(r=1): 
    """Create circle of given radius centered at the origin in the XY plane.
    :param r the radius of the cylinder
    :return a Solid object of the 2D face
    """
    circ = gp_Circ(gp_XOY(), r)
    edge = BRepBuilderAPI_MakeEdge(circ).Edge()
    wire = BRepBuilderAPI_MakeWire(edge).Wire()
    return Solid(BRepBuilderAPI_MakeFace(wire).Shape())


def polygon(points):
    """Create polygon of from 2D points in the XY plane.
    :param points the points of the polygon in path order
    :return a Solid object of the 2D face
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
    :return a Solid object of the 2D face
    """
    s = s * np.ones(2)
    p = s / 2 if center else np.zeros(2)
    points = np.array([
        [0, 0], [s[0], 0], 
        [s[0], s[1]], [0, s[1]]])
    return polygon(points - p)


def segment(pt1, pt2):
    """Create a line segment between two points
    :param pt1 3D start point
    :param pt2 3D end point
    :return a Wire object
    """
    return Wire(BRepBuilderAPI_MakeEdge(gp_Pnt(*pt1), gp_Pnt(*pt2)).Shape())


def circular_arc(pt1, pt2, pt3):
    """Create an arc of circle defined by three points
    :param pt1 3D start point
    :param pt2 3D point on arc of circle
    :param pt3 3D end point
    :return a Wire object
    """
    seg = GC_MakeArcOfCircle(gp_Pnt(*pt1), gp_Pnt(*pt2), gp_Pnt(*pt3))
    assert seg.IsDone()
    return Wire(BRepBuilderAPI_MakeEdge(seg.Value()).Shape())


class Wire:
    def __init__(self, shape=None):
        """Instantiate Wire class with a TopoDS_Shape object.
        :param shape the TopoDS_Shape object to wrap the instantiated class around
        """
        self._shape = shape 

    @property
    def shape(self):
        """Return the TopoDS_Shape object that this Wire object wraps.
        :return the underlying TopoDS_Shape object 
        """
        return self._shape

    def __add__(self, solid):
        """Redirects call to the add method.
        """
        return self.add(solid)

    def add(self, wire):
        """Add this wire to another Wire object.
        :param wire Wire object to add
        :return a new Wire object
        """
        wb = BRepBuilderAPI_MakeWire()
        if self._shape is not None:
            wb.Add(self._shape)
        wb.Add(wire.shape)
        return Wire(wb.Wire())

    def mirror(self, v):
        """Mirror this wire about the given axis.
        :param v 3D vector to mirror wire about
        :return a new Wire object
        """
        trns = gp_Trsf()
        axis = gp_Ax1(gp_Pnt(0,0,0), gp_Dir(*v))
        trns.SetMirror(axis)
        return Wire(BRepBuilderAPI_Transform(self._shape, trns).Shape())

    def face(self):
        """
        Create a face from the Wire object.
        :return a Solid object of the 2D face
        """
        return Solid(BRepBuilderAPI_MakeFace(self._shape).Shape())


class Solid:
    def __init__(self, shape=None):
        """Instantiate Solid class with a TopoDS_Shape object.
        :param shape the TopoDS_Shape object to wrap the instantiated class around
        """
        self._shape = shape 

    @property
    def shape(self):
        """Return the TopoDS_Shape object that this Solid object wraps.
        :return the underlying TopoDS_Shape object 
        """  
        return self._shape

    def write_step(self, filename, schema="AP203"):
        """Write this solid to a STEP file.
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
        """Write this solid to a STL file.
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
        """Mirror this solid about the X axis
        :return a new Solid object
        """
        return self.mirror(UX)

    def mirrorY(self): 
        """Mirror this solid about the Y axis
        :return a new Solid object
        """
        return self.mirror(UY)

    def mirrorZ(self): 
        """Mirror this solid about the Z axis
        :return a new Solid object
        """
        return self.mirror(UZ)

    def rotateX(self, a): 
        """Rotate this solid around the X axis by given angle.
        :param a the angle to rotate by
        :return a new Solid object
        """
        return self.rotate(a, UX)

    def rotateY(self, a): 
        """Rotate this solid around the Y axis by given angle.
        :param a the angle to rotate by
        :return a new Solid object
        """
        return self.rotate(a, UY)

    def rotateZ(self, a): 
        """Rotate this solid around the Z axis by given angle.
        :param a the angle to rotate by
        :return a new Solid object
        """
        return self.rotate(a, UZ)

    def translateX(self, v): 
        """Translate this solid in the X direction by given amount.
        :param v the amount to translate object by
        :return a new Solid object
        """
        return self.translate(v * np.array(UX))

    def translateY(self, v): 
        """Translate this solid in the Y direction by given amount.
        :param v the amount to translate object by
        :return a new Solid object
        """
        return self.translate(v * np.array(UY))

    def translateZ(self, v): 
        """Translate this solid in the Z direction by given amount.
        :param v the amount to translate object by
        :return a new Solid object
        """
        return self.translate(v * np.array(UZ))

    ###

    def union(self, solid):
        """Union this solid with another Solid object.
        :param solid Solid object to merge with
        :return a new Solid object
        """
        # ?? return Solid(BRepAlgoAPI_Fuse(self._shape, solid.shape).Shape())
        shapes = TopTools_ListOfShape()
        if self._shape is not None:
            shapes.Append(self._shape)
        shapes.Append(solid.shape)
        mv = BOPAlgo_MakerVolume()
        mv.SetArguments(shapes)
        mv.Perform()
        return Solid(mv.Shape())

    def intersection(self, solid):
        """Intersect this solid with another Solid object.
        :param solid Solid object to intersect with
        :return a new Solid object
        """
        return Solid(BRepAlgoAPI_Common(self._shape, solid.shape).Shape())

    def difference(self, solid):
        """Cut another solid from this Solid object.
        :param solid Solid object to cut with
        :return a new Solid object
        """
        return Solid(BRepAlgoAPI_Cut(self._shape, solid.shape).Shape())

    def mirror(self, v):
        """Mirror this solid about the given axis.
        :param v 3D vector to mirror object about
        :return a new Solid object
        """
        trns = gp_Trsf()
        axis = gp_Ax1(gp_Pnt(0,0,0), gp_Dir(*v))
        trns.SetMirror(axis)
        return Solid(BRepBuilderAPI_Transform(self._shape, trns).Shape())

    def translate(self, v):
        """Translate this solid by the given 3D vector.
        :param v 3D vector to translate object with
        :return a new Solid object
        """
        trns = gp_Trsf()
        trns.SetTranslation(gp_Vec(*v))
        return Solid(BRepBuilderAPI_Transform(self._shape, trns).Shape())

    def rotate(self, a, v):
        """Rotate this solid around the given 3D vector by the given angle. 
        :param a angle to rotate object
        :param v 3D vector to rotate object around
        :return a new Solid object
        """
        trns = gp_Trsf()
        axis = gp_Ax1(gp_Pnt(0,0,0), gp_Dir(*v))
        trns.SetRotation(axis, a);
        return Solid(BRepBuilderAPI_Transform(self._shape, trns).Shape())

    def scale(self, v):
        """Scale this solid by the given factor.
        :param v the factor to scale, given as a real or 3D vector
        :return a new Solid object
        """
        v = v * np.ones(3)
        gtrns = gp_GTrsf()
        gtrns.SetVectorialPart(gp_Mat(
            v[0], 0, 0,
            0, v[1], 0,
            0, 0, v[2]))
        return Solid(BRepBuilderAPI_GTransform(self._shape, gtrns).Shape())

    def linear_extrude(self, v):
        """Linear extrude this 2D face in the Z direction by given amount.
        :param v the amount to linear extrude by
        :return a new Solid object
        """
        v = v * np.array(UZ)
        return Solid(BRepPrimAPI_MakePrism(self._shape, gp_Vec(*v)).Shape())

    def rotate_extrude(self, a=None):
        """Rotate extrude this 2D face around the Z axis by given angle.
        The object will be rotated around the X axis by 90 degrees before being extruded.
        :param a the angle to rotate extrude by, defaults to 360 degrees
        :return a new Solid object
        """
        solid = self.rotateX(np.pi / 2)
        args = [] if a is None else [a]
        return Solid(BRepPrimAPI_MakeRevol(solid.shape, gp_OZ(), *args).Shape())

    def spline_extrude(self, points):
        """Spline extrude this 2D face along a cubic spline given by 3D points.
        :param points the 3D points to create the cubic spline from 
        :return a new Solid object
        """
        data = TColgp_Array1OfPnt(1, len(points))
        for i, p in enumerate(points):
            data.SetValue(i+1, gp_Pnt(*p))
        spline = GeomAPI_PointsToBSpline(data, 3, 3).Curve()
        edge = BRepBuilderAPI_MakeEdge(spline).Edge()
        wire = BRepBuilderAPI_MakeWire(edge).Wire()
        brep = BRepOffsetAPI_MakePipe(wire, self._shape)
        return Solid(brep.Shape())

    def helix_extrude(self, r, h, pitch, center=False):
        """Helix extrude this 2D face by a given radius, height and pitch.
        :param radius the radius of the helix
        :param height the height of the helix
        :param pitch the pitch of the helix
        :param center if true center the helix on the z-axis, otherwise base is at the origin
        :return a new Solid object
        """
        theta = np.arctan(pitch / (TAU * r))
        face = self.rotateX(np.pi / 2 + theta)
        twist = TAU * h / pitch
        step = TAU / 40
        solid = Solid()
        for u1 in np.arange(0, twist, TAU):
            u2 = min(twist, u1 + TAU)
            u = np.linspace(u1, u2, int(np.ceil(u2 - u1) / step + 1))
            points = np.array([ r * np.cos(u), r * np.sin(u), u / TAU * pitch ]).T
            solid += face.spline_extrude(points - points[0]).translateZ(u1 / TAU * pitch)
        solid = solid.translateX(r)
        if center:
            solid = solid.translateZ(-h / 2)
        return solid

    def fillet(self, r):
        """Fillet edges of the solid by the given radius.
        :param radius the radius to fillet edges by
        :return a new Solid object
        """
        fillet = BRepFilletAPI_MakeFillet(self._shape)
        explorer = TopExp_Explorer(self._shape, TopAbs_EDGE)
        while explorer.More():
            fillet.Add(r, explorer.Current())
            explorer.Next()
        return Solid(fillet.Shape())


