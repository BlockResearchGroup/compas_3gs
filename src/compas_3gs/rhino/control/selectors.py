from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import ast
import compas

try:
    import rhinoscriptsyntax as rs
except ImportError:
    compas.raise_if_ironpython()


__all__ = ['VolMeshSelector',
           'CellSelector']


class VolMeshSelector(object):

    @staticmethod
    def select_vertex(self, message="Select a vertex."):
        guid = rs.GetObject(message, preselect=True, filter=rs.filter.point | rs.filter.textdot)
        if guid:
            prefix = self.attributes['name']
            name = rs.ObjectName(guid).split('.')
            if 'vertex' in name:
                if not prefix or prefix in name:
                    key = name[-1]
                    return ast.literal_eval(key)
        return None

    @staticmethod
    def select_vertices(self, message="Select vertices."):
        keys = []
        guids = rs.GetObjects(message, preselect=True, filter=rs.filter.point | rs.filter.textdot)
        if guids:
            prefix = self.attributes['name']
            seen = set()
            for guid in guids:
                name = rs.ObjectName(guid).split('.')
                if 'vertex' in name:
                    if not prefix or prefix in name:
                        key = name[-1]
                        if not seen.add(key):
                            key = ast.literal_eval(key)
                            keys.append(key)
        return keys

    @staticmethod
    def select_halfface(self, message="Select a halfface."):
        guid = rs.GetObject(message, preselect=True, filter=rs.filter.mesh)
        if guid:
            prefix = self.attributes['name']
            name = rs.ObjectName(guid).split('.')
            if 'face' in name:
                if not prefix or prefix in name:
                    key = name[-1]
                    return ast.literal_eval(key)
        return None

    @staticmethod
    def select_halffaces(self, message="Select halffaces."):
        keys = []
        guids = rs.GetObjects(message, preselect=True, filter=rs.filter.mesh)
        if guids:
            prefix = self.attributes['name']
            seen = set()
            for guid in guids:
                name = rs.ObjectName(guid).split('.')
                if 'face' in name:
                    if not prefix or prefix in name:
                        key = name[-1]
                        if not seen.add(key):
                            key = ast.literal_eval(key)
                            keys.append(key)
        return keys


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


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   Main
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


if __name__ == '__main__':
    pass
