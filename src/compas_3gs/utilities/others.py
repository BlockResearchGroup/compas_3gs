from __future__ import print_function
from __future__ import absolute_import
from __future__ import division


__all__ = ['print_result']


def print_result(name, k, deviation):
    """Prints the result of an algorithm.

    Parameters
    ----------
    name : string
        name of the algorithm
    k : int
        number of iterations
    deviation : float
        deviation

    """
    name = str(name)

    print('===================================================================')
    print('')
    print(name, 'ended after', k, 'iterations.')
    print('')
    print('Max deviation :', deviation)
    print('')
    print('===================================================================')
