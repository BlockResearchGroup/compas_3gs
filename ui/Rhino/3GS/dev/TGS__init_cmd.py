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


__commandname__ = "TGS__init"


SETTINGS = {

    "3GS": {
        "show.angles": True,
        "show.forces": False,
        "tol.angles": 1.0,
        "tol.flatness": 0.1
    },

    "Solvers": {
        "reciprocation.kmax": 500,
        "reciprocation.alpha": 1.0,
        "reciprocation.tol": 0.01,
        "reciprocation.refreshrate": 10,

        "planarization.kmax": 500,
        "planarization.tol": 0.01,
        "planarization.refreshrate": 10,

        "arearization.kmax": 500,
        "arearization.tol": 0.01,
        "arearization.refreshrate": 10,

    }
}


HERE = compas_rhino.get_document_dirname()
HOME = os.path.expanduser('~')
CWD = HERE or HOME


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
