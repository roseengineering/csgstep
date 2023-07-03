
__version__ = '0.0.4'

import numpy as np

# https://dev.opencascade.org/doc/refman/html/package_gp.html
from OCC.Core.gp import (
     gp_Pnt, gp_Vec, gp_Dir, gp_Ax1, gp_Ax2, gp_Pln,
     gp_GTrsf, gp_Trsf, gp_Mat,
     gp_Circ, gp_Elips,
     gp_XOY, gp_OZ, gp_DZ, gp_Origin)

# https://dev.opencascade.org/doc/refman/html/package_brepalgoapi.html
from OCC.Core.BRepAlgoAPI import (
     BRepAlgoAPI_Fuse, BRepAlgoAPI_Common, BRepAlgoAPI_Cut)

# https://dev.opencascade.org/doc/refman/html/package_brepprimapi.html
from OCC.Core.BRepPrimAPI import (
     BRepPrimAPI_MakeBox, BRepPrimAPI_MakeSphere, 
     BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakePrism, 
     BRepPrimAPI_MakeRevol, BRepPrimAPI_MakeWedge,
     BRepPrimAPI_MakeCone)

# https://dev.opencascade.org/doc/refman/html/package_brepbuilderapi.html
from OCC.Core.BRepBuilderAPI import (
     BRepBuilderAPI_Transform, BRepBuilderAPI_GTransform,
     BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace,
     BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire)

# inspection
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_EDGE, TopAbs_FACE

# make pipe, fillet, chamfer, and draft angle
# https://dev.opencascade.org/doc/refman/html/package_brepfilletapi.html
# https://dev.opencascade.org/doc/refman/html/package_brepoffsetapi.html
from OCC.Core.BRepFilletAPI import (
    BRepFilletAPI_MakeFillet, BRepFilletAPI_MakeChamfer)
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakePipe

# draft angle
from OCC.Core.BOPTools import BOPTools_AlgoTools3D
from OCC.Core.BRep import BRep_Tool
from OCC.Core.GeomAdaptor import GeomAdaptor_Surface
from OCC.Core.GeomAbs import GeomAbs_Plane
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_DraftAngle

# splines
# https://dev.opencascade.org/doc/refman/html/package_geomapi.html
# https://dev.opencascade.org/doc/refman/html/package_tcolgp.html
from OCC.Core.TColgp import TColgp_Array1OfPnt
from OCC.Core.GeomAPI import GeomAPI_PointsToBSpline

# union
# https://dev.opencascade.org/doc/refman/html/package_bopalgo.html
# https://dev.opencascade.org/doc/refman/html/package_toptools.html
from OCC.Core.BOPAlgo import BOPAlgo_MakerVolume
from OCC.Core.TopTools import TopTools_ListOfShape

# compound shape
from OCC.Core.BRep import BRep_Builder
from OCC.Core.TopoDS import TopoDS_Compound

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
    :return a Solid object
    """
    step_reader = STEPControl_Reader()
    status = step_reader.ReadFile(filename)
    if status != IFSelect_RetDone:
        raise ValueError('STEP read failed.')
    step_reader.TransferRoot(1)
    return Solid(step_reader.Shape(1))


def sphere(r=1):
    """Create a sphere of the given radius centered at the origin.
    :param r the radius of the sphere
    :return a Solid object
    """
    return Solid(BRepPrimAPI_MakeSphere(r).Shape())


def cube(s=1, center=False):
    """Create a cube of the given size.
    :param s the length of the sides of the cube as a real or 3D vector
    :param center if true center the cube at the origin, otherwise the lowest edge of the cube is at the origin
    :return a Solid object
    """
    s = s * np.ones(3)
    p = -s / 2 if center else np.zeros(3)
    return Solid(BRepPrimAPI_MakeBox(gp_Pnt(*p), *s).Shape())


def cylinder(r=1, h=1, center=False):
    """Create a cylinder along the Z axis of the given radius and height
    :param r the radius of the cylinder
    :param h the height of the cylinder
    :param center if true center the cylinder on the Z axis, otherwise the base is at the origin
    :return a Solid object
    """
    p = gp_Pnt(0, 0, -h / 2 if center else 0)
    v = gp_DZ()
    axes = gp_Ax2(p, v)
    return Solid(BRepPrimAPI_MakeCylinder(axes, r, h).Shape())


def cone(r1=1, r2=0, h=1, center=False):
    """Create a cone along the Z axis of the given base radius, top radius, and height
    :param r1 the bottom radius of the cone
    :param r2 the top radius of the cone
    :param h the height of the cone
    :param center if true center the cone on the Z axis, otherwise the base is at the origin
    :return a Solid object
    """
    p = gp_Pnt(0, 0, -h / 2 if center else 0)
    v = gp_DZ()
    axes = gp_Ax2(p, v)
    return Solid(BRepPrimAPI_MakeCone(axes, r1, r2, h).Shape())


def wedge(s=1, xmin=0, zmin=0, xmax=0, zmax=0):
    """Create a wedge of the given size and given the face at dy.
    :param s the length of the sides of the wedge as a real or 3D vector
    :param xmin the minimum value of x at dy
    :param zmin the minimum value of z at dy
    :param xmax the maximum value of x at dy
    :param zmax the maximum value of z at dy
    :return a Solid object
    """
    s = s * np.ones(3)
    return Solid(BRepPrimAPI_MakeWedge(s[0], s[1], s[2], xmin, zmin, xmax, zmax).Shape())


def circle(r=1): 
    """Create a 2D face of a circle for the given radius centered at the origin in the XY plane.
    :param r the radius of the circle
    :return a Solid object
    """
    circ = gp_Circ(gp_XOY(), r)
    edge = BRepBuilderAPI_MakeEdge(circ).Edge()
    wire = BRepBuilderAPI_MakeWire(edge).Wire()
    return Solid(BRepBuilderAPI_MakeFace(wire).Shape())


def ellipse(rx, ry): 
    """Create a 2D face of a ellipse for the given X radius and Y radius centered at the origin in the XY plane.
    :param rx the radius of the ellipse in the X axis direction
    :param ry the radius of the ellipse in the Y axis direction
    :return a Solid object
    """
    vx = gp_Dir(*UX)
    if rx < ry:
        rx, ry = ry, rx
        vx = gp_Dir(*UY)
    axes = gp_Ax2(gp_Origin(), gp_DZ(), vx)
    elips = gp_Elips(axes, rx, ry)
    edge = BRepBuilderAPI_MakeEdge(elips).Edge()
    wire = BRepBuilderAPI_MakeWire(edge).Wire()
    return Solid(BRepBuilderAPI_MakeFace(wire).Shape())


def square(s=1, center=False):
    """Create a 2D face of a square for the given size in the XY plane.
    :param s the length of the sides of the square as a real or 2D vector
    :param center if true center the square at the origin, otherwise one edge is at the origin
    :return a Solid object
    """
    s = s * np.ones(2)
    p = s / 2 if center else np.zeros(2)
    points = np.array([
        [0, 0], [s[0], 0], 
        [s[0], s[1]], [0, s[1]]])
    return polygon(points - p)


def polygon(points):
    """Create a 2D face of a polygon from 2D points in the XY plane.
    :param points the points of the polygon in path order
    :return a Solid object
    """
    poly = BRepBuilderAPI_MakePolygon()
    for x, y in points:
        poly.Add(gp_Pnt(x, y, 0))
    poly.Close()
    wire = poly.Wire()
    return Solid(BRepBuilderAPI_MakeFace(wire).Shape())


class Solid:
    def __init__(self, shape=None):
        """Instantiate Solid class with a TopoDS_Shape object.
        :param shape the TopoDS_Shape object to wrap the instantiated class around
        """
        self._shape = shape 

    @property
    def shape(self):
        """Return the TopoDS_Shape object this Solid object wraps.
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
        """Mirror this solid about the X axis.
        :return a new Solid object
        """
        return self.mirror(UX)

    def mirrorY(self): 
        """Mirror this solid about the Y axis.
        :return a new Solid object
        """
        return self.mirror(UY)

    def mirrorZ(self): 
        """Mirror this solid about the Z axis.
        :return a new Solid object
        """
        return self.mirror(UZ)

    def rotateX(self, a): 
        """Rotate this solid around the X axis by the given angle.
        :param a the angle to rotate by
        :return a new Solid object
        """
        return self.rotate(a, UX)

    def rotateY(self, a): 
        """Rotate this solid around the Y axis by the given angle.
        :param a the angle to rotate by
        :return a new Solid object
        """
        return self.rotate(a, UY)

    def rotateZ(self, a): 
        """Rotate this solid around the Z axis by the given angle.
        :param a the angle to rotate by
        :return a new Solid object
        """
        return self.rotate(a, UZ)

    def translateX(self, v): 
        """Translate this solid in the X direction by the given amount.
        :param v the amount to translate object by
        :return a new Solid object
        """
        return self.translate(v * np.array(UX))

    def translateY(self, v): 
        """Translate this solid in the Y direction by the given amount.
        :param v the amount to translate object by
        :return a new Solid object
        """
        return self.translate(v * np.array(UY))

    def translateZ(self, v): 
        """Translate this solid in the Z direction by the given amount.
        :param v the amount to translate object by
        :return a new Solid object
        """
        return self.translate(v * np.array(UZ))

    def union(self, solid):
        """Union this solid with another Solid object.
        The openCASCADE BOPAlgo_MakerVolume function is used to perform the union.
        :param solid the Solid object to merge with
        :return a new Solid object
        """
        shapes = TopTools_ListOfShape()
        if self._shape is not None:
            shapes.Append(self._shape)
        shapes.Append(solid.shape)
        mv = BOPAlgo_MakerVolume()
        mv.SetArguments(shapes)
        mv.Perform()
        return Solid(mv.Shape())

    def intersection(self, solid):
        """Intersect this solid with the given Solid object.
        :param solid the Solid object to intersect with
        :return a new Solid object
        """
        return Solid(BRepAlgoAPI_Common(self._shape, solid.shape).Shape())

    def difference(self, solid):
        """Cut the given Solid object from this solid.
        :param solid the Solid object to cut with
        :return a new Solid object
        """
        return Solid(BRepAlgoAPI_Cut(self._shape, solid.shape).Shape())

    def fuse(self, solid):
        """Fuse this solid with the given Solid object.
        The openCASCADE BRepAlgoAPI_Fuse function is used to perform the fusion.
        :param solid the Solid object to merge with
        :return a new Solid object
        """
        return Solid(BRepAlgoAPI_Fuse(self._shape, solid.shape).Shape())

    def compound(self, solid):
        """Create a compound shape with this solid and the given Solid object.
        The method creates a openCASCADE TopoDS_Compound shape from the shapes.
        :param solid the Solid object to create a compound shape with
        :return a new Solid object with the TopoDS_Compound shape
        """
        comp = TopoDS_Compound()
        builder = BRep_Builder()
        builder.MakeCompound(comp)
        if self._shape is not None:
            builder.Add(comp, self._shape)
        builder.Add(comp, solid.shape)
        return Solid(comp)

    def mirror(self, v):
        """Mirror this solid about the given axis.
        :param v the 3D vector to mirror object about
        :return a new Solid object
        """
        trns = gp_Trsf()
        axis = gp_Ax1(gp_Origin(), gp_Dir(*v))
        trns.SetMirror(axis)
        return Solid(BRepBuilderAPI_Transform(self._shape, trns).Shape())

    def translate(self, v):
        """Translate this solid by the given 3D vector.
        :param v the 3D vector to translate object with
        :return a new Solid object
        """
        trns = gp_Trsf()
        trns.SetTranslation(gp_Vec(*v))
        return Solid(BRepBuilderAPI_Transform(self._shape, trns).Shape())

    def rotate(self, a, v):
        """Rotate this solid around the given 3D vector by the given angle. 
        :param a the angle to rotate object
        :param v the 3D vector to rotate object around
        :return a new Solid object
        """
        trns = gp_Trsf()
        axis = gp_Ax1(gp_Origin(), gp_Dir(*v))
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

    def fillet(self, r):
        """Fillet all edges of the solid by the given radius.
        :param radius the radius to fillet edges by
        :return a new Solid object
        """
        fillet = BRepFilletAPI_MakeFillet(self._shape)
        explorer = TopExp_Explorer(self._shape, TopAbs_EDGE)
        while explorer.More():
            fillet.Add(r, explorer.Current())
            explorer.Next()
        return Solid(fillet.Shape())

    def chamfer(self, d):
        """Chamfer all edges of the solid by the given distance.
        :param d the distance to chamfer edges by
        :return a new Solid object
        """
        chamfer = BRepFilletAPI_MakeChamfer(self._shape)
        explorer = TopExp_Explorer(self._shape, TopAbs_EDGE)
        while explorer.More():
            chamfer.Add(d, explorer.Current())
            explorer.Next()
        return Solid(chamfer.Shape())

    def draft(self, a):
        """Apply a draft angle to all vertical faces of the solid.
        The vertical direction is used to measure the draft angle.
        The neutral plane is the XY plane at the origin.
        :param a the draft angle to apply
        :return a new Solid object
        """
        v = gp_DZ()
        neutral_plane = gp_Pln(gp_Origin(), v)
        draft = BRepOffsetAPI_DraftAngle(self._shape)
        explorer = TopExp_Explorer(self._shape, TopAbs_FACE)
        while explorer.More():
            face = explorer.Current()
            surf = BRep_Tool.Surface(face)
            geom = GeomAdaptor_Surface(surf)
            if geom.GetType() == GeomAbs_Plane:
                ex = TopExp_Explorer(face, TopAbs_EDGE)
                normal = gp_Dir()
                BOPTools_AlgoTools3D.GetNormalToFaceOnEdge(ex.Current(), face, normal)
                if normal.IsNormal(v, 0):
                    draft.Add(face, v, a, neutral_plane)
            explorer.Next()
        draft.Build()
        return Solid(draft.Shape())

    def linear_extrude(self, v):
        """Linear extrude this 2D face in the Z direction by the given amount.
        :param v the amount to linear extrude by
        :return a new Solid object
        """
        v = v * np.array(UZ)
        return Solid(BRepPrimAPI_MakePrism(self._shape, gp_Vec(*v)).Shape())

    def rotate_extrude(self, a=None):
        """Rotate extrude this 2D face around the Z axis by the given angle.
        The object will be rotated around the X axis by 90 degrees before being extruded.
        :param a the angle to rotate extrude by, defaults to 360 degrees
        :return a new Solid object
        """
        a = [] if a is None else [a]
        solid = self.rotateX(np.pi / 2)
        return Solid(BRepPrimAPI_MakeRevol(solid.shape, gp_OZ(), *a).Shape())

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
        """Helix extrude this 2D face by the given radius, height and pitch.
        :param radius the radius of the helix
        :param height the height of the helix
        :param pitch the pitch of the helix
        :param center if true center the helix on the Z axis, otherwise base is at the origin
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

