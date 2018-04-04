import Rhino
import rhinoscriptsyntax as rs

import compas_rhino

from compas.utilities import color_to_colordict


import compas_rhino.utilities as rhino



def draw_volmesh_face_normals(volmesh):
    pass


def draw_celllabels(volmesh, text=None, color=None):

    if text is None:
        textdict = {ckey: str(ckey) for ckey in volmesh.cell}
    elif isinstance(text, dict):
        textdict = text
    else:
        raise NotImplementedError

    colordict = color_to_colordict(color,
                                   textdict.keys(),
                                   default=(0,0,0),
                                   colorformat='rgb',
                                   normalize=False)

    labels = []
    for ckey, text in iter(textdict.items()):
        labels.append({
            'pos'  : volmesh.cell_centroid(ckey),
            'name' : textdict[ckey],
            'color': colordict[ckey],
            'text' : textdict[ckey],
        })
    return compas_rhino.xdraw_labels(labels, clear=False, redraw=False)
