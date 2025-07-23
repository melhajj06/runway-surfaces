from .runway import *
from .util import *


class Edge():
	"""Represents a straight or curved edge of a horizontal surface around a series of runways
	"""

	def __init__(self, p1: tuple[float, float], p2: tuple[float, float], center: tuple[float, float] = tuple()):
		"""Creates a new ``Edge`` object

		If ``center`` is not empty, then this edge is to be interpreted as an arc from ``p1`` to ``p2`` centered at ``center``.
		Otherwise, this edge is a straight line segment from ``p1`` to ``p2``
		
		:param (_type_) p1: a 2D coordinate point
		:param (_type_) p2: a 2D coordinate point
		:param (_type_) center: the centerpoint of the arc from ``p1`` to ``p2``, defaults to tuple()
		"""

		self.p1 = p1
		self.p2 = p2
		self.center = center

# TODO: optimize this. since it's already in ccw order, no need to check every possible common tangent at first
def get_horizontal_surface_edges(runways: list[Runway]) -> list[Edge]:
	"""Gets the outline of the horizontal surface encompassing every runway in ``runways``
	
	See `FAR Part-77 <https://www.ecfr.gov/current/title-14/part-77/section-77.19#p-77.19(a)>`_
	
	:param (list[Runway]) runways: a list of ``Runway``s
	:return (list[Edge]): a list of ``Edge``s defining the outline of the horizontal surface
	"""

	edges = []
	psurface_vertices = {}

	if len(runways) == 0:
		return edges
	
	# get the correct primary surface endpoints for each runway
	for runway in runways:
		extended_endpoints = (runway.end1.point, runway.end2.point)

		if (runway.special_surface):
			extended_endpoints = extend_points_in_both_directions(runway.end1.point, runway.end2.point, 200)

		r = runway.calc_hsurface_radius()
		psurface_vertices[tuple(extended_endpoints[0])] = r
		psurface_vertices[tuple(extended_endpoints[1])] = r

	# sort points in counter-clockwise order
	endpoints = list(psurface_vertices.keys())
	sort_directional(endpoints, ccw=True)
	psurface_vertices = {point: psurface_vertices[point] for point in endpoints}
	
	# if the order is not preserved
	next_point = -1
	i = 0

	while i < len(endpoints):
		prev_edge = edges[-1] if len(edges) > 0 else None
		c1 = endpoints[i] if next_point < 0 else endpoints[next_point]
		p1 = None
		p2 = None
		
		for j in range(len(endpoints)):
			c2 = endpoints[j]

			# avoid trying to connect a circle to itself
			# avoid trying to connect circles inside of circles
			if (next_point >= 0 and next_point == j) or i == j or circle_in_circle(c1, psurface_vertices[c1], c2, psurface_vertices[c2]):
				continue

			tangent_line = cet2cr(c1, psurface_vertices[c1], c2, psurface_vertices[c2])
			
			if len(tangent_line) == 0:
				continue

			p1 = tangent_line[0]
			p2 = tangent_line[1]

			for u in range(len(endpoints)):
				t1 = endpoints[u]
				t2 = endpoints[(u + 1) % len(endpoints)]

				# if the tangent line intersects any perimeter segment,
				# then it isn't valid
				if len(line_intersects_segment(p1, p2, t1, t2)) > 0:
					p1 = None
					p2 = None
					break
				
				# if the tangent line intersects any other circle than those that it's tangent to,
				# then it isn't valid
				if u != i and u != j:
					a = 0
					b = 0
					c = 0
					if p2[0] - p1[0] == 0:
						a = 1
						c = -p1[0]
					else:
						m = (p2[1] - p1[1]) / (p2[0] - p1[0])
						a = -m
						b = 1
						c = m * p1[0] - p1[1]
					
					# if the line is a common external tangent to 3 circles then it still counts
					#
					# no need to check the side of the 3rd circle's tangent point since,
					# if it's on the wrong side, it will intersect a line segment as well
					l = len(line_intersects_circle(a, b, c, t1, psurface_vertices[t1]))
					if l == 0 or l == 1:
						continue
					else:
						p1 = None
						p2 = None
						break
			
			# if the tangent line does not intersect any perimeter segments nor any other circles,
			# it is valid
			if p1 and p2:
				if j != (i + 1) % len(endpoints):
					next_point = j
					i = i - 1
				else:
					next_point = -1
				break

		# if no tangent line that doesn't have an invalid intersection is found,
		# then this point would either create a concavity or a self intersection in the final surface
		if p1 and p2:
			if prev_edge:
				edges.append(Edge(prev_edge.p2, p1, center=c1))
			edges.append(Edge(p1, p2))
		
		i += 1

	# since runways aren't allowed to have differing radii at their endpoints, len(edges) will always be at least 3 at this point
	edges.append(Edge(edges[-1].p2, edges[0].p1, center=endpoints[0]))
	return edges


def get_primary_surface_vertices(runway: Runway) -> list[tuple[float, float]]:
	"""Gets the 2D coordinate points of the vertices of the primary surface for ``runway``

	:param Runway runway: a runway
	:return list[tuple[float, float]]: the vertices of the primary surface for ``runway``
	"""

	endpoints = [runway.end1.point, runway.end2.point]
	if runway.special_surface:
		endpoints = extend_points_in_both_directions(runway.end1.point, runway.end2.point, 200)
	
	w = runway.calc_psurface_width() / 2.0
	side1 = create_right_triangle(endpoints[0], endpoints[1], w)
	side2 = create_right_triangle(endpoints[1], endpoints[0], w)

	if len(side1) == 0 or len(side2) == 0:
		return []
	
	return [*side1, *side2]


def get_approach_surface_lines(psurface_vertices: list[tuple[float, float]]) -> list[Line3D]:
	return []