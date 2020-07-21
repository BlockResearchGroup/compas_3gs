from __future__ import print_function
from __future__ import absolute_import
from __future__ import division


__author__    = 'Juney Lee'
__copyright__ = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'juney.lee@arch.ethz.ch'


__all__ = ['golden_section_search']


def golden_section_search(function, a, b, tol=1e-3):
    """Golden section search algorithm for finding the minimum or maximum of a strictly unimodal function 
    by successively narrowing the range of values inside which the extremum is known to exist.

    Parameters
    ----------
    function : Function
        Evaluation function.
    a : float
        Lower bound of the initial search interval.
    b : float
        Upper bound of the initial search interval.
    tol : float, optional
        A tolerance for convergence.
        Default is ``1e-6``.

    Returns
    -------
    float
        The minimum or maximum value.

    Notes
    -----
    Adapted after [1]_.

    References
    ----------
    .. [1] Wikipedia *Golden section search*.
           Available at: https://en.wikipedia.org/wiki/Golden-section_search

    .. [2] Kiefer, J. (1953). Sequential minimax search for a maximum. In *Proceedings of the American Mathematical Society* 4(3).

    """

    gr = (5 ** 0.5 + 1) / 2

    c  = b - (b - a) / gr
    d  = a + (b - a) / gr

    while abs(c - d) > tol:

        if function(c) < function(d):
            b = d

        else:
            a = c

        c = b - (b - a) / gr
        d = a + (b - a) / gr

    return (b + a) / 2


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   Main
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


if __name__ == '__main__':
    pass
