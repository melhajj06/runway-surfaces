from .runway import *
from .util import *
import numpy as np
from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.geometry import LineString
from python_tsp.exact import solve_tsp_dynamic_programming
from python_tsp.distances import great_circle_distance_matrix

class Edge():
	def __init__(self, p1, p2, arc=False):
		self.p1 = p1
		self.p2 = p2
		self.arc = arc


def get_horizontal_surface_edges(runways: list[Runway]):
	edges = []
	psurface_vertices = []
	radii = []

	if len(runways) == 0:
		return edges

	for runway in runways:
		point = (runway.end1.point, runway.end2.point)

		if (runway.special_surface):
			point = extend_points_in_both_directions(runway.end1.point, runway.end2.point, 200)

		psurface_vertices.append(point[0])
		psurface_vertices.append(point[1])

		r = runway.calc_hsurface_radius()
		radii.append(r)
		radii.append(r)


	distances_matrix = great_circle_distance_matrix(np.array(psurface_vertices))
	permutation, distance = solve_tsp_dynamic_programming(distances_matrix)

	i = 0
	reordered_vertices = []
	reordered_radii = []
	for node in permutation:
		reordered_vertices.insert(i, psurface_vertices[node])
		reordered_radii.insert(i, radii[node])
		i += 1

	# TODO:
	# check for vertices that would be encompassed entirely by the region had they not been included
	for i in range(len(reordered_vertices)):
		prev_vertex = edges[i - 1].p2 if i > 0 else None
		v1 = reordered_vertices[i]
		v2 = reordered_vertices[(i + 1) % len(reordered_vertices)]
		i1 = calc_perp_intersection(v1, v2, reordered_radii[i])
		i2 = calc_perp_intersection(v2, v1, -reordered_radii[(i + 1) % len(reordered_radii)])

		if prev_vertex:
			edges.append(Edge(prev_vertex, i1, arc=True))

		edges.append(Edge(i1, i2))

	v1 = edges[len(edges) - 1].p2
	v2 = edges[0].p1
	edges.append(Edge(v1, v2, arc=True))

	return edges