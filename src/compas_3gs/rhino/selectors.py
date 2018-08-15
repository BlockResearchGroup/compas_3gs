from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import ast

try:
    import rhinoscriptsyntax as rs
except ImportError:
    import platform
    if platform.python_implementation() == 'IronPython':
        raise


__author__    = ['Juney Lee', ]
__copyright__ = 'Copyright 2018 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'juney.lee@arch.ethz.ch'


__all__ = ['CellSelector', ]


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
    def select_vertices(self, message="Select cells."):

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


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    pass
