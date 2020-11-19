from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.utilities import i_to_rgb
from compas.geometry import Point
from compas.geometry import Scale
from compas.geometry import Translation
from compas.geometry import Rotation

import compas_rhino
from compas_rhino.objects import mesh_update_vertex_attributes
from compas_rhino.objects import mesh_update_edge_attributes
from compas_rhino.objects import mesh_update_face_attributes

from compas_3gs.rhino.objects.volmeshobject import VolMeshObject


__all__ = ['ForceVolMeshObject']


class ForceVolMeshObject(VolMeshObject):
    """A force volmesh object represents a polyhedral force diagram in the Rhino view.
    """

    SETTINGS = {
        'show.vertices': True,
        'show.edges': True,
        'show.faces': True,
        'show.vertexlabels': False,
        'show.edgelabels': False,
        'show.celllabels': False,

        'color.vertices': (255, 0, 0),
        'color.vertexlabels': (255, 255, 255),
        'color.vertices:is_fixed': (0, 0, 255),

        'color.edges': (0, 0, 0),
        'color.edgelabels': (0, 0, 0),

        'color.faces': (125, 125, 125),
        'color.facelabels': (125, 125, 125),

        'color.celllabels': (0, 0, 255)
    }

    def __init__(self, diagram, *args, **kwargs):
        super(ForceVolMeshObject, self).__init__(diagram, *args, **kwargs)
        self.settings.update(ForceVolMeshObject.SETTINGS)
        settings = kwargs.get('settings') or {}
        if settings:
            self.settings.update(settings)

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

    # --------------------------------------------------------------------------
    #   modify
    # --------------------------------------------------------------------------

    def move_vertex(self, vertex):
        pass


    def move_vertices(self, vertices):
        pass


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

        self.clear()
        if not self.visible:
            return

        self.artist.vertex_xyz = self.vertex_xyz

        # vertices
        if self.settings['show.vertices']:

            vertices = list(self.diagram.vertices())
            vertices_color = {}
            vertices_label_color = {}

            for vertex in vertices:

                if self.diagram.vertex_attribute(vertex, 'is_fixed'):
                    vertices_color[vertex] = self.settings['color.vertices:is_fixed']
                    vertices_label_color[vertex] = self.settings['color.vertices:is_fixed']
                else:
                    vertices_color[vertex] = self.settings['color.vertices']
                    vertices_label_color[vertex] = self.settings['color.vertexlabels']

            guids = self.artist.draw_vertices(color=vertices_color)
            self.guid_vertex = zip(guids, vertices)

            # vertex labels
            if self.settings['show.vertexlabels']:
                text = {vertex: index for index, vertex in enumerate(vertices)}
                guids = self.artist.draw_vertexlabels(text=text, color=vertices_label_color)
                self.guid_vertexlabel = zip(guids, vertices)

        # edges
        if self.settings['show.edges']:
            edges = list(self.diagram.edges())
            color = {}
            color.update({edge: self.settings['color.edges'] for edge in edges})

            guids = self.artist.draw_edges(color=color)
            self.guid_edge = zip(guids, edges)

        self.redraw()

        # # ======================================================================
        # # Groups
        # # ------
        # # Create groups for vertices and edges.
        # # These groups will be turned on/off based on the visibility settings of the diagram
        # # ======================================================================

        # group_vertices = "{}::vertices".format(layer)
        # group_edges = "{}::edges".format(layer)

        # if not compas_rhino.rs.IsGroup(group_vertices):
        #     compas_rhino.rs.AddGroup(group_vertices)

        # if not compas_rhino.rs.IsGroup(group_edges):
        #     compas_rhino.rs.AddGroup(group_edges)

        # # ======================================================================
        # # Vertices
        # # --------
        # # Draw the vertices and add them to the vertex group.
        # # ======================================================================

        # vertices = list(self.volmesh.vertices())
        # color = {vertex: self.settings['color.vertices'] for vertex in vertices}
        # color_fixed = self.settings['color.vertices:is_fixed']
        # color.update({vertex: color_fixed for vertex in self.volmesh.vertices_where({'is_fixed': True}) if vertex in vertices})

        # guids = self.artist.draw_vertices(vertices, color)
        # self.guid_vertex = zip(guids, vertices)
        # compas_rhino.rs.AddObjectsToGroup(guids, group_vertices)

        # if self.settings['show.vertices']:
        #     compas_rhino.rs.ShowGroup(group_vertices)
        # else:
        #     compas_rhino.rs.HideGroup(group_vertices)

        # # ======================================================================
        # # Edges
        # # --------
        # # Draw the edges and add them to the edge group.
        # # ======================================================================

        # edges = list(self.volmesh.edges())
        # color = {edge: self.settings['color.edges'] for edge in edges}

        # guids = self.artist.draw_edges(edges, color)
        # self.guid_edge = zip(guids, edges)
        # compas_rhino.rs.AddObjectsToGroup(guids, group_edges)

        # if self.settings['show.edges']:
        #     compas_rhino.rs.ShowGroup(group_edges)
        # else:
        #     compas_rhino.rs.HideGroup(group_edges)

