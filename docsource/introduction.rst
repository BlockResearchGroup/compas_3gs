********************************************************************************
Introduction
********************************************************************************


.. image:: _images/compas_3gs_bw.jpg
   :width: 100 %

|

``compas_3gs`` is a 3D graphic statics add-on package for the **COMPAS** framework.

Graphic statics is a graphical method of analysis and design of structures using reciprocal form and force diagrams.
Computational graphic statics is a powerful design tool that automates the drawing process of the reciprocal diagrams.
It also enables dynamic interaction and bi-directional control of both the geometry of form and internal forces of a structure, while providing a real-time, visual feedback.

In 2D graphic statics, the planar equilibrium of forces at a node of a structure is represented by a closed force polygon.
In 3D graphic statics, the spatial equilibrium of forces at a node of a structure is represented by a closed force polyhedron.
As structures become more complex, so does the topology and geometry of its force polyhedra.
Conventional CAD tools are limited in its functions and visualisation methods to allow sufficient handling and modelling of polyhedral geometries.

The ``compas_3gs`` package provides the necessary datastructures, functionalities, algorithms and visualisation tools for a wide range of 3D graphic statics applications.
Using the ``network``, ``mesh`` and ``volmesh`` datastructures, this packages aids the user in setting up and initialising polyhedral reciprocal diagrams.
Various algorithms allow precise control and transformation of the polyhedral form and force diagrams.
Most importantly, the legibility and usability of the polyhedral reciprocal diagrams are maximised through various visualisation functionalities to provide the user with new design insights, which is one of the most rewarding inherent benefits of graphic statics.