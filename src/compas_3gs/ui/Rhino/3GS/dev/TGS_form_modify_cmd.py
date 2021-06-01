from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino


__commandname__ = "TGS_form_modify"


def RunCommand(is_interactive):

    sc.doc.EndUndoRecord(sc.doc.CurrentUndoRecordSerialNumber)

    if '3GS' not in sc.sticky:
        compas_rhino.display_message('3GS has not been initialised yet.')
        return

    scene = sc.sticky['3GS']['scene']
    if not scene:
        return

    scene.update()
    scene.save()

# ==============================================================================
# Main
# ==============================================================================


if __name__ == '__main__':

    RunCommand(True)
