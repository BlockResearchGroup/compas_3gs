from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas.geometry import add_vectors

from compas_rhino.selectors import VertexSelector

from compas_3gs.rhino.control import get_initial_point

try:
    import Rhino

    from Rhino.ApplicationSettings import *
    from Rhino.Geometry import Point3d

    from System.Drawing.Color import FromArgb

    dotted_color = FromArgb(0, 0, 0)
    arrow_color  = FromArgb(255, 0, 79)
    edge_color   = FromArgb(0, 0, 0)

except ImportError:
    compas.raise_if_ironpython()


__author__     = 'Juney Lee'
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


__all__ = ['rhino_vertex_modify_fixity',
           'rhino_vertex_move',
           'rhino_vertex_align']


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   volmesh or network
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def rhino_vertex_modify_fixity(diagram):
    """Modifies the fixity attribute(s) of selected vertices.

    """

    vkeys = VertexSelector.select_vertices(diagram)

    go = Rhino.Input.Custom.GetOption()
    go.SetCommandPrompt('Set axes Constraints')

    boolOptionA = Rhino.Input.Custom.OptionToggle(False, 'False', 'True')
    boolOptionX = Rhino.Input.Custom.OptionToggle(False, 'False', 'True')
    boolOptionY = Rhino.Input.Custom.OptionToggle(False, 'False', 'True')
    boolOptionZ = Rhino.Input.Custom.OptionToggle(False, 'False', 'True')

    go.AddOptionToggle('A', boolOptionA)
    go.AddOptionToggle('X', boolOptionX)
    go.AddOptionToggle('Y', boolOptionY)
    go.AddOptionToggle('Z', boolOptionZ)

    while True:
        opt = go.Get()
        if go.CommandResult() != Rhino.Commands.Result.Success:
            break
        if opt == Rhino.Input.GetResult.Option:  # keep picking options
            continue
        break

    if not vkeys:
        return

    for vkey in vkeys:
        if boolOptionA.CurrentValue:
            diagram.vertex[vkey]['x_fix'] = True
            diagram.vertex[vkey]['y_fix'] = True
            diagram.vertex[vkey]['z_fix'] = True
        else:
            diagram.vertex[vkey]['x_fix'] = boolOptionX.CurrentValue
            diagram.vertex[vkey]['y_fix'] = boolOptionY.CurrentValue
            diagram.vertex[vkey]['z_fix'] = boolOptionZ.CurrentValue

    diagram.draw(layer=diagram.layer)


def rhino_vertex_move(diagram):
    """Moves the selected vertices.

    """

    vkeys = VertexSelector.select_vertices(diagram)

    nbr_vkeys = {}
    edges = set()
    for vkey in vkeys:
        all_nbrs = diagram.vertex_neighbors(vkey)
        nbrs = []
        for nbr in all_nbrs:
            if nbr in vkeys:
                edges.add(frozenset([vkey, nbr]))
            else:
                nbrs.append(nbr)
        nbr_vkeys[vkey] = nbrs

    ip = get_initial_point()

    def OnDynamicDraw(sender, e):
        cp = e.CurrentPoint
        translation = cp - ip
        for vkey in vkeys:
            xyz = diagram.vertex_coordinates(vkey)
            sp  = Point3d(*xyz)
            for nbr_vkey in nbr_vkeys[vkey]:
                nbr  = diagram.vertex_coordinates(nbr_vkey)
                np   = Point3d(*nbr)
                line = Rhino.Geometry.Line(sp, sp + translation)
                e.Display.DrawDottedLine(np, sp + translation, dotted_color)
                e.Display.DrawArrow(line, arrow_color, 15, 0)

        for pair in list(edges):
            pair = list(pair)
            u  = diagram.vertex_coordinates(pair[0])
            v  = diagram.vertex_coordinates(pair[1])
            sp = Point3d(*u) + translation
            ep = Point3d(*v) + translation
            e.Display.DrawLine(sp, ep, edge_color, 3)

    ModelAidSettings.Ortho = True
    gp = Rhino.Input.Custom.GetPoint()
    gp.DynamicDraw += OnDynamicDraw
    gp.SetCommandPrompt('Point to move to')
    ortho_option = Rhino.Input.Custom.OptionToggle(True, 'Off', 'On')
    gp.AddOptionToggle('ortho_snap', ortho_option)

    while True:
        # ModelAidSettings.Ortho = ortho_option.CurrentValue
        get_rc = gp.Get()
        gp.SetBasePoint(ip, False)
        if gp.CommandResult() != Rhino.Commands.Result.Success:
            continue
        if get_rc == Rhino.Input.GetResult.Option:
            continue
        elif get_rc == Rhino.Input.GetResult.Point:
            target = gp.Point()
        break

    translation = target - ip
    for vkey in vkeys:
        new_xyz = add_vectors(diagram.vertex_coordinates(vkey), translation)
        diagram.vertex_update_xyz(vkey, new_xyz, constrained=False)

    diagram.draw()


def rhino_vertex_align(diagram):

    def update_point(old, new):
        if boolOptionA.CurrentValue is True:
            return new

        if boolOptionX.CurrentValue is True:
            old[0] = new[0]
        if boolOptionY.CurrentValue is True:
            old[1] = new[1]
        if boolOptionZ.CurrentValue is True:
            old[2] = new[2]
        return old

    # --------------------------------------------------------------------------
    # get vkeys to align
    # --------------------------------------------------------------------------
    vkeys = VertexSelector.select_vertices(diagram)
    nbr_vkeys = {}
    edges = set()
    for vkey in vkeys:
        all_nbrs = diagram.plane[vkey].keys()
        nbrs = []
        for nbr in all_nbrs:
            if nbr in vkeys:
                edges.add(frozenset([vkey, nbr]))
            else:
                nbrs.append(nbr)
        nbr_vkeys[vkey] = nbrs

    # --------------------------------------------------------------------------
    # get rhino point
    # --------------------------------------------------------------------------
    gp   = Rhino.Input.Custom.GetPoint()
    gp.SetCommandPrompt('Set alignment Constraints')

    boolOptionA = Rhino.Input.Custom.OptionToggle(False, 'False', 'True')
    boolOptionX = Rhino.Input.Custom.OptionToggle(False, 'False', 'True')
    boolOptionY = Rhino.Input.Custom.OptionToggle(False, 'False', 'True')
    boolOptionZ = Rhino.Input.Custom.OptionToggle(False, 'False', 'True')

    gp.AddOptionToggle('A', boolOptionA)
    gp.AddOptionToggle('X', boolOptionX)
    gp.AddOptionToggle('Y', boolOptionY)
    gp.AddOptionToggle('Z', boolOptionZ)

    def OnDynamicDraw(sender, e):
        cp = e.CurrentPoint

        for vkey in vkeys:
            xyz = diagram.vertex_coordinates(vkey)
            sp  = Point3d(*xyz)
            sp_f = update_point(sp, cp)
            for nbr_vkey in nbr_vkeys[vkey]:
                nbr  = diagram.vertex_coordinates(nbr_vkey)
                np   = Point3d(*nbr)
                e.Display.DrawDottedLine(np, sp_f, dotted_color)
                e.Display.DrawLine(sp, sp_f, edge_color, 3)

        for pair in list(edges):
            pair = list(pair)
            u  = diagram.vertex_coordinates(pair[0])
            v  = diagram.vertex_coordinates(pair[1])
            sp = update_point(Point3d(*u), cp)
            ep = update_point(Point3d(*v), cp)
            e.Display.DrawLine(sp, ep, edge_color, 3)

    while True:
        get_rc = gp.Get()
        gp.DynamicDraw += OnDynamicDraw
        # loop until a point is picked -----------------------------------------
        if gp.CommandResult() != Rhino.Commands.Result.Success:
            break
        if get_rc == Rhino.Input.GetResult.Option:  # keep picking options
            continue
        # loop until a point is picked -----------------------------------------
        elif get_rc == Rhino.Input.GetResult.Point:
            target = gp.Point()
        break

    for vkey in vkeys:
        xyz = update_point(diagram.vertex_coordinates(vkey), target)
        diagram.vertex_update_xyz(vkey, xyz, constrained=False)

    diagram.draw()


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   network
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


# def network_vertex_fixity(network):

#     vkeys = VertexSelector.select_vertices(network)

#     go = Rhino.Input.Custom.GetOption()
#     go.SetCommandPrompt('Set axes Constraints')

#     boolOptionA = Rhino.Input.Custom.OptionToggle(False, 'False', 'True')
#     boolOptionX = Rhino.Input.Custom.OptionToggle(False, 'False', 'True')
#     boolOptionY = Rhino.Input.Custom.OptionToggle(False, 'False', 'True')
#     boolOptionZ = Rhino.Input.Custom.OptionToggle(False, 'False', 'True')

#     go.AddOptionToggle('A', boolOptionA)
#     go.AddOptionToggle('X', boolOptionX)
#     go.AddOptionToggle('Y', boolOptionY)
#     go.AddOptionToggle('Z', boolOptionZ)

#     while True:
#         opt = go.Get()
#         if go.CommandResult() != Rhino.Commands.Result.Success:
#             break
#         if opt == Rhino.Input.GetResult.Option:  # keep picking options
#             continue
#         break

#     if not vkeys:
#         return

#     for vkey in vkeys:
#         if boolOptionA.CurrentValue:
#             network.v_data[vkey]['x_fix'] = True
#             network.v_data[vkey]['y_fix'] = True
#             network.v_data[vkey]['z_fix'] = True
#         network.v_data[vkey]['x_fix'] = boolOptionX.CurrentValue
#         network.v_data[vkey]['y_fix'] = boolOptionY.CurrentValue
#         network.v_data[vkey]['z_fix'] = boolOptionZ.CurrentValue

#     network.draw()

#     return network


# def network_vertex_move(network):

#     vkeys = VertexSelector.select_vertices(network)

#     nbr_vkeys = {}
#     edges = set()
#     for vkey in vkeys:
#         all_nbrs = network.vertex_neighbours(vkey)
#         nbrs = []
#         for nbr in all_nbrs:
#             if nbr in vkeys:
#                 edges.add(frozenset([vkey, nbr]))
#             else:
#                 nbrs.append(nbr)
#         nbr_vkeys[vkey] = nbrs

#     ip   = get_initial_point()

#     def OnDynamicDraw(sender, e):
#         cp = e.CurrentPoint
#         translation = cp - ip
#         for vkey in vkeys:
#             xyz = network.vertex_coordinates(vkey)
#             sp  = Point3d(*xyz)
#             for nbr_vkey in nbr_vkeys[vkey]:
#                 nbr  = network.vertex_coordinates(nbr_vkey)
#                 np   = Point3d(*nbr)
#                 line = Rhino.Geometry.Line(sp, sp + translation)
#                 e.Display.DrawDottedLine(np, sp + translation, dotted_color)
#                 e.Display.DrawArrow(line, arrow_color, 15, 0)

#         for pair in list(edges):
#             pair = list(pair)
#             u  = network.vertex_coordinates(pair[0])
#             v  = network.vertex_coordinates(pair[1])
#             sp = Point3d(*u) + translation
#             ep = Point3d(*v) + translation
#             e.Display.DrawLine(sp, ep, edge_color, 3)

#     ModelAidSettings.Ortho = True
#     gp = Rhino.Input.Custom.GetPoint()
#     gp.DynamicDraw += OnDynamicDraw
#     gp.SetCommandPrompt('Point to move to')
#     ortho_option = Rhino.Input.Custom.OptionToggle(True, 'Off', 'On')
#     gp.AddOptionToggle('ortho_snap', ortho_option)

#     while True:
#         ModelAidSettings.Ortho = ortho_option.CurrentValue
#         get_rc = gp.Get()
#         gp.SetBasePoint(ip, False)
#         if gp.CommandResult() != Rhino.Commands.Result.Success:
#             continue
#         if get_rc == Rhino.Input.GetResult.Option:
#             continue
#         elif get_rc == Rhino.Input.GetResult.Point:
#             target = gp.Point()
#         break

#     translation = target - ip
#     for vkey in vkeys:
#         new_xyz = add_vectors(network.vertex_coordinates(vkey), translation)
#         network.vertex_update_xyz(vkey, new_xyz, constrained=False)

#     network.draw()


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
