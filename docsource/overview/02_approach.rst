********************************************************************************
compas_3gs
********************************************************************************

About
=====

``compas_3gs`` is an additional package for the `COMPAS <https://compas-dev.github.io/>`_ framework.
**COMPAS** is an open-source, Python-based computational
framework for collaboration and research in architecture, engineering and
digital fabrication.
``compas``, the main library of the **COMPAS** framework,
contains all of the basic datastructures, algorithms, utilities and functionality.
Building on this core library, ``compas_3gs`` provides additional features that are specifically geared towards 3D graphic statics applications.
Developed entirely independent of the functionality of CAD software, ``compas_3gs`` can be used on different platforms and in combination with
external software and libraries.
It can also take advantage of the extensive libraries for design and research that are widely available in the Python ecosystem.
Because it is not dependent on any other software, ``compas_3gs`` in combination with ``compas``, is intended to bring 3D graphic statics to a wide audience with diverse range of academic backgrounds, expertise and experience.

|

.. figure:: ../_images/compas_3gs_bw.jpg
    :width: 100%

----

General approach
================

The functionalities and algorithms of ``compas_3gs`` are mainly based on transparent, geometry-based solvers and optimisation techniques as opposed to “black-box,” numerical methods.
``compas_3gs`` is developed with the following goals in mind:

|

**1. Flexibility**

The implementation needs to be general and flexible enough to cover a wide range of both known and unknown structural typologies.
It also needs to have as few software dependencies as possible, so that users from a variety of backgrounds and expertise can adapt the library for various applications regardless of the CAD software being used.

|

**2. Simplicity**

In computational geometry, improvement of the computational efficiency of solving procedures and algorithms are often prioritised over the user’s ability to modify and interact with the resulting solutions.
Instead of focusing on computing the absolute solution in the shortest amount of time possible, the solution as well as the procedure should communicate complex information in simple ways that are easy to understand and potentially provide meaningful insights.

|

**3. Customisability**

During early stages of design, it may be desirable to explore multiple
feasible solutions as rapidly as possible while meeting the requirements
that are specific to the design problem at hand.
This requires a set of flexible yet robust functions and operations, which can be easily mix-and-matched to create customised toolbars and workflows that are
tailored for the needs of the user.

|

**4. Open source**

``compas_3gs`` is developed as an open-source library, encouraging researchers from a wide range of disciplines and expertise to make contributions that all users can benefit from.
In order to incentivise the researchers to contribute their work, each contribution to ``compas_3gs`` is treated like a publication which can be cited and referenced.