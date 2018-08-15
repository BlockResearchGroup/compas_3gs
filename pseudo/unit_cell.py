
def unit_cell_from_EGI(egi):

    cell = VolMesh()

    ckey = cell._get_cell_key(ckey=None)

    cell.c_data[ckey]['egi'] = egi

    for fkey in egi.face:
        x, y, z = egi.face_centroid(fkey)
        cell.add_vertex(vkey=fkey, x=x, y=y, z=z)

    halffaces = []
    for vkey in egi.vertex:
        halfface = egi.vertex_faces(vkey)
        cell.add_halfface(halfface, fkey=vkey)
        halffaces.append(halfface)

    cell.add_cell(halffaces, ckey=ckey)

    return cell