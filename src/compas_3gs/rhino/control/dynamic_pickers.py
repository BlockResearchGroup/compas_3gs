from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas
from compas.utilities import i_to_rgb

from compas_3gs.rhino.control.inspectors import VolmeshCellInspector
from compas_3gs.rhino.control.selectors import CellSelector

try:
    import rhinoscriptsyntax as rs
except ImportError:
    compas.raise_if_ironpython()


__author__     = 'Juney Lee'
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


__all__ = ['volmesh3gs_select_cell']


def volmesh3gs_select_cell(volmesh):

    cell_colors = {}
    ckeys = volmesh.cell.keys()
    for index, ckey in enumerate(ckeys):
        value = 0
        if len(ckeys) > 1:
            value  = float(index) / (len(ckeys) - 1)
        color  = i_to_rgb(value)
        cell_colors[ckey] = color

    volmesh.draw_cell_labels(color_dict=cell_colors)

    rs.EnableRedraw(True)

    # dynamic selector
    cell_inspector = VolmeshCellInspector(volmesh, color_dict=cell_colors)
    cell_inspector.enable()
    ckey = CellSelector.select_cell(volmesh)
    cell_inspector.disable()
    del cell_inspector

    volmesh.clear_cell_labels()

    return ckey


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
