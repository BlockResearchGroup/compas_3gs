from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas

import scriptcontext as sc

import compas_rhino

from compas_3gs.diagrams.polyhedral import formVolMesh

from compas_rhino.utilities import volmesh_from_polysurfaces

try:
    import rhinoscriptsyntax as rs
except ImportError:
    compas.raise_if_ironpython()


__commandname__ = "TGS_reciprocate"


def RunCommand(is_interactive):

    if '3GS' not in sc.sticky:
        compas_rhino.display_message('3GS has not been initialised yet.')
        return

    scene = sc.sticky['3GS']['scene']

# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    RunCommand(True)


