********************************************************************************
Test example 2
********************************************************************************

.. image:: images/theblock.jpg

.. image:: images/theblock.jpg

.. code-block:: python

    import compas
    from compas.datastructures import Mesh

.. plot::
    :include-source:

    import compas
    from compas.datastructures import Mesh
    from compas.plotters import MeshPlotter

    mesh = Mesh.from_obj(compas.get('faces.obj'))

    plotter = MeshPlotter(mesh)
    plotter.draw_vertices()
    plotter.draw_edges()
    plotter.draw_faces()
    plotter.show()

.. literalinclude:: /_examples/test.py

