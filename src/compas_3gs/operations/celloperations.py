

# try:
#     import rhinoscriptsyntax as rs
#     import scriptcontext as sc
# except ImportError:
#     compas.raise_if_ironpython()


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


__all__ = [
    'cell_subdivide_barycentric',
]


def cell_subdivide_barycentric(volmesh, ckey):
    new_ckeys = []
    x, y, z   = volmesh.cell_center(ckey)
    w         = volmesh.add_vertex(x=x, y=y, z=z)

    new_cells = []
    halffaces = volmesh.cell_halffaces(ckey)

    for hfkey in halffaces:
        cell_halffaces = [volmesh.halfface_vertices(hfkey)]

        halfedges = volmesh.halfface_halfedges(hfkey)

        for u, v in halfedges:
            cell_halffaces.append([w, v, u])

        volmesh.delete_halfface(hfkey)
        new_ckeys.append(volmesh.add_cell(cell_halffaces))

    del volmesh.cell[ckey]

    return new_ckeys


def halfface_pinch(volmesh, hfkey, xyz):
    x, y, z = xyz
    w       = volmesh.add_vertex(x=x, y=y, z=z)

    cell_halffaces = [volmesh.halfface_vertices(hfkey).reverse()]

    halfedges = volmesh.halfface_halfedges(hfkey)
    for u, v in halfedges:
            cell_halffaces.append([w, v, u])

