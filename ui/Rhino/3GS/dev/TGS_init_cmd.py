from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import errno
import shelve

import scriptcontext as sc

import compas
import compas_rhino

from compas_3gs.rhino import Scene
# from compas_3gs.web import Browser


__commandname__ = "TGS_init"


HERE = compas_rhino.get_document_dirname()
HOME = os.path.expanduser('~')
CWD = HERE or HOME


SETTINGS = {

    "3GS": {
        "show.forces": False,
    },

    "Solvers": {
        "reciprocation.kmax": 500,
        "reciprocation.tol": 0.01,
        "reciprocation.refreshrate": 10,

        "planarisation.kmax": 500,
        "planarisation.tol": 0.01,
        "planarisation.refreshrate": 10,

        "arearisation.kmax": 500,
        "arearisation.tol": 0.01,
        "arearisation.refreshrate": 10,
    }
}


def RunCommand(is_interactive):

    shelvepath = os.path.join(compas.APPTEMP, '3GS', '.history')
    if not os.path.exists(os.path.dirname(shelvepath)):
        try:
            os.makedirs(os.path.dirname(shelvepath))
        except OSError as error:
            if error.errno != errno.EEXIST:
                raise

    db = shelve.open(shelvepath, 'n')
    db['states'] = []

    scene = Scene(db, 20, SETTINGS)
    scene.purge()

    sc.sticky["3GS"] = {
        'system': {
            "session.dirname": CWD,
            "session.filename": None,
            "session.extension": '3gs'
        },
        'scene': scene,
    }

    scene.update()

    # Browser()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
