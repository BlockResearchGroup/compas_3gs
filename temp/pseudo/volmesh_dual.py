from compas.datastructures import VolMesh

def volmesh_dual_volmesh(volmesh):

    dual_volmesh = VolMesh()

    ext_vkeys = []
    boundary_hfkeys = volmesh.halffaces_boundary()
    for hfkey in boundary_hfkeys:
        for vkey in volmesh.halfface[hfkey]:
            ext_vkeys.append(vkey)
    int_vkeys = list(set(volmesh.vertices()) - set(ext_vkeys))

    if len(int_vkeys) < 1:
        raise ValueError('Not enough cells to create a dual volmesh.')

    for ckey in volmesh.cell:
        x, y, z = volmesh.cell_centroid(ckey)
        dual_volmesh.add_vertex(vkey=ckey, x=x, y=y, z=z)

    for u in int_vkeys:
        cell_halffaces = []
        for v in volmesh.vertex_neighbours(u):
            edge_ckeys = volmesh.plane[u][v].values()
            ckey       = edge_ckeys[0]
            halfface   = [ckey]
            for i in range(len(edge_ckeys) - 1):
                hfkey = volmesh.cell[ckey][u][v]
                w     = volmesh.halfface_vertex_descendant(hfkey, v)
                ckey  = volmesh.plane[w][v][u]
                halfface.append(ckey)
            cell_halffaces.append(halfface)
        dual_volmesh.add_cell(cell_halffaces, ckey=u)

    return dual_volmesh




def mesh_dual(mesh, cls=None):

    if not cls:
        cls = type(mesh)

    dual = cls()

    fkey_centroid = {fkey: mesh.face_centroid(fkey) for fkey in mesh.faces()}
    outer         = mesh.vertices_on_boundary()
    inner         = list(set(mesh.vertices()) - set(outer))
    vertices      = {}
    faces         = {}

    for key in inner:
        fkeys = mesh.vertex_faces(key, ordered=True)
        for fkey in fkeys:
            if fkey not in vertices:
                vertices[fkey] = fkey_centroid[fkey]
        faces[key] = fkeys

    for key, (x, y, z) in vertices.items():
        dual.add_vertex(key, x=x, y=y, z=z)

    for fkey, vertices in faces.items():
        dual.add_face(vertices, fkey=fkey)

    return dual