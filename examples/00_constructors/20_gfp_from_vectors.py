from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas
import compas_rhino

from compas.datastructures import Mesh

from compas.utilities import geometric_key


from compas.geometry import distance_point_point
from compas.geometry import subtract_vectors



from compas_rhino.artists import MeshArtist
from compas_rhino.helpers import volmesh_from_polysurfaces

from compas_3gs.diagrams import EGI
from compas_3gs.diagrams import FormNetwork
from compas_3gs.diagrams import ForceVolMesh

from compas_3gs.algorithms import volmesh_dual_volmesh
from compas_3gs.algorithms import volmesh_dual_network

from compas_3gs_rhino.wrappers import rhino_gfp_from_vectors


try:
    import rhinoscriptsyntax as rs
    import scriptcontext as sc
except ImportError:
    compas.raise_if_ironpython()


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


# ------------------------------------------------------------------------------
# make / set layer
# ------------------------------------------------------------------------------


egi = rhino_gfp_from_vectors()
