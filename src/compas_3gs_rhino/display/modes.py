from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas
import compas_rhino

from compas.utilities import i_to_rgb
from compas.utilities import i_to_green
from compas.utilities import i_to_red
from compas.utilities import i_to_blue

from compas.geometry import distance_point_point
from compas.geometry import midpoint_point_point
from compas.geometry import centroid_points
from compas.geometry import project_points_plane
from compas.geometry import bestfit_plane
from compas.geometry import scale_vector
from compas.geometry import add_vectors

from compas_rhino.utilities import xdraw_lines
from compas_rhino.utilities import xdraw_points
from compas_rhino.utilities import xdraw_labels
from compas_rhino.utilities import xdraw_faces

from compas_3gs.utilities import pair_edge_to_halfface

from compas_3gs_rhino.display.helpers import get_index_colordict
from compas_3gs_rhino.display.helpers import get_value_colordict

try:
    import rhinoscriptsyntax as rs
    import scriptcontext as sc
except ImportError:
    compas.raise_if_ironpython()


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


__all__ = ['display_mode_colors']


# ==============================================================================
#   display modes
# ==============================================================================

def display_mode_colors(volmesh, network, label=False):

    edge_halfface_dict = pair_edge_to_halfface(volmesh, network)
    hfkeys = edge_halfface_dict.keys()

    hf_colordict = get_index_colordict(hfkeys)
    edge_colordict = {}
    for hfkey in hf_colordict:
        edge_colordict[edge_halfface_dict[hfkey]] = hf_colordict[hfkey]

    volmesh.clear()
    volmesh.draw_edges()
    volmesh.draw_faces(keys=hfkeys, color=hf_colordict)

    network.clear()
    network.draw_edges(color=edge_colordict)

    if label:
        text_dict = {fkey: str(fkey) for fkey in hfkeys}
        volmesh.draw_face_labels(text=text_dict, color=hf_colordict)
        network.draw_edge_labels(color=edge_colordict)



def display_mode_pipes(volmesh, network):
    pass


def display_mode_vectors(volmesh, network):
    pass


def display_mode_unified_diagram(volmesh, network):
    pass

