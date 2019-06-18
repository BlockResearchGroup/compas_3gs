********************************************************************************
Datastructure
********************************************************************************

A polyhedral cell which is typically used for the representation of a global
force polyhedron :math:`\Lambda^{\perp}`, is modelled as a ``mesh``.
The initial form diagram :math:`\Lambda`, which contains the information of the magnitudes and locations of the external forces, are typically a disconnected set of vectors or "lines" in space.
These vectors can be moved to one location such that the heads of the
vectors are coincident.
The consolidated vectors then can be modelled as a ``network``, where each external force is represented with an edge.

.. figure:: ../../_images/04_datastructures_01_cell.jpg
    :width: 100%

|

----

|

The topology and geometry of a polyhedral cell can be represented by a ``mesh``, which is based on a halfedge datastructure that stores incidenceinformation of vertices, edges and faces.
Each edge of a mesh is decomposed into two halfedges with opposite directions.
Each halfedge stores the information of the face that it belongs to.
Using the halfedge directions and incident face information, various data of the mesh can be accessed and traversed.
The data of a ``mesh`` thus consists of vertices, faces and halfedges.

For a detiled overview of the ``mesh`` datastructure, please refer to this page `page <https://compas-dev.github.io/main/tutorials/meshes.html>`_ of the online documentation of COMPAS.

.. figure:: ../../_images/compas_3gs_datastructure_mesh.jpg
    :width: 100%