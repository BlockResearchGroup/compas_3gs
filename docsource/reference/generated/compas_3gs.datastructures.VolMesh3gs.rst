compas\_3gs.datastructures.VolMesh3gs
=====================================

.. currentmodule:: compas_3gs.datastructures

.. autoclass:: VolMesh3gs

   
   .. automethod:: __init__

   
   .. rubric:: Methods

   .. autosummary::
   
      ~VolMesh3gs.__init__
      ~VolMesh3gs.add_cell
      ~VolMesh3gs.add_halfface
      ~VolMesh3gs.add_vertex
      ~VolMesh3gs.bounding_box
      ~VolMesh3gs.cell_center
      ~VolMesh3gs.cell_centroid
      ~VolMesh3gs.cell_edges
      ~VolMesh3gs.cell_halfedges
      ~VolMesh3gs.cell_halffaces
      ~VolMesh3gs.cell_neighbors
      ~VolMesh3gs.cell_pair_halffaces
      ~VolMesh3gs.cell_to_mesh
      ~VolMesh3gs.cell_to_vertices_and_halffaces
      ~VolMesh3gs.cell_tree
      ~VolMesh3gs.cell_vertex_delete
      ~VolMesh3gs.cell_vertex_halffaces
      ~VolMesh3gs.cell_vertex_neighbors
      ~VolMesh3gs.cell_vertices
      ~VolMesh3gs.cells
      ~VolMesh3gs.centroid
      ~VolMesh3gs.clean
      ~VolMesh3gs.clear
      ~VolMesh3gs.clear_celldict
      ~VolMesh3gs.clear_edges
      ~VolMesh3gs.clear_faces
      ~VolMesh3gs.clear_halffacedict
      ~VolMesh3gs.clear_vertexdict
      ~VolMesh3gs.copy
      ~VolMesh3gs.cull_edges
      ~VolMesh3gs.cull_halffaces
      ~VolMesh3gs.cull_vertices
      ~VolMesh3gs.delete_cell
      ~VolMesh3gs.delete_halfface
      ~VolMesh3gs.delete_vertex
      ~VolMesh3gs.draw
      ~VolMesh3gs.draw_edge_labels
      ~VolMesh3gs.draw_edges
      ~VolMesh3gs.draw_face_labels
      ~VolMesh3gs.draw_faces
      ~VolMesh3gs.draw_vertex_labels
      ~VolMesh3gs.draw_vertices
      ~VolMesh3gs.dump
      ~VolMesh3gs.dumps
      ~VolMesh3gs.edge_cells
      ~VolMesh3gs.edge_coordinates
      ~VolMesh3gs.edge_direction
      ~VolMesh3gs.edge_halffaces
      ~VolMesh3gs.edge_label_name
      ~VolMesh3gs.edge_length
      ~VolMesh3gs.edge_midpoint
      ~VolMesh3gs.edge_name
      ~VolMesh3gs.edge_point
      ~VolMesh3gs.edge_vector
      ~VolMesh3gs.edges
      ~VolMesh3gs.edges_where
      ~VolMesh3gs.edges_where_predicate
      ~VolMesh3gs.face_center
      ~VolMesh3gs.face_coordinates
      ~VolMesh3gs.face_label_name
      ~VolMesh3gs.face_name
      ~VolMesh3gs.faces
      ~VolMesh3gs.faces_interior
      ~VolMesh3gs.faces_where
      ~VolMesh3gs.faces_where_predicate
      ~VolMesh3gs.from_data
      ~VolMesh3gs.from_json
      ~VolMesh3gs.from_obj
      ~VolMesh3gs.from_pickle
      ~VolMesh3gs.from_vertices_and_cells
      ~VolMesh3gs.from_vertices_and_edges
      ~VolMesh3gs.get_any_edge
      ~VolMesh3gs.get_any_face
      ~VolMesh3gs.get_any_face_vertex
      ~VolMesh3gs.get_any_vertex
      ~VolMesh3gs.get_any_vertices
      ~VolMesh3gs.get_edge_attribute
      ~VolMesh3gs.get_edge_attributes
      ~VolMesh3gs.get_edges_attribute
      ~VolMesh3gs.get_edges_attributes
      ~VolMesh3gs.get_face_attribute
      ~VolMesh3gs.get_face_attributes
      ~VolMesh3gs.get_face_attributes_all
      ~VolMesh3gs.get_faces_attribute
      ~VolMesh3gs.get_faces_attributes
      ~VolMesh3gs.get_faces_attributes_all
      ~VolMesh3gs.get_vertex_attribute
      ~VolMesh3gs.get_vertex_attributes
      ~VolMesh3gs.get_vertices_attribute
      ~VolMesh3gs.get_vertices_attributes
      ~VolMesh3gs.gkey_key
      ~VolMesh3gs.halfface_area
      ~VolMesh3gs.halfface_cell
      ~VolMesh3gs.halfface_center
      ~VolMesh3gs.halfface_centroid
      ~VolMesh3gs.halfface_coordinates
      ~VolMesh3gs.halfface_edge_dependents
      ~VolMesh3gs.halfface_halfedges
      ~VolMesh3gs.halfface_normal
      ~VolMesh3gs.halfface_opposite_halfface
      ~VolMesh3gs.halfface_oriented_area
      ~VolMesh3gs.halfface_oriented_normal
      ~VolMesh3gs.halfface_vertex_ancestor
      ~VolMesh3gs.halfface_vertex_descendent
      ~VolMesh3gs.halfface_vertices
      ~VolMesh3gs.halffaces
      ~VolMesh3gs.halffaces_interior
      ~VolMesh3gs.halffaces_on_boundary
      ~VolMesh3gs.index_key
      ~VolMesh3gs.index_uv
      ~VolMesh3gs.insert_vertex
      ~VolMesh3gs.is_halfface_on_boundary
      ~VolMesh3gs.is_vertex_on_boundary
      ~VolMesh3gs.key_gkey
      ~VolMesh3gs.key_index
      ~VolMesh3gs.load
      ~VolMesh3gs.loads
      ~VolMesh3gs.number_of_cells
      ~VolMesh3gs.number_of_edges
      ~VolMesh3gs.number_of_faces
      ~VolMesh3gs.number_of_vertices
      ~VolMesh3gs.planes
      ~VolMesh3gs.scale
      ~VolMesh3gs.set_edge_attribute
      ~VolMesh3gs.set_edge_attributes
      ~VolMesh3gs.set_edges_attribute
      ~VolMesh3gs.set_edges_attributes
      ~VolMesh3gs.set_face_attribute
      ~VolMesh3gs.set_face_attributes
      ~VolMesh3gs.set_faces_attribute
      ~VolMesh3gs.set_faces_attributes
      ~VolMesh3gs.set_vertex_attribute
      ~VolMesh3gs.set_vertex_attributes
      ~VolMesh3gs.set_vertices_attribute
      ~VolMesh3gs.set_vertices_attributes
      ~VolMesh3gs.summary
      ~VolMesh3gs.to_data
      ~VolMesh3gs.to_json
      ~VolMesh3gs.to_obj
      ~VolMesh3gs.to_pickle
      ~VolMesh3gs.to_vertices_and_cells
      ~VolMesh3gs.update_default_edge_attributes
      ~VolMesh3gs.update_default_face_attributes
      ~VolMesh3gs.update_default_vertex_attributes
      ~VolMesh3gs.uv_index
      ~VolMesh3gs.vertex_cells
      ~VolMesh3gs.vertex_coordinates
      ~VolMesh3gs.vertex_halffaces
      ~VolMesh3gs.vertex_label_name
      ~VolMesh3gs.vertex_name
      ~VolMesh3gs.vertex_neighbors
      ~VolMesh3gs.vertex_normal
      ~VolMesh3gs.vertex_update_xyz
      ~VolMesh3gs.vertices
      ~VolMesh3gs.vertices_where
      ~VolMesh3gs.vertices_where_predicate
      ~VolMesh3gs.volmesh_edge_dependents_all
   
   

   
   
   .. rubric:: Attributes

   .. autosummary::
   
      ~VolMesh3gs.data
      ~VolMesh3gs.name
   
   