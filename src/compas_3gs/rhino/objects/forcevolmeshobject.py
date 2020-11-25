from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.utilities import i_to_rgb

import compas_rhino

from compas_3gs.rhino.objects.volmeshobject import VolMeshObject

from compas_3gs.utilities import volmesh_face_flatness


__all__ = ['ForceVolMeshObject']


class ForceVolMeshObject(VolMeshObject):
    """A force volmesh object represents a polyhedral force diagram in the Rhino view.
    """

    SETTINGS = {
        'layer': "3GS::ForceDiagram",

        '_is.valid': False,

        'show.vertices': True,
        'show.edges': True,
        'show.faces': True,
        'show.vertexlabels': False,
        'show.facelabels': False,
        'show.celllabels': False,

        'color.invalid': (100, 255, 100),

        'color.vertices': (0, 0, 0),
        'color.vertexlabels': (255, 255, 255),
        'color.vertices:is_fixed': (0, 0, 255),

        'color.edges': (50, 50, 50),
        'color.edgelabels': (0, 0, 0),

        'color.faces': (200, 200, 200),
        'color.facelabels': (200, 200, 200),

        'color.celllabels': (0, 0, 255)
    }

    def __init__(self, diagram, *args, **kwargs):
        super(ForceVolMeshObject, self).__init__(diagram, *args, **kwargs)
        self.settings.update(ForceVolMeshObject.SETTINGS)
        settings = kwargs.get('settings') or {}
        if settings:
            self.settings.update(settings)

    def check_eq(self):
        ftol = self.scene.settings['3GS']['tol.flatness']
        fmax = max(volmesh_face_flatness(self.diagram).values())

        atol = self.scene.settings['3GS']['tol.angles']
        halffaces = list(self.diagram.faces())
        amax = max(self.diagram.faces_attribute('_a', faces=halffaces))

        if fmax > ftol or amax > atol:
            self.settings['_is.valid'] = False
        if fmax < ftol and amax < atol:
            self.settings['_is.valid'] = True

    # @property
    # def vertex_xyz(self):
    #     """dict : The view coordinates of the mesh object."""
    #     origin = Point(0, 0, 0)
    #     if self.anchor is not None:
    #         xyz = self.volmesh.vertex_attributes(self.anchor, 'xyz')
    #         point = Point(* xyz)
    #         T1 = Translation.from_vector(origin - point)
    #         S = Scale.from_factors([self.scale] * 3)
    #         R = Rotation.from_euler_angles(self.rotation)
    #         T2 = Translation.from_vector(self.location)
    #         X = T2 * R * S * T1
    #     else:
    #         S = Scale.from_factors([self.scale] * 3)
    #         R = Rotation.from_euler_angles(self.rotation)
    #         T = Translation.from_vector(self.location)
    #         X = T * R * S
    #     volmesh = self.volmesh.transformed(X)
    #     vertex_xyz = {vertex: volmesh.vertex_attributes(vertex, 'xy') + [0.0] for vertex in volmesh.vertices()}
    #     return vertex_xyz
    # # --------------------------------------------------------------------------
    # #   attributes
    # # --------------------------------------------------------------------------

    # def update_attributes(self):
    #     """Update the attributes of the data structure through a Rhino dialog.

    #     Returns
    #     -------
    #     bool
    #         True if the update was successful.
    #         False otherwise.
    #     """
    #     return compas_rhino.update_settings(self.datastructure.attributes)

    # def update_vertices_attributes(self, keys, names=None):
    #     """Update the attributes of selected vertices.

    #     Parameters
    #     ----------
    #     keys : list
    #         The identifiers of the vertices of which the attributes should be updated.
    #     names : list, optional
    #         The names of the attributes that should be updated.
    #         Default is ``None``, in which case all attributes are updated.

    #     Returns
    #     -------
    #     bool
    #         True if the update was successful.
    #         False otherwise.
    #     """
    #     if keys:
    #         compas_rhino.rs.UnselectAllObjects()
    #         select_vertices(self.datastructure, keys)
    #         return mesh_update_vertex_attributes(self.datastructure, keys, names)

    # def update_edges_attributes(self, keys, names=None):
    #     """Update the attributes of selected edges.

    #     Parameters
    #     ----------
    #     keys : list
    #         The identifiers of the edges of which the attributes should be updated.
    #     names : list, optional
    #         The names of the attributes that should be updated.
    #         Default is ``None``, in which case all attributes are updated.

    #     Returns
    #     -------
    #     bool
    #         True if the update was successful.
    #         False otherwise.
    #     """
    #     if keys:
    #         compas_rhino.rs.UnselectAllObjects()
    #         select_edges(self.datastructure, keys)
    #         return mesh_update_edge_attributes(self.datastructure, keys, names)

    # def update_faces_attributes(self, keys, names=None):
    #     """Update the attributes of selected faces.

    #     Parameters
    #     ----------
    #     keys : list
    #         The identifiers of the faces of which the attributes should be updated.
    #     names : list, optional
    #         The names of the attributes that should be updated.
    #         Default is ``None``, in which case all attributes are updated.

    #     Returns
    #     -------
    #     bool
    #         True if the update was successful.
    #         False otherwise.
    #     """
    #     if keys:
    #         compas_rhino.rs.UnselectAllObjects()
    #         select_faces(self.datastructure, keys)
    #         return mesh_update_face_attributes(self.datastructure, keys, names)

    # --------------------------------------------------------------------------
    #   drawing
    # --------------------------------------------------------------------------

    def draw(self):
        """Draw the objects representing the force diagram.
        """
        layer = self.settings["layer"]
        self.artist.layer = layer
        self.artist.clear_layer()
        self.clear()
        if not self.visible:
            return

        self.artist.vertex_xyz = self.vertex_xyz

        # ======================================================================
        # Groups
        # ======================================================================

        group_vertices = "{}::vertices".format(layer)
        group_vertices_labels = "{}::vertices_labels".format(layer)
        group_edges = "{}::edges".format(layer)
        group_edges_labels = "{}::edges_labels".format(layer)
        group_halffaces = "{}::halffaces".format(layer)
        group_halffaces_labels = "{}::halffaces_labels".format(layer)
        group_cells_labels = "{}::cells_labels".format(layer)
        group_angles = "{}::angles".format(layer)

        if not compas_rhino.rs.IsGroup(group_vertices):
            compas_rhino.rs.AddGroup(group_vertices)

        if not compas_rhino.rs.IsGroup(group_vertices_labels):
            compas_rhino.rs.AddGroup(group_vertices_labels)

        if not compas_rhino.rs.IsGroup(group_edges):
            compas_rhino.rs.AddGroup(group_edges)

        if not compas_rhino.rs.IsGroup(group_edges_labels):
            compas_rhino.rs.AddGroup(group_edges_labels)

        if not compas_rhino.rs.IsGroup(group_halffaces):
            compas_rhino.rs.AddGroup(group_halffaces)

        if not compas_rhino.rs.IsGroup(group_halffaces_labels):
            compas_rhino.rs.AddGroup(group_halffaces_labels)

        if not compas_rhino.rs.IsGroup(group_cells_labels):
            compas_rhino.rs.AddGroup(group_cells_labels)

        if not compas_rhino.rs.IsGroup(group_angles):
            compas_rhino.rs.AddGroup(group_angles)

        # ======================================================================
        # vertices
        # ======================================================================

        # vertices -------------------------------------------------------------
        vertices = list(self.diagram.vertices())
        vertices_color = {}
        vertices_labels_color = {}

        for vertex in vertices:
            if self.diagram.vertex_attribute(vertex, 'is_fixed'):
                vertices_color[vertex] = self.settings['color.vertices:is_fixed']
                vertices_labels_color[vertex] = self.settings['color.vertices:is_fixed']
            else:
                vertices_color[vertex] = self.settings['color.vertices']
                vertices_labels_color[vertex] = self.settings['color.vertexlabels']

        guids = self.artist.draw_vertices(color=vertices_color)
        self.guid_vertex = zip(guids, vertices)
        compas_rhino.rs.AddObjectsToGroup(guids, group_vertices)

        if self.settings["show.vertices"] and self.settings['_is.valid']:
            compas_rhino.rs.ShowGroup(group_vertices)
        else:
            compas_rhino.rs.HideGroup(group_vertices)

        # vertices labels ------------------------------------------------------
        if self.settings["show.vertexlabels"] and self.settings['_is.valid']:
            text = {vertex: index for index, vertex in enumerate(vertices)}
            guids = self.artist.draw_vertexlabels(text=text, color=vertices_labels_color)
            self.guid_vertexlabel = zip(guids, vertices)
            compas_rhino.rs.AddObjectsToGroup(guids, group_vertices_labels)

            compas_rhino.rs.ShowGroup(group_vertices_labels)
        else:
            compas_rhino.rs.HideGroup(group_vertices_labels)

        # ======================================================================
        # edges
        # ======================================================================

        # edges ----------------------------------------------------------------
        edges = list(self.diagram.edges())
        color = {edge: self.settings['color.edges'] if self.settings['_is.valid'] else self.settings['color.invalid'] for edge in edges}

        guids = self.artist.draw_edges(edges, color)
        self.guid_edge = zip(guids, edges)
        compas_rhino.rs.AddObjectsToGroup(guids, group_edges)

        if self.settings["show.edges"] and self.settings['_is.valid']:
            compas_rhino.rs.ShowGroup(group_edges)
        else:
            compas_rhino.rs.HideGroup(group_edges)

        # # edge labels ----------------------------------------------------------
        # text = {edge: index for index, edge in enumerate(edges)}
        # guids = self.artist.draw_edgelabels(text=text, color=edges_labels_color)
        # self.guid_edgelabel = zip(guids, edges)
        # compas_rhino.rs.AddObjectsToGroup(guids, group_edges_labels)

        # if self.settings["show.edgelabels"]:
        #     compas_rhino.rs.ShowGroup(group_edges_labels)
        # else:
        #     compas_rhino.rs.HideGroup(group_edges_labels)

        # ======================================================================
        # halffaces
        # ======================================================================

        # halffaces ------------------------------------------------------------
        halffaces = list(self.diagram.faces())
        color = {face: self.settings['color.faces'] if self.settings['_is.valid'] else self.settings['color.invalid'] for face in halffaces}

        if self.settings['show.faces']:
            guids = self.artist.draw_faces(halffaces, color)
            self.guid_face = zip(guids, halffaces)
        # compas_rhino.rs.AddObjectsToGroup(guids, group_halffaces)

        # if self.settings['show.faces']:
        #     compas_rhino.rs.ShowGroup(group_halffaces)
        # else:
        #     compas_rhino.rs.HideGroup(group_halffaces)

        # halfface labels ------------------------------------------------------
        if self.settings["show.facelabels"] and self.settings['_is.valid']:
            text = {halfface: index for index, halfface in enumerate(halffaces)}
            guids = self.artist.draw_facelabels(text=text, color=color)
            self.guid_facelabel = zip(guids, halffaces)
            compas_rhino.rs.AddObjectsToGroup(guids, group_halffaces_labels)

            compas_rhino.rs.ShowGroup(group_halffaces_labels)
        else:
            compas_rhino.rs.HideGroup(group_halffaces_labels)

        # ======================================================================
        # cell labels
        # ======================================================================

        if self.settings["show.celllabels"] and self.settings['_is.valid']:
            cells = list(self.diagram.cells())
            cells_labels_color = {}
            cells_labels_color.update({cell: self.settings['color.celllabels'] for cell in cells})
            guids = self.artist.draw_celllabels(color=cells_labels_color)
            self.guid_celllabel = zip(guids, cells)
            compas_rhino.rs.AddObjectsToGroup(guids, group_cells_labels)

            compas_rhino.rs.ShowGroup(group_cells_labels)
        else:
            compas_rhino.rs.HideGroup(group_cells_labels)

        # ======================================================================
        # angle deviations
        # ======================================================================

        if self.scene and self.scene.settings['3GS']['show.angles']:
            tol = self.scene.settings['3GS']['tol.angles']
            halffaces = [halfface for halfface in self.diagram.faces() if not self.diagram.is_halfface_on_boundary(halfface)]
            angles = self.diagram.faces_attribute('_a', faces=halffaces)
            amin = min(angles)
            amax = max(angles)
            if (amax - amin)**2 > 0.001**2:
                text = {}
                color = {}
                for halfface, angle in zip(halffaces, angles):
                    if angle > tol:
                        text[halfface] = "{:.0f}".format(angle)
                        color[halfface] = i_to_rgb((angle - amin) / (amax - amin))
                if text:
                    guids = self.artist.draw_facelabels(text, color)
                    self.guid_facelabel = zip(guids, halffaces)
                    compas_rhino.rs.AddObjectsToGroup(guids, group_angles)
                    compas_rhino.rs.ShowGroup(group_angles)
        else:
            compas_rhino.rs.HideGroup(group_angles)

        self.redraw()
