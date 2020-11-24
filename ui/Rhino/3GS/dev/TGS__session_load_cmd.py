from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import json

import scriptcontext as sc

import compas_rhino

from compas.utilities import DataDecoder


from compas_3gs.diagrams import ForceVolMesh
from compas_3gs.diagrams import FormNetwork

__commandname__ = "TGS__session_load"


def RunCommand(is_interactive):

    if '3GS' not in sc.sticky:
        compas_rhino.display_message('3GS has not been initialised yet.')
        return

    system = sc.sticky['3GS']['system']
    scene = sc.sticky['3GS']['scene']

    filepath = compas_rhino.select_file(folder=system['session.dirname'], filter=system['session.extension'])

    if not filepath:
        return
    if not os.path.exists(filepath):
        return
    if not os.path.isfile(filepath):
        return
    if not filepath.endswith(".{}".format(system['session.extension'])):
        return

    dirname, basename = os.path.split(filepath)
    filename, extension = os.path.splitext(basename)

    system['session.dirname'] = dirname
    system['session.filename'] = filename

    with open(filepath, "r") as f:
        session = json.load(f, cls=DataDecoder)

    if not session['data']['force']:
        compas_rhino.display_message('The session file has no force diagram.')

    forcediagram = ForceVolMesh.from_data(session['data']['force'])

    force_id = scene.add_forcevolmesh(forcediagram, name='force', layer='3GS::ForceDiagram')
    force = scene.find(force_id)

    if 'settings' in session['scene']['force']:
        force.settings.update(session['scene']['force']['settings'])

    if 'anchor' in session['scene']['force']:
        force.anchor = session['scene']['force']['anchor']

    if 'location' in session['scene']['force']:
        force.location = session['scene']['force']['location']

    if 'scale' in session['scene']['form']:
        force.scale = session['scene']['force']['scale']

    

    if session['data']['form']:

        formdiagram = FormNetwork.from_data(session['data']['form'])

        form_id = scene.add_formnetwork(formdiagram, name='form', layer='3GS::FormDiagram')
        form = scene.find(form_id)

        forcediagram.primal = formdiagram
        formdiagram.dual = forcediagram

        if 'settings' in session['scene']['form']:
            form.settings.update(session['scene']['form']['settings'])

        if 'anchor' in session['scene']['form']:
            form.anchor = session['scene']['form']['anchor']

        if 'location' in session['scene']['form']:
            form.location = session['scene']['form']['location']

        if 'scale' in session['scene']['form']:
            form.scale = session['scene']['form']['scale']


    scene.update()
    scene.save()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
