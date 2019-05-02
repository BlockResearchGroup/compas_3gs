import Rhino
import System

from Rhino.ApplicationSettings import *

from Rhino.Geometry import Point3d

from compas.geometry import add_vectors



from compas_rhino.helpers.volmesh import volmesh_select_vertices


from compas_3gs.rhino.interface import _get_initial_point
from compas_3gs.rhino.interface import _get_target_point


from compas_rhino.utilities import draw_labels
from compas_rhino.utilities import draw_lines
from compas_rhino.utilities import draw_faces

dotted_color = System.Drawing.Color.FromArgb(0, 0, 0)
arrow_color  = System.Drawing.Color.FromArgb(255, 0, 79)
edge_color   = System.Drawing.Color.FromArgb(0, 0, 0)


def volmesh_vertex_fixity(volmesh):


    vkeys = volmesh_select_vertices(volmesh)

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
            volmesh.v_data[vkey]['x_fix'] = True
            volmesh.v_data[vkey]['y_fix'] = True
            volmesh.v_data[vkey]['z_fix'] = True
        volmesh.v_data[vkey]['x_fix'] = boolOptionX.CurrentValue
        volmesh.v_data[vkey]['y_fix'] = boolOptionY.CurrentValue
        volmesh.v_data[vkey]['z_fix'] = boolOptionZ.CurrentValue

    volmesh.draw(layer='forcepolyhedra')
    return volmesh


def vertex_move(volmesh):

    vkeys = volmesh_select_vertices(volmesh)

    nbr_vkeys = {}
    edges = set()
    for vkey in vkeys:
        all_nbrs = volmesh.plane[vkey].keys()
        nbrs = []
        for nbr in all_nbrs:
            if nbr in vkeys:
                edges.add(frozenset([vkey, nbr]))
            else:
                nbrs.append(nbr)
        nbr_vkeys[vkey] = nbrs

    ip   = _get_initial_point()

    print(nbr_vkeys)
    print(list(edges))

    def OnDynamicDraw(sender, e):
        cp = e.CurrentPoint
        translation = cp - ip
        for vkey in vkeys:
            xyz = volmesh.vertex_coordinates(vkey)
            sp  = Point3d(*xyz)
            for nbr_vkey in nbr_vkeys[vkey]:
                nbr  = volmesh.vertex_coordinates(nbr_vkey)
                np   = Point3d(*nbr)
                line = Rhino.Geometry.Line(sp, sp + translation)
                e.Display.DrawDottedLine(np, sp + translation, dotted_color)
                e.Display.DrawArrow(line, arrow_color, 15, 0)

        for pair in list(edges):
            pair = list(pair)
            u  = volmesh.vertex_coordinates(pair[0])
            v  = volmesh.vertex_coordinates(pair[1])
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
        ModelAidSettings.Ortho = ortho_option.CurrentValue
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
        new_xyz = add_vectors(volmesh.vertex_coordinates(vkey), translation)
        volmesh.vertex_update_xyz(vkey, new_xyz, constrained=False)

    volmesh.draw(layer='forcepolyhedra')


def volmesh_vertex_align(volmesh):

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
    vkeys = volmesh_select_vertices(volmesh)
    nbr_vkeys = {}
    edges = set()
    for vkey in vkeys:
        all_nbrs = volmesh.plane[vkey].keys()
        nbrs = []
        for nbr in all_nbrs:
            if nbr in vkeys:
                edges.add(frozenset([vkey, nbr]))
            else:
                nbrs.append(nbr)
        nbr_vkeys[vkey] = nbrs

    print(nbr_vkeys)

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
            xyz = volmesh.vertex_coordinates(vkey)
            sp  = Point3d(*xyz)
            sp_f = update_point(sp, cp)
            for nbr_vkey in nbr_vkeys[vkey]:
                nbr  = volmesh.vertex_coordinates(nbr_vkey)
                np   = Point3d(*nbr)
                e.Display.DrawDottedLine(np, sp_f, dotted_color)
                e.Display.DrawLine(sp, sp_f, edge_color, 3)

        for pair in list(edges):
            pair = list(pair)
            u  = volmesh.vertex_coordinates(pair[0])
            v  = volmesh.vertex_coordinates(pair[1])
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
        xyz = update_point(volmesh.vertex_coordinates(vkey), target)
        volmesh.vertex_update_xyz(vkey, xyz, constrained=False)

    volmesh.draw(layer='forcepolyhedra')

