from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas
import compas_rhino

from compas.geometry import add_vectors
from compas.geometry import scale_vector
from compas.geometry import subtract_vectors
from compas.geometry import normalize_vector
from compas.geometry import length_vector

from compas.utilities import i_to_green
from compas.utilities import color_to_colordict

from compas_3gs.algorithms import volmesh_ud

from compas_3gs.utilities import pair_uv_to_hf

from compas_3gs.utilities import get_index_colordict
from compas_3gs.utilities import valuedict_to_colordict
from compas_3gs.utilities import get_force_mags
from compas_3gs.utilities import get_force_colors_uv
from compas_3gs.utilities import get_force_colors_hf

try:
    import rhinoscriptsyntax as rs
    import scriptcontext as sc

    from System.Drawing.Color import FromArgb

    from Rhino.Geometry import Point3d
    from Rhino.Geometry import Arc
    from Rhino.Geometry import ArcCurve
    from Rhino.Geometry import Sphere
    from Rhino.Geometry import Vector3d
    from Rhino.Geometry import Plane
    from Rhino.Geometry import Brep

    from Rhino.DocObjects.ObjectColorSource import ColorFromObject
    from Rhino.DocObjects.ObjectDecoration import EndArrowhead

    find_object = sc.doc.Objects.Find
    find_layer_by_fullpath = sc.doc.Layers.FindByFullPath
    add_arc = sc.doc.Objects.AddArc
    add_brep = sc.doc.Objects.AddBrep
    add_curve = sc.doc.Objects.AddCurve

except ImportError:
    compas.raise_if_ironpython()


__all__ = ['draw_vertex_normal',
           'draw_vertex_fixities',

           'draw_cell_force_vectors',
           'draw_cell_labels',
           'clear_cell_labels',

           'draw_network_external_forces',
           'draw_network_pipes',
           'draw_network_internal_forces',

           'draw_volmesh_cells',
           'draw_corresponding_elements',
           'draw_compression_tension',
           'draw_directed_hf_and_uv',
           'draw_volmesh_face_normals',
           'draw_volmesh_UD',

           'draw_egi_arcs',

           'bake_cells_as_polysurfaces']


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   vertex
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def draw_vertex_normal(datastructure, vkeys=None):
    pass


def draw_vertex_fixities(diagram):

    text_dict = {}
    color_dict = {}
    for vertex in diagram.vertices():

        text = ''
        r = 0
        g = 0
        b = 0
        if diagram.vertex_attribute(vertex, 'x_fix') is True:
            text += 'x'
            r = 255
        if diagram.vertex_attribute(vertex, 'y_fix') is True:
            text += 'y'
            g = 255
        if diagram.vertex_attribute(vertex, 'z_fix') is True:
            text += 'z'
            b = 255

        if text != '':
            text_dict[vertex] = text
            color_dict[vertex] = (r, g, b)

    diagram.draw()
    guids = diagram.draw_vertexlabels(text=text_dict, color=color_dict)
    return guids


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   face
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def draw_face_normal(datastructure, fkeys=None):
    pass


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   cells
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


# def draw_cell(volmesh, ckeys=None):
#     """Draw the specified cells of a volmesh.

#     Parameters
#     ----------
#     ckeys: list, optional
#         The keys of specific cells that should be drawn.

#     """
#     if not ckeys:
#         return
#     hfkeys = []
#     for ckey in ckeys:
#         hfkeys += volmesh.cell_halffaces(ckey)
#     volmesh.draw_faces(keys=hfkeys)


def draw_cell_force_vectors(volmesh, ckey):
    """Draw the force vectors of a single cell.
    """
    center = volmesh.cell_centroid(ckey)
    lines = []

    for hfkey in volmesh.halfface:
        normal = volmesh.halfface_normal(hfkey, unitized=False)

        lines.append({
            'start': center,
            'end': add_vectors(center, normal),
            'arrow': 'end',
            'color': (0, 255, 0),
            'name': 'hfkey.{}'.format(hfkey)})

    guids = compas_rhino.draw_lines(lines)

    return guids


def draw_cell_labels(volmesh, ckeys=None, text=None, color=None):
    """Draw cell labels.

    Parameters
    ----------
    text : dict
        A dictionary of ckey-text pairs.
        The default value is ``None``, in which case every cell will be labelled with its key.
    colors : str, tuple, dict
        The color specification for the cells.

    """
    if ckeys is None:
        ckeys = volmesh.cell

    # 1. get ckeys to label ----------------------------------------------------
    if text is None:
        textdict = {ckey: str(ckey) for ckey in ckeys}
    elif isinstance(text, dict):
        textdict = text
    else:
        raise NotImplementedError

    # 2. get colors ------------------------------------------------------------
    colordict = get_index_colordict(volmesh.cell)
    if color:
        colordict = color_to_colordict(color,
                                       textdict.keys(),
                                       default=(0, 0, 0),
                                       colorformat='rgb',
                                       normalize=False)

    # 3. labels ----------------------------------------------------------------
    labels = []
    for ckey in textdict:
        labels.append({
            'pos': volmesh.cell_centroid(ckey),
            'name': '{0}.cell.label.{1}'.format(volmesh.name, ckey),
            'color': colordict[ckey],
            'text': textdict[ckey]})

    # 4. draw ------------------------------------------------------------------
    guids = compas_rhino.draw_labels(labels,
                                     layer=volmesh.layer,
                                     clear=False,
                                     redraw=False)
    return guids


def clear_cell_labels(volmesh, ckeys=None):
    """Clear cell labels.

    Parameters
    ----------
    keys : list, optional
        The keys of a specific set of cell labels that should be cleared.
        Default is to clear all cell labels.

    """
    if not ckeys:
        name = '{}.cell.label.*'.format(volmesh.name)
        guids = compas_rhino.get_objects(name=name)
    else:
        guids = []
        for key in ckeys:
            name = '*.cell.label.{}'.format(key)
            guid = compas_rhino.get_object(name=name)
            guids.append(guid)
    guids = compas_rhino.delete_objects(guids)
    return guids


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   volmesh
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def draw_volmesh_cells(volmesh,
                       ckeys=[],
                       color=None):

    # 2. get hf_colors ---------------------------------------------------------
    hf_colordict = color_to_colordict(color,
                                      keys=volmesh.halfface.keys(),
                                      default=(0, 0, 0),
                                      colorformat='rgb',
                                      normalize=False)

    hfkeys = []

    for ckey in ckeys:
        halffaces = volmesh.cell_halffaces(ckey)
        for hfkey in halffaces:
            hfkeys.append(hfkey)

    guids = volmesh.draw_faces(faces=hfkeys, color=hf_colordict)
    return guids


def draw_volmesh_face_normals(volmesh,
                              hfkeys=None,
                              color=None,
                              scale=1):
    """Draws the face normals of the volmesh.

    Parameters
    ----------
    volmesh : volmesh object
        A volmesh datastructure representing a polyhedral force diagram.
    hfkeys : list, optional
        Specific hfkeys to display the normals for.
    hf_c_dict : dictionary, optional
        An optinoal dictionary of hfkey-color pairs.
    scale : float, optional
        Scale factor for the face normal vectors.

    Note
    ----
        By default, normals of volmesh.faces() are drawn. For the interior cell-to-cell interfaces, the normal will be drawn for only one of the two halffaces at that interface.

    """

    # 1. evaluate hfkeys -------------------------------------------------------
    hfkeys = hfkeys or volmesh.faces()

    # 2. get hf_colors ---------------------------------------------------------
    hf_colordict = color_to_colordict(color,
                                      hfkeys,
                                      default=(0, 255, 0),
                                      colorformat='rgb',
                                      normalize=False)

    # 2. normals to draw -------------------------------------------------------
    f_normals = []
    for hfkey in hfkeys:
        center = volmesh.face_center(hfkey)
        normal = scale_vector(volmesh.halfface_normal(hfkey), scale)
        name = '{}.edge.f_normal.{}'.format(volmesh.attributes['name'], hfkey)
        f_normals.append({
            'start': center,
            'end': add_vectors(center, normal),
            'arrow': 'end',
            'color': hf_colordict[hfkey],
            'name': name})

    # 3. draw ------------------------------------------------------------------
    guids = compas_rhino.draw_lines(f_normals,
                                    layer=volmesh.layer,
                                    clear=False,
                                    redraw=False)
    return guids


def draw_volmesh_UD(volmesh,
                    network,
                    color=None,
                    draw_prisms=True,
                    scale=0.5):
    """Draw the unified diagram of a volmesh.
    """

    hfkeys = volmesh.halfface.keys()

    # 1. get colors ------------------------------------------------------------
    hf_color = (0, 0, 0)
    prism_c = (155, 225, 255)  # color for compression prisms
    prism_t = (255, 180, 180)  # color for tension prisms

    hf_colordict = color_to_colordict(color,
                                      hfkeys,
                                      default=hf_color,
                                      colorformat='rgb',
                                      normalize=False)

    # 2. compute unified diagram geometries ------------------------------------
    halffaces, prism_faces = volmesh_ud(volmesh, network, scale=scale)

    # 3. halffaces and prisms --------------------------------------------------
    faces = []
    for hfkey in hfkeys:
        vkeys = volmesh.halfface[hfkey]
        hf_xyz = [halffaces[hfkey][i] for i in vkeys]
        name = '{}.face.ud.{}'.format(volmesh.name, hfkey)
        faces.append({'points': hf_xyz,
                      'name': name,
                      'color': hf_colordict[hfkey]})

    if draw_prisms:
        forces = get_force_mags(volmesh, network)
        for uv in prism_faces:
            name = '{}.face.ud.prism.{}'.format(volmesh.name, uv)
            color = prism_c
            if forces[uv] > 0:
                color = prism_t
            for face in prism_faces[uv]:
                faces.append({'points': face,
                              'name': name,
                              'color': color})

    # 4. draw ------------------------------------------------------------------
    guids = compas_rhino.draw_faces(faces,
                                    layer=volmesh.layer,
                                    clear=False,
                                    redraw=False)

    return guids

# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   network
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def draw_network_external_forces(volmesh,
                                 network,
                                 gradient=True,
                                 scale=1.0):
    """Draws the boundary forces on the form diagram.

    Parameters
    ----------
    volmesh : volmesh object
        A volmesh datastructure representing a polyhedral force diagram.
    network : network object
        A network datastructure representing a polyhedral form diagram.
    scale : float, optional
        Drawing scale factor for the boundary forces.

    """

    load_vectors = {}
    load_mags = {}

    for cell in volmesh.cells_on_boundaries():
        vectors = []
        for face in volmesh.cell_faces(cell):
            if volmesh.is_halfface_on_boundary(face):
                vectors.append(volmesh.halfface_normal(face, unitized=False))

        vectors = zip(*vectors)
        resultant = [sum(vector) for vector in vectors]
        load_vectors[cell] = resultant
        load_mags[cell] = length_vector(resultant)

    # get green gradient
    colordict = valuedict_to_colordict(load_mags, color_scheme=i_to_green)

    lines = []
    for vertex in load_vectors:
        vector = scale_vector(load_vectors[vertex], scale)
        sp = network.vertex_coordinates(vertex)
        ep = add_vectors(sp, vector)
        if volmesh.attributes['convention'] == -1:
            sp, ep = ep, sp
        color = (0, 100, 0)
        if gradient:
            color = colordict[vertex]
        lines.append({
            'start': sp,
            'end': ep,
            'color': color,
            'arrow': 'end',
            'name': '{}.load.at.vertex.{}'.format(network.name, vertex)})

    # 5. draw ------------------------------------------------------------------
    return compas_rhino.draw_lines(lines,
                                   layer=network.layer,
                                   clear=False,
                                   redraw=False)

    # # # 2. get boundary hfs ------------------------------------------------------
    # hfkeys = volmesh.halffaces_on_boundaries()

    # # # 1. delete any existing boundary forces -----------------------------------
    # # name = '*.edge.loads.*'
    # # delete_objects(compas_rhino.get_objects(name=name))

    # # # evaluate specified vertices
    # # if vkeys:
    # #     temp_hfs = []
    # #     for vkey in vkeys:
    # #         cell_hfs = volmesh.cell_halffaces(vkey)
    # #         for cell_hf in cell_hfs:
    # #             if cell_hf in hfkeys:
    # #                 temp_hfs.append(cell_hf)
    # #     if not temp_hfs:
    # #         return
    # #     hfkeys = temp_hfs

    # # 3. get hf areas and colors -----------------------------------------------
    # hf_areas = {hfkey: volmesh.halfface_area(hfkey) for hfkey in hfkeys}

    # hf_c_dict = {}
    # if gradient:
    #     hf_c_dict = valuedict_to_colordict(hf_areas, color_scheme=i_to_green)

    # colordict = color_to_colordict(hf_c_dict,
    #                                hfkeys,
    #                                default=(0, 255, 0),
    #                                colorformat='rgb',
    #                                normalize=False)

    # # 4. forces and labels to draw ---------------------------------------------
    # lines = []
    # for hfkey in hfkeys:
    #     ckey = volmesh.halfface_cell(hfkey)
    #     normal = volmesh.halfface_normal(hfkey, unitized=False)
    #     area = hf_areas[hfkey]
    #     vector = scale_vector(normal, scale)

    #     sp = network.vertex_coordinates(ckey)
    #     ep = add_vectors(sp, vector)
    #     if volmesh.attributes['convention'] == -1:
    #         sp, ep = ep, sp

    #     color = colordict[hfkey]
    #     lines.append({
    #         'start': sp,
    #         'end': ep,
    #         'color': color,
    #         'arrow': 'end',
    #         'name': '{}.edge.loads.{}.{}'.format(network.name, hfkey, area)})

    # # 5. draw ------------------------------------------------------------------
    # guids = compas_rhino.draw_lines(lines,
    #                                 layer=network.layer,
    #                                 clear=False,
    #                                 redraw=False)

    # return guids


def draw_network_internal_forces(volmesh,
                                 network,
                                 vkeys=[],
                                 gradient=True,
                                 scale=1.0):

    # 1. get vkeys -------------------------------------------------------------
    vkeys = vkeys or network.nodes()

    # 2. colors and force magnitudes -------------------------------------------
    uv_f_dict = get_force_mags(volmesh, network)
    uv_c_dict = get_force_colors_uv(volmesh, network, gradient=gradient)

    # 3. vectors to draw -------------------------------------------------------
    arrows = []

    for u in vkeys:
        for v in network.neighbors(u):

            vec = network.edge_direction(u, v)
            u_xyz = network.node_coordinates(u)

            if (u, v) in uv_f_dict:
                force = uv_f_dict[(u, v)]
                color = uv_c_dict[(u, v)]

            else:
                force = uv_f_dict[(v, u)]
                color = uv_c_dict[(v, u)]

            v_xyz = add_vectors(u_xyz, scale_vector(vec, abs(force) * scale))

            sp = u_xyz
            ep = v_xyz
            if force < 0:  # if compression
                sp = v_xyz
                ep = u_xyz

            arrows.append({
                'start': sp,
                'end': ep,
                'color': color,
                'arrow': 'end',
                'layer': network.layer,
                'name': '{}.edge.force.{}-{}'.format(network.name, u, v)})

    # 4. draw force vectors ----------------------------------------------------
    guids = compas_rhino.draw_lines(arrows)

    return guids


def draw_network_pipes(volmesh,
                       network,
                       color=None,
                       scale=1.0):

    colordict = color_to_colordict(color,
                                   [uv for uv in network.edges()],
                                   default=(0, 0, 0),
                                   colorformat='rgb',
                                   normalize=False)

    # 2. map uv to hf ----------------------------------------------------------
    uv_hf_dict = pair_uv_to_hf(network, volmesh)

    # 3. pipes to draw ---------------------------------------------------------
    cylinders = []
    for uv in network.edges():
        cylinders.append({
            'start': network.vertex_coordinates(uv[0]),
            'end': network.vertex_coordinates(uv[1]),
            'radius': volmesh.halfface_area(uv_hf_dict[uv]) * scale,
            'color': colordict[uv],
            'layer': network.layer,
            'name': '{}.edge.pipes.{}'.format(network.name, uv)})

    # 4. draw ------------------------------------------------------------------
    guids = compas_rhino.draw_cylinders(cylinders, cap=True)
    return guids

# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   both diagrams
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def draw_corresponding_elements(volmesh,
                                datastructure,
                                edges=[]):

    if not edges:
        edges = list(datastructure.edges())

    uv_c_dict = get_index_colordict(edges)
    hf_c_dict = get_force_colors_hf(volmesh, datastructure, uv_c_dict=uv_c_dict)

    faces_to_draw = [pair_uv_to_hf(datastructure, volmesh)[uv] for uv in edges]

    volmesh.clear()
    volmesh.draw_edges()
    volmesh.draw_faces(faces=faces_to_draw, color=hf_c_dict)

    datastructure.clear()
    datastructure.draw_edges(color=uv_c_dict)


def draw_compression_tension(volmesh,
                             network,
                             gradient=False,
                             label=False):

    hfkeys = pair_uv_to_hf(network, volmesh).values()

    uv_c_dict = get_force_colors_uv(volmesh, network, gradient=gradient)
    hf_c_dict = get_force_colors_hf(volmesh, network, uv_c_dict=uv_c_dict)

    volmesh.clear()
    volmesh.draw_edges()
    volmesh.draw_faces(faces=hfkeys, color=hf_c_dict)

    network.clear()
    network.draw_edges(color=uv_c_dict)

    # draw labels --------------------------------------------------------------
    if label:
        text_dict = {fkey: str(fkey) for fkey in hfkeys}
        volmesh.draw_facelabels(text=text_dict, color=hf_c_dict)
        network.draw_edgelabels(color=uv_c_dict)


def draw_directed_uv(datastructure,
                     uv_color=None):

    edges = []
    for u, v in datastructure.edges():

        sp = datastructure.vertex_coordinates(u)
        ep = datastructure.vertex_coordinates(v)

        edges.append({
            'start': sp,
            'end': ep,
            'arrow': 'end',
            'color': uv_color[(u, v)],
            'name': '{}.edge.{}-{}'.format(datastructure.name, u, v)})

    # 3. draw network ----------------------------------------------------------
    guids = compas_rhino.draw_lines(edges,
                                    layer=datastructure.layer,
                                    clear=False,
                                    redraw=False)

    return guids


def draw_directed_hf_and_uv(volmesh,
                            datastructure,
                            uv_color=None,
                            scale=1.0):

    hfkeys = pair_uv_to_hf(datastructure, volmesh).values()

    # 1. get colors ------------------------------------------------------------
    uv_colordict = color_to_colordict(uv_color,
                                      [uv for uv in datastructure.edges()],
                                      default=(0, 0, 0),
                                      colorformat='rgb',
                                      normalize=False)
    hf_colordict = get_force_colors_hf(volmesh,
                                       datastructure,
                                       uv_c_dict=uv_colordict)

    # 2. edges to draw ---------------------------------------------------------
    draw_directed_uv(datastructure, uv_color=uv_colordict)

    # 4. draw volmesh ----------------------------------------------------------
    volmesh.draw_faces(faces=hfkeys, color=hf_colordict)
    draw_volmesh_face_normals(volmesh,
                              hfkeys,
                              color=hf_colordict,
                              scale=scale)


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   other
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def draw_egi_arcs(egi):
    origin = egi.attributes['origin']

    for u, v in egi.edges():
        normal_1 = subtract_vectors(egi.vertex_coordinates(u), origin)
        normal_2 = subtract_vectors(egi.vertex_coordinates(v), origin)
        arc = draw_arc(normal_1, normal_2, origin)
        guid = add_curve(arc)
        obj = find_object(guid)
        color = (0, 0, 0)
        if egi.vertex[u]['type'] == 'zero' or egi.vertex[v]['type'] == 'zero':
            color = (255, 0, 0)
        attr = obj.Attributes
        attr.Name = egi.edge_name(u, v)
        attr.ObjectColor = FromArgb(*color)
        attr.ColorSource = ColorFromObject
        attr.ObjectDecoration = EndArrowhead
        obj.CommitChanges()


def bake_cells_as_polysurfaces(volmesh):
    for ckey in volmesh.cells():
        origin = volmesh.cell_centroid(ckey)
        ball = Sphere(Point3d(*tuple(origin)), 100)
        brep = Brep.CreateFromSphere(ball)
        rs.EnableRedraw(False)
        for hfkey in volmesh.cell_faces(ckey):
            center = volmesh.halfface_center(hfkey)
            normal = volmesh.halfface_normal(hfkey)
            plane = Plane(Point3d(*tuple(center)), Vector3d(*tuple(normal)))
            intersection = brep.Trim(plane, 0.1)
            if intersection:
                brep = brep.Trim(plane, 0.0001)[0]
                brep = brep.CapPlanarHoles(0.0001)
        guid = add_brep(brep)
        obj = find_object(guid)
        attr = obj.Attributes
        layer = 'cells_as_polysurfaces'
        rs.AddLayer(layer)
        index = find_layer_by_fullpath(layer, True)
        if index >= 0:
            attr.LayerIndex = index
        attr.Name = 'cell.{0}'.format(ckey)
        obj.CommitChanges()


def draw_arc(normal_1, normal_2, origin):
    mid_pt = normalize_vector(add_vectors(normal_1, normal_2))
    arc = Arc(Point3d(*[sum(axis) for axis in zip(normal_1, origin)]),
              Point3d(*[sum(axis) for axis in zip(mid_pt, origin)]),
              Point3d(*[sum(axis) for axis in zip(normal_2, origin)]))
    arc_as_curve = ArcCurve(arc)
    return arc_as_curve


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   Main
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


if __name__ == '__main__':
    pass
