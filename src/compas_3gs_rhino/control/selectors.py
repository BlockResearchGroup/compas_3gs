from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import ast

from compas_3gs_rhino.control.inspectors import VolmeshVertexInspector
from compas_3gs_rhino.control.inspectors import VolmeshHalffaceInspector
from compas_3gs_rhino.control.inspectors import VolmeshCellInspector

from compas_rhino.helpers.volmesh import volmesh_select_vertex
from compas_rhino.helpers.volmesh import volmesh_select_vertices
from compas_rhino.helpers.volmesh import volmesh_select_face
from compas_rhino.helpers.volmesh import volmesh_select_faces

try:
    import rhinoscriptsyntax as rs
    import scriptcontext as sc
except ImportError:
    compas.raise_if_ironpython()


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


__all__ = ['CellSelector',
           'select_boundary_halffaces']


class CellSelector(object):

    @staticmethod
    def select_cell(self, message="Select a cell."):
        rs.EnableRedraw(True)
        guid = rs.GetObject(message, preselect=True, filter=rs.filter.point | rs.filter.textdot)
        if guid:
            prefix = self.attributes['name']
            name = rs.ObjectName(guid).split('.')
            if 'cell' in name:
                if not prefix or prefix in name:
                    key = name[-1]
                    return ast.literal_eval(key)
        return None

    @staticmethod
    def select_cells(self, message="Select cells."):
        rs.EnableRedraw(True)
        keys = []
        guids = rs.GetObjects(message, preselect=True, filter=rs.filter.point | rs.filter.textdot)
        if guids:
            prefix = self.attributes['name']
            seen = set()
            for guid in guids:
                name = rs.ObjectName(guid).split('.')
                if 'cell' in name:
                    if not prefix or prefix in name:
                        key = name[-1]
                        if not seen.add(key):
                            key = ast.literal_eval(key)
                            keys.append(key)
        return keys


def select_boundary_halffaces(volmesh):

    hfkeys = volmesh.halffaces_on_boundary()

    volmesh.clear()
    volmesh.draw_edges()
    volmesh.draw_faces(fkeys=hfkeys)
    rs.EnableRedraw(True)

    hfkey = volmesh_select_faces(volmesh)

    volmesh.draw()
    print(hfkey)
    return hfkey



# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
