compas\_3gs.datastructures.Mesh3gs
==================================

.. currentmodule:: compas_3gs.datastructures

.. autoclass:: Mesh3gs

   
   .. automethod:: __init__

   
   .. rubric:: Methods

   .. autosummary::
   
      ~Mesh3gs.__init__
      ~Mesh3gs.add_edge
      ~Mesh3gs.add_face
      ~Mesh3gs.add_vertex
      ~Mesh3gs.area
      ~Mesh3gs.boundaries
      ~Mesh3gs.centroid
      ~Mesh3gs.clear
      ~Mesh3gs.clear_facedict
      ~Mesh3gs.clear_halfedgedict
      ~Mesh3gs.clear_vertexdict
      ~Mesh3gs.copy
      ~Mesh3gs.cull_edges
      ~Mesh3gs.cull_vertices
      ~Mesh3gs.datastructure_centroid
      ~Mesh3gs.delete_face
      ~Mesh3gs.delete_vertex
      ~Mesh3gs.draw
      ~Mesh3gs.draw_edgelabels
      ~Mesh3gs.draw_edges
      ~Mesh3gs.draw_facelabels
      ~Mesh3gs.draw_faces
      ~Mesh3gs.draw_vertexlabels
      ~Mesh3gs.draw_vertices
      ~Mesh3gs.dump
      ~Mesh3gs.dumps
      ~Mesh3gs.edge_coordinates
      ~Mesh3gs.edge_direction
      ~Mesh3gs.edge_faces
      ~Mesh3gs.edge_label_name
      ~Mesh3gs.edge_length
      ~Mesh3gs.edge_midpoint
      ~Mesh3gs.edge_name
      ~Mesh3gs.edge_point
      ~Mesh3gs.edge_vector
      ~Mesh3gs.edges
      ~Mesh3gs.edges_on_boundary
      ~Mesh3gs.edges_where
      ~Mesh3gs.edges_where_predicate
      ~Mesh3gs.euler
      ~Mesh3gs.face_adjacency_halfedge
      ~Mesh3gs.face_adjacency_vertices
      ~Mesh3gs.face_area
      ~Mesh3gs.face_aspect_ratio
      ~Mesh3gs.face_center
      ~Mesh3gs.face_centroid
      ~Mesh3gs.face_coordinates
      ~Mesh3gs.face_corners
      ~Mesh3gs.face_curvature
      ~Mesh3gs.face_degree
      ~Mesh3gs.face_flatness
      ~Mesh3gs.face_halfedges
      ~Mesh3gs.face_label_name
      ~Mesh3gs.face_max_degree
      ~Mesh3gs.face_min_degree
      ~Mesh3gs.face_name
      ~Mesh3gs.face_neighborhood
      ~Mesh3gs.face_neighbors
      ~Mesh3gs.face_normal
      ~Mesh3gs.face_skewness
      ~Mesh3gs.face_vertex_ancestor
      ~Mesh3gs.face_vertex_descendant
      ~Mesh3gs.face_vertices
      ~Mesh3gs.faces
      ~Mesh3gs.faces_on_boundary
      ~Mesh3gs.faces_where
      ~Mesh3gs.faces_where_predicate
      ~Mesh3gs.from_data
      ~Mesh3gs.from_json
      ~Mesh3gs.from_lines
      ~Mesh3gs.from_obj
      ~Mesh3gs.from_off
      ~Mesh3gs.from_pickle
      ~Mesh3gs.from_ply
      ~Mesh3gs.from_points
      ~Mesh3gs.from_polygons
      ~Mesh3gs.from_polyhedron
      ~Mesh3gs.from_polylines
      ~Mesh3gs.from_stl
      ~Mesh3gs.from_vertices_and_faces
      ~Mesh3gs.genus
      ~Mesh3gs.get_any_edge
      ~Mesh3gs.get_any_face
      ~Mesh3gs.get_any_face_vertex
      ~Mesh3gs.get_any_vertex
      ~Mesh3gs.get_any_vertices
      ~Mesh3gs.get_edge_attribute
      ~Mesh3gs.get_edge_attributes
      ~Mesh3gs.get_edges_attribute
      ~Mesh3gs.get_edges_attributes
      ~Mesh3gs.get_face_attribute
      ~Mesh3gs.get_face_attributes
      ~Mesh3gs.get_face_attributes_all
      ~Mesh3gs.get_faces_attribute
      ~Mesh3gs.get_faces_attributes
      ~Mesh3gs.get_faces_attributes_all
      ~Mesh3gs.get_vertex_attribute
      ~Mesh3gs.get_vertex_attributes
      ~Mesh3gs.get_vertices_attribute
      ~Mesh3gs.get_vertices_attributes
      ~Mesh3gs.gkey_key
      ~Mesh3gs.has_edge
      ~Mesh3gs.has_vertex
      ~Mesh3gs.index_key
      ~Mesh3gs.index_uv
      ~Mesh3gs.insert_vertex
      ~Mesh3gs.is_edge_on_boundary
      ~Mesh3gs.is_empty
      ~Mesh3gs.is_face_on_boundary
      ~Mesh3gs.is_manifold
      ~Mesh3gs.is_orientable
      ~Mesh3gs.is_quadmesh
      ~Mesh3gs.is_regular
      ~Mesh3gs.is_trimesh
      ~Mesh3gs.is_valid
      ~Mesh3gs.is_vertex_connected
      ~Mesh3gs.is_vertex_on_boundary
      ~Mesh3gs.key_gkey
      ~Mesh3gs.key_index
      ~Mesh3gs.leaves
      ~Mesh3gs.load
      ~Mesh3gs.loads
      ~Mesh3gs.mesh_split_face
      ~Mesh3gs.normal
      ~Mesh3gs.number_of_edges
      ~Mesh3gs.number_of_faces
      ~Mesh3gs.number_of_vertices
      ~Mesh3gs.set_edge_attribute
      ~Mesh3gs.set_edge_attributes
      ~Mesh3gs.set_edges_attribute
      ~Mesh3gs.set_edges_attributes
      ~Mesh3gs.set_face_attribute
      ~Mesh3gs.set_face_attributes
      ~Mesh3gs.set_faces_attribute
      ~Mesh3gs.set_faces_attributes
      ~Mesh3gs.set_vertex_attribute
      ~Mesh3gs.set_vertex_attributes
      ~Mesh3gs.set_vertices_attribute
      ~Mesh3gs.set_vertices_attributes
      ~Mesh3gs.summary
      ~Mesh3gs.to_data
      ~Mesh3gs.to_json
      ~Mesh3gs.to_obj
      ~Mesh3gs.to_pickle
      ~Mesh3gs.to_vertices_and_faces
      ~Mesh3gs.update_default_edge_attributes
      ~Mesh3gs.update_default_face_attributes
      ~Mesh3gs.update_default_vertex_attributes
      ~Mesh3gs.uv_index
      ~Mesh3gs.vertex_area
      ~Mesh3gs.vertex_coordinates
      ~Mesh3gs.vertex_curvature
      ~Mesh3gs.vertex_degree
      ~Mesh3gs.vertex_faces
      ~Mesh3gs.vertex_label_name
      ~Mesh3gs.vertex_laplacian
      ~Mesh3gs.vertex_max_degree
      ~Mesh3gs.vertex_min_degree
      ~Mesh3gs.vertex_name
      ~Mesh3gs.vertex_neighborhood
      ~Mesh3gs.vertex_neighborhood_centroid
      ~Mesh3gs.vertex_neighbors
      ~Mesh3gs.vertex_normal
      ~Mesh3gs.vertex_update_xyz
      ~Mesh3gs.vertices
      ~Mesh3gs.vertices_on_boundaries
      ~Mesh3gs.vertices_on_boundary
      ~Mesh3gs.vertices_where
      ~Mesh3gs.vertices_where_predicate
   
   

   
   
   .. rubric:: Attributes

   .. autosummary::
   
      ~Mesh3gs.adjacency
      ~Mesh3gs.data
      ~Mesh3gs.name
   
   