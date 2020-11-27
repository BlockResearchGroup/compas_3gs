from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import Point
from compas.geometry import Scale
from compas.geometry import Translation
from compas.geometry import Rotation

from compas.utilities import i_to_rgb

import compas_rhino

from compas_3gs.rhino.objects.networkobject import NetworkObject

from compas_3gs.utilities import get_force_colors_uv

__all__ = ['FormNetworkObject']


class FormNetworkObject(NetworkObject):
    """A form network object represents a polyhedral form diagram in the Rhino view.
    """

    SETTINGS = {
        'layer': "3GS::FormDiagram",

        '_is.valid': False,

        'show.nodes': True,
        'show.edges': True,
        'show.loads': True,
        'show.pipes': False,

        'color.invalid': (100, 255, 100),

        'color.node': (0, 0, 0),
        'color.nodes:is_fixed': (0, 0, 255),

        'color.edges': (0, 0, 0),
        'color.pipes': (0, 0, 0),

        'scale.loads': 0.100,
        'scale.pipes': 0.100,

        'tol.loads': 1e-3,
        'tol.pipes': 1e-3
    }

    def __init__(self, diagram, *args, **kwargs):
        super(FormNetworkObject, self).__init__(diagram, *args, **kwargs)
        self.settings.update(FormNetworkObject.SETTINGS)
        settings = kwargs.get('settings') or {}
        if settings:
            self.settings.update(settings)
        self._guid_loads = {}

    @property
    def node_xyz(self):
        """dict : The view coordinates of the network object."""
        origin = Point(0, 0, 0)
        if self.anchor is not None:
            xyz = self.diagram.node_attributes(self.anchor, 'xyz')
            point = Point(* xyz)
            T1 = Translation.from_vector(origin - point)
            S = Scale.from_factors([self.scale] * 3)
            R = Rotation.from_euler_angles(self.rotation)
            T2 = Translation.from_vector(self.location)
            X = T2 * R * S * T1
        else:
            S = Scale.from_factors([self.scale] * 3)
            R = Rotation.from_euler_angles(self.rotation)
            T = Translation.from_vector(self.location)
            X = T * R * S
        network = self.diagram.transformed(X)
        node_xyz = {node: network.node_attributes(node, 'xyz') for node in network.nodes()}
        return node_xyz

    @property
    def guid_loads(self):
        return self._guid_loads

    @guid_loads.setter
    def guid_loads(self, values):
        self._guid_loads = dict(values)

    @property
    def guid_pipe(self):
        return self._guid_pipe

    @guid_pipe.setter
    def guid_pipe(self, values):
        self._guid_pipe = dict(values)

    def check_eq(self):
        tol = self.scene.settings['3GS']['tol.angles']
        edges = list(self.diagram.edges())
        angles = self.diagram.edges_attribute('_a', keys=edges)
        amax = max(angles)
        if amax > tol:
            self.settings['_is.valid'] = False
        else:
            self.settings['_is.valid'] = True

    def clear(self):
        super(FormNetworkObject, self).clear()
        guids = []
        guids += list(self.guid_loads)
        compas_rhino.delete_objects(guids, purge=True)
        self._guid_loads = {}

    # --------------------------------------------------------------------------
    #   attributes
    # --------------------------------------------------------------------------

    # def update_attributes(self):
    #     """Update the attributes of the data structure through a Rhino dialog.

    #     Returns
    #     -------
    #     bool
    #         True if the update was successful.
    #         False otherwise.
    #     """
    #     return compas_rhino.update_settings(self.datastructure.attributes)

    # def update_nodes_attributes(self, keys, names=None):
    #     """Update the attributes of selected nodes.

    #     Parameters
    #     ----------
    #     keys : list
    #         The identifiers of the nodes of which the attributes should be updated.
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
    #         select_nodes(self.datastructure, keys)
    #         return network_update_node_attributes(self.datastructure, keys, names)

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
    #         return network_update_edge_attributes(self.datastructure, keys, names)

    # --------------------------------------------------------------------------
    #   draw
    # --------------------------------------------------------------------------

    def draw(self):
        """Draw the objects representing the form diagram.
        """
        layer = self.settings['layer']
        self.artist.layer = layer
        self.artist.clear_layer()
        self.clear()
        if not self.visible:
            return
        self.artist.node_xyz = self.node_xyz

        # ======================================================================
        # Groups
        # ------
        # Create groups for nodes and edges.
        # These groups will be turned on/off based on the visibility settings of the diagram
        # ======================================================================

        group_nodes = "{}::nodes".format(layer)
        group_edges = "{}::edges".format(layer)
        group_angles = "{}::angles".format(layer)
        group_loads = "{}::loads".format(layer)
        group_pipes = "{}::pipes".format(layer)

        if not compas_rhino.rs.IsGroup(group_nodes):
            compas_rhino.rs.AddGroup(group_nodes)

        if not compas_rhino.rs.IsGroup(group_edges):
            compas_rhino.rs.AddGroup(group_edges)

        if not compas_rhino.rs.IsGroup(group_loads):
            compas_rhino.rs.AddGroup(group_loads)

        if not compas_rhino.rs.IsGroup(group_angles):
            compas_rhino.rs.AddGroup(group_angles)

        if not compas_rhino.rs.IsGroup(group_pipes):
            compas_rhino.rs.AddGroup(group_pipes)

        # ======================================================================
        # nodes
        # --------
        # Draw the nodes and add them to the node group.
        # ======================================================================

        if self.settings['show.nodes']:
            nodes = list(self.diagram.nodes())
            color = {node: self.settings['color.nodes'] if self.settings['_is.valid'] else self.settings['color.invalid'] for node in nodes}
            color_fixed = self.settings['color.nodes:is_fixed']
            color.update({node: color_fixed for node in self.diagram.nodes_where({'is_fixed': True}) if node in nodes})

            guids = self.artist.draw_nodes(nodes, color)
            self.guid_node = zip(guids, nodes)
            compas_rhino.rs.AddObjectsToGroup(guids, group_nodes)

            compas_rhino.rs.ShowGroup(group_nodes)
        else:
            compas_rhino.rs.HideGroup(group_nodes)

        # ======================================================================
        # Edges
        # --------
        # Draw the edges and add them to the edge group.
        # ======================================================================

        if self.settings['show.edges']:
            edges = list(self.diagram.edges())
            colors = {edge: self.settings['color.edges'] for edge in edges}
            if self.scene.settings['3GS']['show.forces']:
                colors = get_force_colors_uv(self.diagram.dual,
                                             self.diagram,
                                             gradient=True)
            colordict = {edge: colors[edge] if self.settings['_is.valid'] else self.settings['color.invalid'] for edge in edges}

            guids = self.artist.draw_edges(edges, colordict)
            self.guid_edge = zip(guids, edges)
            compas_rhino.rs.AddObjectsToGroup(guids, group_edges)

            compas_rhino.rs.ShowGroup(group_edges)
        else:
            compas_rhino.rs.HideGroup(group_edges)

        # ======================================================================
        # Angle deviations
        # --------
        # Draw angle deviatinos as FormNetwork edge labels.
        # ======================================================================

        if self.scene and self.scene.settings['3GS']['show.angles']:
            tol = self.scene.settings['3GS']['tol.angles']
            edges = list(self.diagram.edges())
            angles = self.diagram.edges_attribute('_a', keys=edges)
            amin = min(angles)
            amax = max(angles)
            if (amax - amin)**2 > 0.001**2:
                text = {}
                color = {}
                for edge, angle in zip(edges, angles):
                    if angle > tol:
                        text[edge] = "{:.0f}".format(angle)
                        color[edge] = i_to_rgb((angle - amin) / (amax - amin))
                guids = self.artist.draw_edgelabels(text, color)
                self.guid_edgelabel = zip(guids, edges)
                compas_rhino.rs.AddObjectsToGroup(guids, group_angles)
                compas_rhino.rs.ShowGroup(group_angles)
        else:
            compas_rhino.rs.HideGroup(group_angles)

        # ======================================================================
        # overlays
        # ======================================================================

        if self.settings['show.loads'] and self.settings['_is.valid']:
            scale = self.settings['scale.loads']
            guids = self.artist.draw_external_forces(gradient=False, scale=scale)
            self.guid_edge = zip(guids, self.diagram.dual.cells_on_boundaries())
            compas_rhino.rs.AddObjectsToGroup(guids, group_loads)
            compas_rhino.rs.ShowGroup(group_loads)
        else:
            compas_rhino.rs.HideGroup(group_loads)

        if self.settings['show.pipes'] and self.settings['_is.valid']:
            tol = self.settings['tol.pipes']
            edges = list(self.diagram.edges())
            colors = {edge: self.settings['color.pipes'] for edge in edges}

            if self.scene.settings['3GS']['show.forces']:
                colors = get_force_colors_uv(self.diagram.dual,
                                             self.diagram,
                                             gradient=True)
            scale = self.settings['scale.pipes']
            guids = self.artist.draw_pipes(edges, colors, scale, tol)
            self.guid_pipe = zip(guids, edges)
            compas_rhino.rs.AddObjectsToGroup(guids, group_pipes)
            compas_rhino.rs.ShowGroup(group_pipes)
        else:
            compas_rhino.rs.HideGroup(group_pipes)

        self.redraw()
