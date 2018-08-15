import Rhino
import System

from Rhino.ApplicationSettings import *

from Rhino.Geometry import Point3d

from compas.geometry import add_vectors

from compas_rhino.helpers.network import network_select_vertices

from compas_3gs.rhino.interface import _get_initial_point
from compas_3gs.rhino.interface import _get_target_point

from compas_rhino.utilities import xdraw_labels
from compas_rhino.utilities import xdraw_lines
from compas_rhino.utilities import xdraw_faces


dotted_color = System.Drawing.Color.FromArgb(0, 0, 0)
arrow_color  = System.Drawing.Color.FromArgb(255, 0, 79)
edge_color   = System.Drawing.Color.FromArgb(0, 0, 0)


def network_vertex_fixity(network):

    vkeys = network_select_vertices(network)

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
            network.v_data[vkey]['x_fix'] = True
            network.v_data[vkey]['y_fix'] = True
            network.v_data[vkey]['z_fix'] = True
        network.v_data[vkey]['x_fix'] = boolOptionX.CurrentValue
        network.v_data[vkey]['y_fix'] = boolOptionY.CurrentValue
        network.v_data[vkey]['z_fix'] = boolOptionZ.CurrentValue

    network.draw(layer='formdiagram')
    return network



def network_vertex_move(network):

    vkeys = network_select_vertices(network)

    nbr_vkeys = {}
    edges = set()
    for vkey in vkeys:
        all_nbrs = network.vertex_neighbours(vkey)
        nbrs = []
        for nbr in all_nbrs:
            if nbr in vkeys:
                edges.add(frozenset([vkey, nbr]))
            else:
                nbrs.append(nbr)
        nbr_vkeys[vkey] = nbrs

    ip   = _get_initial_point()

    def OnDynamicDraw(sender, e):
        cp = e.CurrentPoint
        translation = cp - ip
        for vkey in vkeys:
            xyz = network.vertex_coordinates(vkey)
            sp  = Point3d(*xyz)
            for nbr_vkey in nbr_vkeys[vkey]:
                nbr  = network.vertex_coordinates(nbr_vkey)
                np   = Point3d(*nbr)
                line = Rhino.Geometry.Line(sp, sp + translation)
                e.Display.DrawDottedLine(np, sp + translation, dotted_color)
                e.Display.DrawArrow(line, arrow_color, 15, 0)

        for pair in list(edges):
            pair = list(pair)
            u  = network.vertex_coordinates(pair[0])
            v  = network.vertex_coordinates(pair[1])
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
        new_xyz = add_vectors(network.vertex_coordinates(vkey), translation)
        network.vertex_update_xyz(vkey, new_xyz, constrained=False)

    network.draw(layer='formdiagram')
    return network
