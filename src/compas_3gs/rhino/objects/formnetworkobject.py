from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import Point
from compas.geometry import Scale
from compas.geometry import Translation
from compas.geometry import Rotation

import compas_rhino

from compas_rhino.objects import network_update_node_attributes
from compas_rhino.objects import network_update_edge_attributes

from compas_3gs.rhino.objects.networkobject import NetworkObject


__all__ = ['FormNetworkObject']


class FormNetworkObject(NetworkObject):
    """A form network object represents a polyhedral form diagram in the Rhino view.
    """

    SETTINGS = {
        'layer': "3GS::FormDiagram",

        'show.nodes': True,
        'show.edges': True,

        'show.nodelabels': False,
        'show.edgelabels': False,

        'color.node': (0, 0, 0),
        'color.nodelabels': (0, 0, 0),
        'color.nodes:is_fixed': (0, 0, 255),

        'color.edges': (0, 0, 0),
        'color.edgelabels': (255, 255, 255),
    }

    def __init__(self, diagram, *args, **kwargs):
        super(FormNetworkObject, self).__init__(diagram, *args, **kwargs)
        self.settings.update(FormNetworkObject.SETTINGS)
        settings = kwargs.get('settings') or {}
        if settings:
            self.settings.update(settings)

    @property
    def node_xyz(self):
        """dict : The view coordinates of the network object."""
        origin = Point(0, 0, 0)
        if self.anchor is not None:
            xyz = self.network.node_attributes(self.anchor, 'xyz')
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
        network = self.network.transformed(X)
        node_xyz = {node: network.node_attributes(node, 'xyz') for node in network.nodes()}
        return node_xyz

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

        if not compas_rhino.rs.IsGroup(group_nodes):
            compas_rhino.rs.AddGroup(group_nodes)

        if not compas_rhino.rs.IsGroup(group_edges):
            compas_rhino.rs.AddGroup(group_edges)

        # ======================================================================
        # nodes
        # --------
        # Draw the nodes and add them to the node group.
        # ======================================================================

        nodes = list(self.network.nodes())
        color = {node: self.settings['color.nodes'] for node in nodes}
        color_fixed = self.settings['color.nodes:is_fixed']
        color.update({node: color_fixed for node in self.network.nodes_where({'is_fixed': True}) if node in nodes})

        guids = self.artist.draw_nodes(nodes, color)
        self.guid_node = zip(guids, nodes)
        compas_rhino.rs.AddObjectsToGroup(guids, group_nodes)

        if self.settings['show.nodes']:
            compas_rhino.rs.ShowGroup(group_nodes)
        else:
            compas_rhino.rs.HideGroup(group_nodes)

        # ======================================================================
        # Edges
        # --------
        # Draw the edges and add them to the edge group.
        # ======================================================================

        edges = list(self.network.edges())
        color = {edge: self.settings['color.edges'] for edge in edges}

        guids = self.artist.draw_edges(edges, color)
        self.guid_edge = zip(guids, edges)
        compas_rhino.rs.AddObjectsToGroup(guids, group_edges)

        if self.settings['show.edges']:
            compas_rhino.rs.ShowGroup(group_edges)
        else:
            compas_rhino.rs.HideGroup(group_edges)
