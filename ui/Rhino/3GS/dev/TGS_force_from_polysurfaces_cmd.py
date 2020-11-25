from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas

import scriptcontext as sc

import compas_rhino

from compas_3gs.diagrams.polyhedral import ForceVolMesh

from compas_rhino.utilities import volmesh_from_polysurfaces

try:
    import rhinoscriptsyntax as rs
except ImportError:
    compas.raise_if_ironpython()


__commandname__ = "TGS_force_from_polysurfaces"


def RunCommand(is_interactive):

    if '3GS' not in sc.sticky:
        compas_rhino.display_message('3GS has not been initialised yet.')
        return

    scene = sc.sticky['3GS']['scene']

    guids = rs.GetObjects("select polysurfaces", filter=rs.filter.polysurface)
    compas_rhino.rs.HideObjects(guids)

    force = volmesh_from_polysurfaces(ForceVolMesh, guids)

    scene.purge()
    scene.add_forcevolmesh(force, name='force', layer='3GS::ForceDiagram')

    objects = scene.find_by_name('force')
    force = objects[0]

    force.check_eq()

    scene.update()
    scene.save()

    print('Polyhedral force diagram successfully created.')


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    RunCommand(True)
