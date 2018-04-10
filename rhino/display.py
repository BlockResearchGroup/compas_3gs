import Rhino
import rhinoscriptsyntax as rs

import compas_rhino

from compas.geometry import add_vectors

from compas.utilities import color_to_colordict


from compas_rhino.utilities import xdraw_lines


def draw_volmesh_face_normals(self, hfkeys):

    lines = []
    for hfkey in hfkeys:
        center = self.halfface_center(hfkey)
        normal = self.halfface_normal(hfkey)
        lines.append({
            'start': center,
            'end'  : add_vectors(center, normal),
            'arrow': 'end',
            'color': (0, 255, 0),
            'name' : '{}.edge.{}'.format(self.attributes['name'], hfkey)})
    xdraw_lines(lines)


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
