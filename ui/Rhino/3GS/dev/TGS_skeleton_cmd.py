from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino
from compas_rhino.ui import CommandMenu
from compas.datastructures import Network
from compas.datastructures import Mesh
from compas.datastructures import mesh_subdivide_catmullclark
from compas.datastructures import mesh_subdivide_quad
from compas.utilities import geometric_key
from compas.utilities import reverse_geometric_key
from compas.datastructures import meshes_join
from compas.datastructures import meshes_join_and_weld
from compas.geometry import closest_point_in_cloud
from compas.geometry import convex_hull
from compas.geometry import add_vectors
from compas.topology import unify_cycles
from compas.utilities import flatten
from compas.utilities import pairwise
from compas_skeleton.datastructure import Skeleton3D_Node
from compas_skeleton.datastructure import Skeleton3D
from compas_rhino.artists import MeshArtist


__commandname__ = "TGS_skeleton"


def create_sk3_quad(lines, joint_width=1, leaf_width=1, joint_length=0.4):

    def get_convex_hull_mesh(points):
        faces = convex_hull(points)
        vertices = list(set(flatten(faces)))

        i_index = {i: index for index, i in enumerate(vertices)}
        vertices = [points[index] for index in vertices]
        faces = [[i_index[i] for i in face] for face in faces]
        faces = unify_cycles(vertices, faces)

        mesh = Mesh.from_vertices_and_faces(vertices, faces)

        return mesh

    def create_networks():
        networks = {}
        descendent_tree = {}
        for u in joints:
            global_local = {}
            lines = []
            nbrs = network_global.neighbors(u)
            start_pt = network_global.node_coordinates(u)

            for v in nbrs:
                end_pt = network_global.edge_point(u, v, t=joint_length)
                lines.append([start_pt, end_pt])

            network_local = Network.from_lines(lines)
            key_local = list(set(list(network_local.nodes())) - set(network_local.leaves()))[0]
            global_local.update({u: key_local})
            
            gkeys_global_network = [geometric_key(line[1]) for line in lines]
            gkeys_local_network = [
                geometric_key(network_local.node_coordinates(key))
                for key in network_local.leaves()
                ]

            for i, key_global in enumerate(nbrs):
                gkey_global = gkeys_global_network[i]
                index_local = gkeys_local_network.index(gkey_global)
                key_local = network_local.leaves()[index_local]
                global_local.update({key_global: key_local})

            descendent_tree.update({u: global_local})
            networks.update({u: network_local})

        return networks, descendent_tree

    def create_sk3_branch(u, v):
        def find_vertices(u, v):
            sk3_joint_u = sk3_joints[u]

            # inside of network_u, find vertices on the verge
            leaf_u = descendent_tree[u][v] # this is network local key, not convexhull mesh
            leaf_u = sk3_joint_u.network_convexhull[leaf_u]
            nbrs = sk3_joint_u.convexhull_mesh.vertex_neighbors(leaf_u, ordered=True)
            keys = [sk3_joint_u.descendent_tree[leaf_u][nbr]['lp'] for nbr in nbrs]
            points = [sk3_joint_u.vertex_coordinates(key) for key in keys]

            return points

        if u in joints and v in joints:
            # its an internal edge
            points_u = find_vertices(u, v)
            points_v = find_vertices(v, u)

            if len(points_u) != len(points_v):
                mesh = get_convex_hull_mesh(points_u + points_v)
            else:
                points_v = points_v[::-1]
                index = closest_point_in_cloud(points_u[0], points_v)[2]
                points_v = points_v[index:] + points_v[:index]

                vertices = points_u + points_v
                faces = []
                n = len(points_u)
                for i in range(n):
                    faces.append(
                        [i, (i+1)%n, (i+1)%n+n, i+n]
                        )

                mesh = Mesh.from_vertices_and_faces(vertices, faces)
        
        else:
            if u in leafs:
                leaf, joint = u, v
            elif v in leafs:
                leaf, joint = v, u
            
            points_joint = find_vertices(joint, leaf)
            network = networks[joint]

            u_local = descendent_tree[joint][joint]
            v_local = descendent_tree[joint][leaf]

            vec = [
                i * (1 - joint_length) for i in network_global.edge_vector(joint, leaf)
                ]
            points_leaf = [add_vectors(pt, vec) for pt in points_joint]

            vertices = points_joint + points_leaf
            faces = []
            n = len(points_joint)
            for i in range(n):
                faces.append(
                    [i, (i+1)%n, (i+1)%n+n, i+n]
                    )

            mesh = Mesh.from_vertices_and_faces(vertices, faces)

        return mesh

    def create_sk3_branches():

        return [create_sk3_branch(u, v) for u, v in network_global.edges()]

    def create_sk3_joints(networks):
        sk3_joints = {}
        for u in networks:
            network = networks[u]
            sk3_joint = Skeleton3D_Node.from_network(network)
            sk3_joint.joint_width = joint_width
            sk3_joint.leaf_width = leaf_width
            sk3_joint.update_vertices_location()
            sk3_joints.update({u: sk3_joint})
        
        return sk3_joints

    def draw_mesh_faces(mesh):
        fkeys_nodraw = [fkey for fkey in mesh.faces() if mesh.face_area(fkey) <= 0]
        fkeys = list(set(list(mesh.faces())) - set(fkeys_nodraw))

        artist = MeshArtist(mesh)
        artist.layer = '3GS::Skeleton'
        artist.draw_faces(faces=fkeys, join_faces=True)

    network_global = Network.from_lines(lines)

    joints = []
    leafs = []
    for key in network_global.node:
        if network_global.is_leaf(key): 
            leafs.append(key)
        else:
            joints.append(key)

    networks, descendent_tree = create_networks()
    sk3_joints = create_sk3_joints(networks)
    sk3_branches = create_sk3_branches()

    mesh = meshes_join(sk3_joints.values() + sk3_branches)
    draw_mesh_faces(mesh)

    return mesh


def create_sk3_exo(lines, branch_radius=1, node_radius_fac=1, segments=4):
    sk3 = Skeleton3D.from_skeleton_lines(lines)
    sk3.section_seg = segments
    sk3.branch_radius = branch_radius
    sk3.node_radius_fac = node_radius_fac
    sk3.generate_mesh()
    sk3.merge_triangles()

    artist = MeshArtist(sk3)
    artist.layer = '3GS::Skeleton'
    guid = artist.draw_faces(join_faces=True)
    artist.redraw()

    return sk3, guid[0]


def subdivide(mesh, guid):
    compas_rhino.delete_object(guid)
    mesh = mesh_subdivide_catmullclark(mesh, k=1)

    artist = MeshArtist(mesh)
    artist.layer = '3GS::Skeleton'
    guid = artist.draw_faces(join_faces=True)
    artist.redraw()

    return mesh, guid[0]


config = {
    "name": "skeleton_type",
    "message": "SkeletonType",
    "options": [
        {
            "name": "Exoskeleton",
            "message": "Exoskeleton",
            "action": create_sk3_exo
        },
        {
            "name": "QaudSkeleton",
            "message": "QaudSkeleton",
            "action": create_sk3_quad
        },
    ]
}

config_modify = {
    "name": "modify",
    "message": "Modify",
    "options": [
        {
            "name": "Finish",
            "message": "Finish",
            "action": None
        },
        {
            "name": "Subdivide",
            "message": "Subdivide",
            "action": subdivide
        },
    ]
}

def RunCommand(is_interactive):

    if '3GS' not in sc.sticky:
        compas_rhino.display_message('3GS has not been initialised yet.')
        return

    scene = sc.sticky['3GS']['scene']

    # get ForceVolMeshObject from scene
    objects = scene.find_by_name('form')
    if not objects:
        compas_rhino.display_message("There is no FormDiagram in the scene.")
        return
    form = objects[0]

    # --------------------------------------------------------------------------

    # draw skeleton from form ...

    menu = CommandMenu(config)
    action = menu.select_action()
    
    lines = [form.network.edge_coordinates(u, v) for u, v in form.network.edges()]

    if action['name'] == 'Exoskeleton':
        branch_radius = compas_rhino.rs.GetReal('branch radius:')
        node_radius_fac = compas_rhino.rs.GetReal('node size factor:', number=1, minimum=1)
        # segments = compas_rhino.rs.GetInteger('profile segments?', number=4, minimum=3)
        kwargs = {
            'lines': lines,
            'branch_radius': branch_radius,
            'node_radius_fac': node_radius_fac,
            # 'segments': segments
        }

        sk3, guid = action['action'](**kwargs)

    else:
        raise NotImplementedError
        # joint_width = compas_rhino.rs.GetReal('joint node widths:')
        # leaf_width = compas_rhino.rs.GetReal('leaf node widths:')
        # kwargs = {
        #     'lines': lines,
        #     'joint_width': joint_width,
        #     'leaf_width': leaf_width
        # }
        # action['action'](**kwargs)

    while True:
        menu = CommandMenu(config_modify)
        action = menu.select_action()
        if not action:
            return
        
        if action['name'] == 'Finish':
            break

        sk3, guid = action['action'](sk3, guid)

    scene.update()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    RunCommand(True)
