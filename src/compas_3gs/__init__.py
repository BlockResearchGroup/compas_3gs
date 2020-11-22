"""
********************************************************************************
compas_3gs
********************************************************************************

.. currentmodule:: compas_3gs

.. toctree::
    :maxdepth: 1

    compas_3gs.algorithms
    compas_3gs.datastructures
    compas_3gs.diagrams
    compas_3gs.operations
    compas_3gs.rhino
    compas_3gs.utilities

"""

from __future__ import print_function

import os


__author__    = ['Juney Lee', ]
__copyright__ = 'Copyright 2018 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'juney.lee@arch.ethz.ch'

__version__ = '0.2.5'


HERE = os.path.dirname(__file__)
HOME = os.path.abspath(os.path.join(HERE, '../..'))
DATA = os.path.abspath(os.path.join(HERE, '../../data'))
TEMP = os.path.abspath(os.path.join(HERE, '../../temp'))

__all__ = []
