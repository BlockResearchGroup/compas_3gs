********************************************************************************
Datastructures
********************************************************************************

Form and force diagrams used in ``compas_3gs`` are represented using one or combinations of the three main datastructures of the **COMPAS** framework.

A ``network`` is a directed graph, made up of a finite set of vertices, which are connected by a finite set of edges.
In mathematics, graphs are abstract topological datastructures used to model and depict relationships between pairs of objects.
In ``compas``, the geometry of a network is defined by adding xyz coordinate information to each of the vertices.
A ``network`` can be 2D on a plane, or 3D in space.
By default, a ``network`` does not carry any face information.

A ``mesh`` is a network of faces, which has a halfedge datastructure.
A ``mesh`` can be open with boundary edges (polyhedral mesh or surface), or closed without any boundary edges.
As implemented in ``compas``, a ``mesh`` is strictly a 2-manifold; an edge is shared by no more than two faces.
In essence, a ``mesh`` is a ``network`` with vertices and edges, with the addition of face information.
The edges of a mesh are directed, although the directions of the edges are arbitrary and not used for querying or traversing the datastructure.
A face of a ``mesh`` is defined by an ordered list of vertices, and need not necessarily be planar (flat) in its geometry.

A ``volmesh`` is a 3-manifold volumetric mesh; an edge of a volmesh can
be shared by more than two faces.
Embedded within this volumetric mesh is a network of cells, where the cell-to-cell relationships are defined by a combination of halffaces and planes.
Similar to a ``network`` or ``mesh``, a ``volmesh`` has a finite set of vertices and edges.
The edges of a volmesh are directed, although the directions of the edges are arbitrary and not used for querying or traversing the datastructure.
Whereas every edge of a ``mesh`` is split into two halfedges, every face of a ``volmesh`` is split into two halffaces.
Because the edge directions are arbitrary, a face of a ``volmesh`` does not have a winding direction.
Locally, each cell of a ``volmesh`` is structured like a ``mesh``.


For a more detailed documentation of these datastructures, please visit the of `online documentation <https://compas-dev.github.io/>`_ of the **COMPAS** framework.


.. figure:: ../_images/compas_3gs_datastructure_definitions.jpg
    :width: 100%
