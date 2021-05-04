********************************************************************************
Constructor
********************************************************************************

A single polyhedral cell can be constructed from a set of equilibrated force vectors.
In some cases, it may be convenient to use closed Rhino polysurfaces (solid) to build the ``volmesh`` representing a multi-cell polyhedron.
It is also possible for a ``volmesh`` to have just one cell.

|

----

Example
=======


|

.. raw:: html

    <div class="card bg-light">
    <div class="card-body">
    <div class="card-title">Download</div>

* :download:`volmesh_cubes_4x4.3dm <../../../examples/rhino_files/volmesh_cubes_4x4.3dm>`

.. raw:: html

    </div>
    </div>


.. literalinclude:: ../../../examples/01_10_volmesh_constructor.py
    :language: python