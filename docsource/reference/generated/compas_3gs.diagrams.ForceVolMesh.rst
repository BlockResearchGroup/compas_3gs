compas\_3gs.diagrams.ForceVolMesh
=================================

.. currentmodule:: compas_3gs.diagrams

.. autoclass:: ForceVolMesh

   
   .. automethod:: __init__

   
   .. rubric:: Methods

   .. autosummary::
   
      ~ForceVolMesh.__init__
      ~ForceVolMesh.add_cell
      ~ForceVolMesh.add_halfface
      ~ForceVolMesh.add_vertex
      ~ForceVolMesh.bounding_box
      ~ForceVolMesh.cell_center
      ~ForceVolMesh.cell_centroid
      ~ForceVolMesh.cell_edges
      ~ForceVolMesh.cell_halfedges
      ~ForceVolMesh.cell_halffaces
      ~ForceVolMesh.cell_neighbors
      ~ForceVolMesh.cell_pair_halffaces
      ~ForceVolMesh.cell_to_mesh
      ~ForceVolMesh.cell_to_vertices_and_halffaces
      ~ForceVolMesh.cell_tree
      ~ForceVolMesh.cell_vertex_delete
      ~ForceVolMesh.cell_vertex_halffaces
      ~ForceVolMesh.cell_vertex_neighbors
      ~ForceVolMesh.cell_vertices
      ~ForceVolMesh.cells
      ~ForceVolMesh.centroid
      ~ForceVolMesh.clean
      ~ForceVolMesh.clear
      ~ForceVolMesh.clear_celldict
      ~ForceVolMesh.clear_edges
      ~ForceVolMesh.clear_faces
      ~ForceVolMesh.clear_halffacedict
      ~ForceVolMesh.clear_vertexdict
      ~ForceVolMesh.copy
      ~ForceVolMesh.cull_edges
      ~ForceVolMesh.cull_halffaces
      ~ForceVolMesh.cull_vertices
      ~ForceVolMesh.delete_cell
      ~ForceVolMesh.delete_halfface
      ~ForceVolMesh.delete_vertex
      ~ForceVolMesh.draw
      ~ForceVolMesh.draw_edge_labels
      ~ForceVolMesh.draw_edges
      ~ForceVolMesh.draw_face_labels
      ~ForceVolMesh.draw_faces
      ~ForceVolMesh.draw_vertex_labels
      ~ForceVolMesh.draw_vertices
      ~ForceVolMesh.dump
      ~ForceVolMesh.dumps
      ~ForceVolMesh.edge_cells
      ~ForceVolMesh.edge_coordinates
      ~ForceVolMesh.edge_direction
      ~ForceVolMesh.edge_halffaces
      ~ForceVolMesh.edge_label_name
      ~ForceVolMesh.edge_length
      ~ForceVolMesh.edge_midpoint
      ~ForceVolMesh.edge_name
      ~ForceVolMesh.edge_point
      ~ForceVolMesh.edge_vector
      ~ForceVolMesh.edges
      ~ForceVolMesh.edges_where
      ~ForceVolMesh.edges_where_predicate
      ~ForceVolMesh.face_center
      ~ForceVolMesh.face_coordinates
      ~ForceVolMesh.face_label_name
      ~ForceVolMesh.face_name
      ~ForceVolMesh.faces
      ~ForceVolMesh.faces_interior
      ~ForceVolMesh.faces_where
      ~ForceVolMesh.faces_where_predicate
      ~ForceVolMesh.from_data
      ~ForceVolMesh.from_json
      ~ForceVolMesh.from_obj
      ~ForceVolMesh.from_pickle
      ~ForceVolMesh.from_vertices_and_cells
      ~ForceVolMesh.from_vertices_and_edges
      ~ForceVolMesh.get_any_edge
      ~ForceVolMesh.get_any_face
      ~ForceVolMesh.get_any_face_vertex
      ~ForceVolMesh.get_any_vertex
      ~ForceVolMesh.get_any_vertices
      ~ForceVolMesh.get_edge_attribute
      ~ForceVolMesh.get_edge_attributes
      ~ForceVolMesh.get_edges_attribute
      ~ForceVolMesh.get_edges_attributes
      ~ForceVolMesh.get_face_attribute
      ~ForceVolMesh.get_face_attributes
      ~ForceVolMesh.get_face_attributes_all
      ~ForceVolMesh.get_faces_attribute
      ~ForceVolMesh.get_faces_attributes
      ~ForceVolMesh.get_faces_attributes_all
      ~ForceVolMesh.get_vertex_attribute
      ~ForceVolMesh.get_vertex_attributes
      ~ForceVolMesh.get_vertices_attribute
      ~ForceVolMesh.get_vertices_attributes
      ~ForceVolMesh.gkey_key
      ~ForceVolMesh.halfface_area
      ~ForceVolMesh.halfface_cell
      ~ForceVolMesh.halfface_center
      ~ForceVolMesh.halfface_centroid
      ~ForceVolMesh.halfface_coordinates
      ~ForceVolMesh.halfface_edge_dependents
      ~ForceVolMesh.halfface_halfedges
      ~ForceVolMesh.halfface_normal
      ~ForceVolMesh.halfface_opposite_halfface
      ~ForceVolMesh.halfface_oriented_area
      ~ForceVolMesh.halfface_oriented_normal
      ~ForceVolMesh.halfface_vertex_ancestor
      ~ForceVolMesh.halfface_vertex_descendent
      ~ForceVolMesh.halfface_vertices
      ~ForceVolMesh.halffaces
      ~ForceVolMesh.halffaces_interior
      ~ForceVolMesh.halffaces_on_boundary
      ~ForceVolMesh.index_key
      ~ForceVolMesh.index_uv
      ~ForceVolMesh.insert_vertex
      ~ForceVolMesh.is_halfface_on_boundary
      ~ForceVolMesh.is_vertex_on_boundary
      ~ForceVolMesh.key_gkey
      ~ForceVolMesh.key_index
      ~ForceVolMesh.load
      ~ForceVolMesh.loads
      ~ForceVolMesh.number_of_cells
      ~ForceVolMesh.number_of_edges
      ~ForceVolMesh.number_of_faces
      ~ForceVolMesh.number_of_vertices
      ~ForceVolMesh.planes
      ~ForceVolMesh.scale
      ~ForceVolMesh.set_edge_attribute
      ~ForceVolMesh.set_edge_attributes
      ~ForceVolMesh.set_edges_attribute
      ~ForceVolMesh.set_edges_attributes
      ~ForceVolMesh.set_face_attribute
      ~ForceVolMesh.set_face_attributes
      ~ForceVolMesh.set_faces_attribute
      ~ForceVolMesh.set_faces_attributes
      ~ForceVolMesh.set_vertex_attribute
      ~ForceVolMesh.set_vertex_attributes
      ~ForceVolMesh.set_vertices_attribute
      ~ForceVolMesh.set_vertices_attributes
      ~ForceVolMesh.summary
      ~ForceVolMesh.to_data
      ~ForceVolMesh.to_json
      ~ForceVolMesh.to_obj
      ~ForceVolMesh.to_pickle
      ~ForceVolMesh.to_vertices_and_cells
      ~ForceVolMesh.update_default_edge_attributes
      ~ForceVolMesh.update_default_face_attributes
      ~ForceVolMesh.update_default_vertex_attributes
      ~ForceVolMesh.uv_index
      ~ForceVolMesh.vertex_cells
      ~ForceVolMesh.vertex_coordinates
      ~ForceVolMesh.vertex_halffaces
      ~ForceVolMesh.vertex_label_name
      ~ForceVolMesh.vertex_name
      ~ForceVolMesh.vertex_neighbors
      ~ForceVolMesh.vertex_normal
      ~ForceVolMesh.vertex_update_xyz
      ~ForceVolMesh.vertices
      ~ForceVolMesh.vertices_where
      ~ForceVolMesh.vertices_where_predicate
      ~ForceVolMesh.volmesh_edge_dependents_all
   
   

   
   
   .. rubric:: Attributes

   .. autosummary::
   
      ~ForceVolMesh.data
      ~ForceVolMesh.name
   
   