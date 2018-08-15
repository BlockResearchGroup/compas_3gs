from compas.datastructures import VolMesh


def cell_face_split_vertices(self, hfkey):
    hf_vkeys = self.halfface_vertices(hfkey)


def cell_split_vertex(self, vkey, hfkey1, hfkey2):

    if len(self.cell) > 1:
        raise ValueError('This is a multi-cell volmesh.')

    ckey = self.cell.keys()[0]
    halffaces = self.cell_vertex_halffaces(ckey, vkey)
    i = halffaces.index(hfkey1)
    j = halffaces.index(hfkey2)

    if i + 1 == j or j + 1 == i:
        raise ValueError('The two halffaces are adjacent.')

    egi = self.c_data[ckey]['egi']
    hfkeys = egi.face_vertices(vkey)

    f, g = egi.mesh_split_face(vkey, hfkey1, hfkey2)

    x, y, z = self.vertex_coordinates(vkey)
    self.add_vertex(key=f, x=x, y=y, z=z)
    self.add_vertex(key=g, x=x, y=y, z=z)

    # new halffaces ------------------------------------------------------------
    for hfkey in hfkeys:
        new_vkeys = egi.vertex_faces(hfkey, ordered=True)
        self.add_halfface(new_vkeys[::-1], fkey=hfkey)

    print('f', f)
    print('g', g)
    print('hfkey1', self.halfface[hfkey1])
    print('hfkey2', self.halfface[hfkey2])

    self.cell_vertex_delete(vkey)

    print(egi.face)

