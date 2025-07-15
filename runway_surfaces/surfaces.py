from .runway import *
from .util import *
import numpy as np
from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.geometry import LineString
from python_tsp.exact import solve_tsp_dynamic_programming
from python_tsp.distances import great_circle_distance_matrix


# represents a straight or curved edge of the horizontal surface around a runway
class Edge():
	# ctor
	#
	# param p1 {tuple}: a 2D coordinate point
	# param p2 {tuple}: a 2D coordinate point
	# param center {tuple}: the center of the circle the arc from {p1} to {p2} lies on if this edge is curved
	def __init__(self, p1, p2, center=None):
		self.p1 = p1
		self.p2 = p2

		# used for the curved bits of the horizontal surface outline
		self.center = center


# gets a list of edges defining the outline of the horizontal surface around the runways in {runways}
#
# param runways {list[Runway]}: a list of runways
#
# return {list[Edge]}: the outline of the horizontal surface
def get_horizontal_surface_edges(runways: list[Runway]):
	edges = []
	psurface_vertices = []
	radii = []

	if len(runways) == 0:
		return edges

	# get the correct primary surface endpoints for each runway
	for runway in runways:
		extended_endpoints = (runway.end1.point, runway.end2.point)

		if (runway.special_surface):
			extended_endpoints = extend_points_in_both_directions(runway.end1.point, runway.end2.point, 200)

		psurface_vertices.append(extended_endpoints[0])
		psurface_vertices.append(extended_endpoints[1])

		r = runway.calc_hsurface_radius()
		radii.append(r)
		radii.append(r)

	# solve with TSP to make non-intersecting polygon from all endpoints
	distances_matrix = great_circle_distance_matrix(np.array(psurface_vertices))
	permutation, distance = solve_tsp_dynamic_programming(distances_matrix)

	# reorder the vertices from TSP solution
	i = 0
	reordered_vertices = []
	reordered_radii = []
	for node in permutation:
		reordered_vertices.insert(i, psurface_vertices[node])
		reordered_radii.insert(i, radii[node])
		i += 1

	# breakpoint()

	dir = get_polygon_direction(reordered_vertices)
	if dir and dir > 0:
		reordered_vertices.reverse()
		reordered_radii.reverse()

	# breakpoint()

	cleaned_vertices = []
	cleaned_radii = []

	# remove all endpoints that would be entirely encompassed by another
	for i in range(len(reordered_vertices)):
		c1 = reordered_vertices[i]
		r1 = reordered_radii[i]
		c2 = reordered_vertices[(i + 1) % len(reordered_vertices)]
		r2 = reordered_radii[(i + 1) % len(reordered_vertices)]

		if circle_in_circle(c1, r1, c2, r2):
			if r1 < r2:
				continue
			if r1 >= r2:
				if (i == len(reordered_vertices) - 1):
					cleaned_vertices.pop(0)
					cleaned_radii.pop(0)
				else:
					cleaned_vertices.append(c1)
					cleaned_radii.append(r1)
					i += 1
		else:
			cleaned_vertices.append(c1)
			cleaned_radii.append(r1)

	breakpoint()

	# handle len = 2 edge-case

	# calculate edges
	#
	# TODO:
	# - check if endpoint is unnecessary
	#	i.e. if the common tangent point on the endpoint's circle is to the left (cross product check) of the previous edge
	for i in range(len(cleaned_vertices)):
		prev_edge = None
		if i > 0:
			prev_edge = edges[i - 1] if i > 0 else None

		c1 = cleaned_vertices[i]
		r1 = cleaned_radii[i]
		c2 = cleaned_vertices[(i + 1) % len(cleaned_vertices)]
		r2 = cleaned_radii[(i + 1) % len(cleaned_radii)]

		tangent_line = cet2cr(c1, r1, c2, r2)
		t1 = None
		t2 = None

		# after the cleaning step, there shouldn't be any undefined common tangent points
		# this is to make python happy
		if not tangent_line:
			raise Exception('common tangent points are NoneType')

		t1 = tangent_line[0]
		t2 = tangent_line[1]

		if prev_edge:
			# test points
			p1 = t1
			p2 = prev_edge.p2

			tangent_line2 = cet2cr(cleaned_vertices[i - 1], cleaned_radii[i - 1], c2, r2)
			if not tangent_line2:
				raise Exception('common tangent points are NoneType')

			l1 = tangent_line2[0]
			l2 = tangent_line2[1]
			det1 = get_side_of_line(l1, l2, p1)
			det2 = get_side_of_line(l1, l2, p2)
			if det1 >= 0 and det2 >= 0:  # not really necessary to test both, but performance isn't at the forefront of development right now
				prev_edge.p1 = l1
				prev_edge.p2 = l2
				continue
			else:
				edges.append(Edge(prev_edge.p2, t1, c1))

		edges.append(Edge(t1, t2))

	p1 = edges[-1].p2
	p2 = edges[0].p1
	c1 = cleaned_vertices[-1]
	r1 = cleaned_radii[-1]
	c2 = cleaned_vertices[1]
	r2 = cleaned_radii[1]
	tangent_line = cet2cr(c1, r1, c2, r2)

	if not tangent_line:
		raise Exception('common tangent points are NoneType')
	
	l1 = tangent_line[0]
	l2 = tangent_line[1]

	det1 = get_side_of_line(l1, l2, p1)
	det2 = get_side_of_line(l1, l2, p2)

	# not really necessary to test both, but performance isn't at the forefront of development right now
	if det1 >= 0 and det2 >= 0:
		edges[-1].p1 = l1
		edges[-1].p2 = l2
		edges.pop(0)

	edges.append(Edge(edges[-1].p2, edges[0].p1, cleaned_vertices[0]))

	return edges