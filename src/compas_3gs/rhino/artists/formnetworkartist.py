from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from math import pi
from math import sqrt

import compas_rhino

from compas.geometry import add_vectors
from compas.geometry import scale_vector
from compas.geometry import length_vector

from compas.utilities import i_to_green

from compas_3gs.rhino.artists.networkartist import NetworkArtist

from compas_3gs.utilities import valuedict_to_colordict
from compas_3gs.utilities import get_force_mags


__all__ = ['FormNetworkArtist']


class FormNetworkArtist(NetworkArtist):
    """Artist for visualizing force diagrams in the Rhino model space."""

    def __init__(self, form, layer=None):
        super(FormNetworkArtist, self).__init__(form, layer=layer)

    @property
    def node_xyz(self):
        """dict:
        The view coordinates of the network vertices.
        The view coordinates default to the actual network coordinates.
        """
        if not self._node_xyz:
            self._node_xyz = {node: self.diagram.node_attributes(node, 'xyz') + [0.0] for node in self.diagram.nodes()}
        return self._node_xyz

    @node_xyz.setter
    def node_xyz(self, node_xyz):
        self._node_xyz = node_xyz

    def draw_external_forces(self, gradient=True, scale=1.0):
        node_xyz = self.node_xyz

        volmesh = self.diagram.dual
        network = self.diagram

        load_vectors = {}
        load_mags = {}

        for cell in volmesh.cells_on_boundaries():
            vectors = []
            for face in volmesh.cell_faces(cell):
                if volmesh.is_halfface_on_boundary(face):
                    vectors.append(volmesh.halfface_normal(face, unitized=False))

            vectors = zip(*vectors)
            resultant = [sum(vector) for vector in vectors]
            load_vectors[cell] = resultant
            load_mags[cell] = length_vector(resultant)

        colordict = valuedict_to_colordict(load_mags, color_scheme=i_to_green)

        lines = []
        for vertex in load_vectors:
            vector = scale_vector(load_vectors[vertex], scale)
            sp = node_xyz[vertex]
            ep = add_vectors(sp, vector)
            if volmesh.attributes['convention'] == -1:
                sp, ep = ep, sp
            color = (0, 100, 0)
            if gradient:
                color = colordict[vertex]
            lines.append({
                'start': sp,
                'end': ep,
                'color': color,
                'arrow': 'end',
                'name': '{}.load.at.vertex.{}'.format(network.name, vertex)})

        return compas_rhino.draw_lines(lines,
                                       layer=self.layer,
                                       clear=False,
                                       redraw=False)

    def draw_pipes(self, edges, color, scale, tol):
        node_xyz = self.node_xyz
        cylinders = []

        forces = get_force_mags(self.diagram.dual, self.diagram)

        for edge in edges:
            u, v = edge
            start = node_xyz[u]
            end = node_xyz[v]
            force = abs(forces[edge])
            force = scale * force
            if force < tol:
                continue
            radius = sqrt(force / pi)
            if isinstance(color, dict):
                pipe_color = color[edge]
            else:
                pipe_color = color
            cylinders.append({
                'start': start,
                'end': end,
                'radius': radius,
                'color': pipe_color
            })
        return compas_rhino.draw_cylinders(cylinders, layer=self.layer, clear=False, redraw=False)
