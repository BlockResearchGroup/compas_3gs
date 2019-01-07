
@classmethod
def from_force_vectors(cls, forces_dict, origin):

    egi = cls()

    for key in forces_dict:
        egi.add_vertex(vkey=get_new_vkey(egi),
                       coordinates=forces_dict[key]['normal'] + origin,
                       attributes={'type'  : 'real',
                                   'area'  : forces_dict[key]['magnitude'],
                                   'normal': forces_dict[key]['normal']})

    arcs = {}
    for vkey1 in egi.vertex:
        for vkey2 in egi.vertex:
            if vkey1 != vkey2:
                arc = egi_arc(vkey1, vkey2)
                if (length(arc) != 0) or not (is_antipodal(vkey1, vkey2)):
                    arcs[frozenset([vkey1, vkey2])] = []

    for arc1 in arcs:
        for arc2 in arcs:
            if arc1 != arc2:
                intersection = arc_arc_intersection(arc1, arc2)
                if intersection:
                    new_vkey = get_new_vkey(egi)
                    egi.add_vertex(vkey=new_vkey,
                                   coordinates=intersection,
                                   attributes={'type'  : 'zero',
                                               'area'  : 0,
                                               'normal': intersection - origin})
                    arcs[arc1].append(new_vkey)
                    arcs[arc2].append(new_vkey)

    for arc in arcs:
        ordered_vkeys = reorder_vkeys(list(arc) + arcs[arc_key]['inner_pts'])
        for i in range(len(ordered_vkeys) - 1):
            egi.add_edge(ordered_vkeys[i], ordered_vkeys[i + 1])

    check_for_empty_hemispheres(egi)
    find_egi_faces(egi)

    return egi


@classmethod
def from_volmesh_cell(cls, ckey, volmesh):

    egi = cls()

    egi.attributes['name']   = ckey
    egi.attributes['origin'] = volmesh.cell_centroid(ckey)

    halffaces = volmesh.cell_halffaces(ckey)
    for hfkey in halffaces:
        normal  = volmesh.halfface_normal(hfkey)
        x, y, z = add_vectors(origin, normal)
        egi.add_vertex(key=hfkey, x=x, y=y, z=z)

    vertices  = volmesh.cell_vertices(ckey)
    for vkey in vertices:
        face = volmesh.cell_vertex_halffaces(ckey, vkey)
        egi.add_face(face, fkey=vkey)

    return egi
