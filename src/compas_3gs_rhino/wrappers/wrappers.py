# from compas_3gs.algorithms import volmesh_dual_network
# from compas_3gs.algorithms import volmesh_reciprocate

# from compas_3gs.operations import cell_subdivide_barycentric


# from compas_3gs_rhino.control.dynamic_pickers import volmesh3gs_select_cell

# try:
#     import rhinoscriptsyntax as rs
#     import scriptcontext as sc
# except ImportError:
#     compas.raise_if_ironpython()


# __author__     = ['Juney Lee']
# __copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
# __license__    = 'MIT License'
# __email__      = 'juney.lee@arch.ethz.ch'


# __all__ = [
#     'rhino_cell_subdivide_barycentric',
# ]






# def rhino_cell_subdivide_barycentric(volmesh, formdiagram=None):

#     ckey = volmesh3gs_select_cell(volmesh)

#     new_ckeys = cell_subdivide_barycentric(volmesh, ckey)


#     if formdiagram:
#         xyz = {vkey: formdiagram.vertex_coordinates(vkey) for vkey in formdiagram.vertex}

#         dual = volmesh_dual_network(volmesh)
#         for vkey in xyz:
#             dual.vertex_update_xyz(vkey, xyz[vkey], constrained=False)

#         volmesh_reciprocate(volmesh,
#                             formdiagram,
#                             weight=1,
#                             min_edge=5,
#                             max_edge=15,
#                             fix_vkeys=xyz.keys(),)


#     dual.draw()

#     volmesh.draw()

#     return volmesh
