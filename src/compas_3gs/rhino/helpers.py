from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import json
from ast import literal_eval

import scriptcontext as sc

import compas_rhino
from compas_rhino.forms import TextForm

from compas_3gs.diagrams import FormNetwork
from compas_3gs.diagrams import ForceVolMesh


__all__ = [
    "is_valid_file",
    "select_filepath_open",
    "select_filepath_save",
    "get_tgs",
    "get_scene",
    "get_proxy",
    "get_system",
    "select_nodes",
    "select_vertices",
    "select_edges",
    "select_faces",
    "tgs_undo",
    "relocate_formdiagram"

]


def match_nodes(diagram, keys):
    temp = compas_rhino.get_objects(name="{}.node.*".format(diagram.name))
    names = compas_rhino.get_object_names(temp)
    guids = []
    for guid, name in zip(temp, names):
        parts = name.split('.')
        key = literal_eval(parts[2])
        if key in keys:
            guids.append(guid)
    return guids


def match_vertices(diagram, keys):
    temp = compas_rhino.get_objects(name="{}.vertex.*".format(diagram.name))
    names = compas_rhino.get_object_names(temp)
    guids = []
    for guid, name in zip(temp, names):
        parts = name.split('.')
        key = literal_eval(parts[2])
        if key in keys:
            guids.append(guid)
    return guids


def match_edges(diagram, keys):
    temp = compas_rhino.get_objects(name="{}.edge.*".format(diagram.name))
    names = compas_rhino.get_object_names(temp)
    guids = []
    for guid, name in zip(temp, names):
        parts = name.split('.')[2].split('-')
        u = literal_eval(parts[0])
        v = literal_eval(parts[1])
        if (u, v) in keys or (v, u) in keys:
            guids.append(guid)
    return guids


def match_faces(diagram, keys):
    temp = compas_rhino.get_objects(name="{}.face.*".format(diagram.name))
    names = compas_rhino.get_object_names(temp)
    guids = []
    for guid, name in zip(temp, names):
        parts = name.split('.')
        key = literal_eval(parts[2])
        if key in keys:
            guids.append(guid)
    return guids


def select_nodes(diagram, keys):
    guids = match_nodes(diagram, keys)
    compas_rhino.rs.EnableRedraw(False)
    compas_rhino.rs.SelectObjects(guids)
    compas_rhino.rs.EnableRedraw(True)


def select_vertices(diagram, keys):
    guids = match_vertices(diagram, keys)
    compas_rhino.rs.EnableRedraw(False)
    compas_rhino.rs.SelectObjects(guids)
    compas_rhino.rs.EnableRedraw(True)


def select_edges(diagram, keys):
    guids = match_edges(diagram, keys)
    compas_rhino.rs.EnableRedraw(False)
    compas_rhino.rs.SelectObjects(guids)
    compas_rhino.rs.EnableRedraw(True)


def select_faces(diagram, keys):
    guids = match_faces(diagram, keys)
    compas_rhino.rs.EnableRedraw(False)
    compas_rhino.rs.SelectObjects(guids)
    compas_rhino.rs.EnableRedraw(True)


def is_valid_file(filepath, ext):
    """Is the selected path a valid file.

    Parameters
    ----------
    filepath
    """
    if not filepath:
        return False
    if not os.path.exists(filepath):
        return False
    if not os.path.isfile(filepath):
        return False
    if not filepath.endswith(".{}".format(ext)):
        return False
    return True


def select_filepath_open(root, ext):
    """Select a filepath for opening a session.

    Parameters
    ----------
    root : str
        Base directory from where the file selection is started.
        If no directory is provided, the parent folder of the current
        Rhino document will be used
    ext : str
        The type of file that can be openend.

    Returns
    -------
    tuple
        The parent directory.
        The file name.
    None
        If the procedure fails.

    Notes
    -----
    The file extension is only used to identify the type of session file.
    Regardless of the provided extension, the file contents should be in JSON format.

    """
    ext = ext.split('.')[-1]
    filepath = compas_rhino.select_file(folder=root, filter=ext)
    if not is_valid_file(filepath, ext):
        print("This is not a valid session file: {}".format(filepath))
        return
    return filepath


def select_filepath_save(root, ext):
    """Select a filepath for saving a session."""
    filepath = compas_rhino.rs.SaveFileName('save', filter=ext, folder=root)
    if not filepath:
        return
    if filepath.split('.')[-1] != ext:
        filepath = "%s.%s" % (filepath, ext)
    return filepath


def get_tgs():
    if "3GS" not in sc.sticky:
        form = TextForm('Initialise the plugin first!', '3GS')
        form.show()
        return None
    return sc.sticky["3GS"]


def get_scene():
    tgs = get_tgs()
    if tgs:
        return tgs['scene']


def get_proxy():
    if "3GS.proxy" not in sc.sticky:
        form = TextForm('Initialise the plugin first!', '3GS')
        form.show()
        return None
    return sc.sticky["3GS.proxy"]


def get_system():
    if "3GS.system" not in sc.sticky:
        form = TextForm('Initialise the plugin first!', '3GS')
        form.show()
        return None
    return sc.sticky["3GS.system"]


def save_session():
    scene = get_scene()
    session = {
        "data": {"form": None, "force": None},
        "settings": scene.settings,
    }
    form = scene.get('form')[0]
    if form:
        session['data']['form'] = form.datastructure.to_data()
    force = scene.get('force')[0]
    if force:
        session['data']['force'] = force.datastructure.to_data()
    return session


def load_session(session):
    print("loading session")
    scene = get_scene()
    scene.clear()
    if 'settings' in session:
        scene.settings = session['settings']
    if 'data' in session:
        data = session['data']
        if 'form' in data and data['form']:
            form = FormNetwork.from_data(data['form'])
            scene.add(form, name="form")

        if 'force' in data and data['force']:
            force = ForceVolMesh.from_data(data['force'])
            force.primal = form
            form.dual = force
            force.update_angle_deviations()
            scene.add(force, name="force")
    scene.update()


def record():
    session = json.loads(json.dumps(save_session()))
    sc.sticky["3GS.sessions"] = sc.sticky["3GS.sessions"][:sc.sticky["3GS.sessions.current"] + 1]
    sc.sticky["3GS.sessions"].append(session)
    if len(sc.sticky["3GS.sessions"]) > 10:
        sc.sticky["3GS.sessions"] = sc.sticky["3GS.sessions"][-10:]
    sc.sticky["3GS.sessions.current"] = len(sc.sticky["3GS.sessions"]) - 1


def undo(sender, e):
    if e.Tag == "undo":
        if sc.sticky["3GS.sessions.current"] - 1 < 0:
            print("no more recorded sessions to undo")
            return
        sc.sticky["3GS.sessions.current"] -= 1
        session = sc.sticky["3GS.sessions"][sc.sticky["3GS.sessions.current"]]
        load_session(session)
        e.Document.AddCustomUndoEvent("RV2 Redo", undo, "redo")
    if e.Tag == "redo":
        if sc.sticky["3GS.sessions.current"] + 1 >= len(sc.sticky["3GS.sessions"]):
            print("no more recorded sessions to redo")
            return
        sc.sticky["3GS.sessions.current"] += 1
        session = sc.sticky["3GS.sessions"][sc.sticky["3GS.sessions.current"]]
        load_session(session)
        e.Document.AddCustomUndoEvent("RV2 Redo", undo, "undo")
    print("current sessions:", sc.sticky["3GS.sessions.current"] + 1)
    print("total sessions:", len(sc.sticky["3GS.sessions"]))


def tgs_undo(command):
    def wrapper(*args, **kwargs):
        sc.doc.EndUndoRecord(sc.doc.CurrentUndoRecordSerialNumber)
        undoRecord = sc.doc.BeginUndoRecord("RV2 Undo")
        if undoRecord == 0:
            print("undo record did not start")
        else:
            print("Custom undo recording", undoRecord)

        if len(sc.sticky["3GS.sessions"]) == 0:
            sc.sticky["3GS.sessions.current"] = 0
            record()
        command(*args, **kwargs)
        record()
        sc.doc.AddCustomUndoEvent("3GS Undo", undo, "undo")
        if undoRecord > 0:
            sc.doc.EndUndoRecord(undoRecord)
    return wrapper


def relocate_formdiagram(force, form):

    bbox_force = force.bounding_box()
    bbox_form = form.bounding_box()
    xmin_force, xmax_force = bbox_force[0][0], bbox_force[1][0]
    xmin_form, _ = bbox_form[0][0], bbox_form[1][0]
    ymin_force, ymax_force = bbox_force[0][1], bbox_force[3][1]
    ymin_form, ymax_form = bbox_form[0][1], bbox_form[3][1]
    y_force = ymin_force + 0.5 * (ymax_force - ymin_force)
    y_form = ymin_form + 0.5 * (ymax_form - ymin_form)
    dx = 1.5 * (xmax_force - xmin_force) + (xmin_force - xmin_form)
    dy = y_force - y_form

    return (dx, dy, 0)
