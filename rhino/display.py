import Rhino
import rhinoscriptsyntax as rs

import compas_rhino

from compas.geometry import add_vectors
from compas.geometry import scale_vector

from compas.utilities import color_to_colordict


from compas_rhino.utilities import xdraw_lines


def draw_cell(volmesh, ckey):
    hfkeys = volmesh.cell_halffaces(ckey)
    volmesh.draw_faces(fkeys=hfkeys)


def draw_cell_force_vectors(volmesh):

    ckey = volmesh.cell.keys()[0]
    center = volmesh.cell_centroid(ckey)

    lines = []
    for hfkey in volmesh.halfface:
        normal = volmesh.halfface_normal(hfkey, unitized=False)
        # normal = scale_vector(normal, -1)
        lines.append({
            'start': center,
            'end'  : add_vectors(center, normal),
            'arrow': 'end',
            'color': (0, 255, 0),
            'name' : 'hfkey.{}'.format(hfkey)})
    xdraw_lines(lines)



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


def draw_cell_labels(volmesh, text=None, color_dict=None):

    rs.CurrentLayer(volmesh.layer)

    # colordict = color_to_colordict(color,
    #                                textdict.keys(),
    #                                default=(0,0,0),
    #                                colorformat='rgb',
    #                                normalize=False)

    labels = []
    for ckey in volmesh.cell:

        color = (0, 0, 0)
        if color_dict:
            color = color_dict[ckey]
        labels.append({
            'pos'  : volmesh.cell_centroid(ckey),
            'name' : '{0}.cell.label.{1}'.format(volmesh.name, ckey),
            'color': color,
            'layer': volmesh.layer,
            'text' : str(ckey),
        })
    return compas_rhino.xdraw_labels(labels, clear=False, redraw=False)


def clear_cell_labels(volmesh, keys=None):
        if not keys:
            name = '{}.cell.label.*'.format(volmesh.name)
            guids = compas_rhino.get_objects(name=name)
        else:
            guids = []
            for key in keys:
                name = '*.cell.label.{}'.format(key)
                guid = compas_rhino.get_object(name=name)
                guids.append(guid)
        compas_rhino.delete_objects(guids)


