********************************************************************************
Motivation
********************************************************************************

Lack of computational framework for 3D graphic statics
======================================================

Despite its benefits for both academic research and professional architecture and structural engineering practices, there currently exists no general computational design framework for 3D graphic statics.
New publications of graphic statics are often stand-alone implementations with their own set of conventions, computational languages and software dependencies, which make them incompatible or unusable by other researchers.
New knowledge is often shared through papers in physical or digital formats that describe the computational implementations with text and static images without actually delivering any computational means to the readers.
A new researcher who is interested in 3D graphic statics must start his or her implementation from scratch, unless he or she joins a research group with an established computational framework.
The lack of a unifying platform or computational environment for graphic statics makes it difficult to start new strands of research or continue existing ones.

The development of ``compas_3gs`` was motivated by this issue, and intended to be an open-source computational framework which will make 3D graphic statics available to a wider audience.
It is designed to be a sharing platform and a common computational langugage through which future researchers can conduct their own research and experiments, communicate with one another, exchange their latest discoveries and collaborate on joint research projects.
``compas_3gs`` is not meant to be an end result or a finalised computational package.
Rather, it is meant to be the starting point and the initial basic kit of parts for 3D graphic statics, which works out of the box for users of all experience levels and background.
The ultimate hope is to encourage contributions to ``compas_3gs`` from various individuals and institutions over time, which will help expand, diversify and enrich the field of 3D graphic statics.

|

.. figure:: ../_images/01_gs_papers.jpg
    :width: 100%

    Some of the notable publications related to graphic statics (circa 2017).

----

Advent of research in graphic statics
=====================================

In recent years, there has been a rise of interest and research within the field of graphic statics.
This is mainly due to the new design and research possibilities that arise when graphic statics is combined with advanced parametric and computer-aided design (CAD) software, which are readily available today.
The three-dimensional modelling capabilities of most CAD software used in architectural design allows structural design explorations using 3D graphic statics based on polyhedral reciprocal diagrams, which was challenging with 2D drafting tools or software.

Over the past three decades, the annual number of publications written in English on graphic statics have increased at an almost exponential rate.
Although the origins of graphic statics date back to the 18th century, computational graphic statics and 3D graphic statics in particular, are new emerging areas of research with countless design and research opportunities yet to be discovered.

|

.. figure:: ../_images/01_gs_citation_history_tall.jpg
    :width: 100%

    History of graphic-statics-related publications in English by year. Some of the notable publications on Goolge Scholar that are relevant to ``compas_3gs`` from the past three decades are highlighted.
