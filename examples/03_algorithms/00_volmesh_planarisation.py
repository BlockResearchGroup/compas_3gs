from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from compas_rhino.selectors import VertexSelector

from compas_3gs.rhino import rhino_volmesh_from_polysurfaces
from compas_3gs.rhino import rhino_volmesh_planarise


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'

# ------------------------------------------------------------------------------
# 1. make vomesh from rhino polysurfaces
# ------------------------------------------------------------------------------
forcediagram = rhino_volmesh_from_polysurfaces()


# ------------------------------------------------------------------------------
# 2. pick vertices to fix
# ------------------------------------------------------------------------------
vkeys = VertexSelector.select_vertices(forcediagram,
                                       message='Select vertices to fix:')


# ------------------------------------------------------------------------------
# 3. planarise
# ------------------------------------------------------------------------------
rhino_volmesh_planarise(forcediagram,
                        kmax=200,
                        target_normals={},
                        target_centers={},
                        fix_vkeys=vkeys,
                        fix_boundary_normals=False,
                        fix_all_normals=False,
                        flat_tolerance=0.001,
                        refreshrate=10)
