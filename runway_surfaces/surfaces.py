from .runway import *
from .util import *


# represents a straight or curved edge of the horizontal surface around a runway
class Edge():
	# ctor
	#
	# param p1 {tuple}: a 2D coordinate point
	# param p2 {tuple}: a 2D coordinate point
	def __init__(self, p1, p2):
		self.p1 = p1
		self.p2 = p2

def get_horizontal_surface_edges(runways: list[Runway]):
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

	endpoints = list(psurface_vertices.keys())
	sort_directional(endpoints, ccw=True)
	psurface_vertices = {point: psurface_vertices[point] for point in endpoints}
	
	for i in range(len(endpoints)):
		c1 = endpoints[i]
		p1 = None
		p2 = None
		
		for j in range(len(endpoints)):
			c2 = endpoints[j]

			# avoid trying to connect a circle to itself
			# avoid trying to connect circles inside of circles
			if i == j or circle_in_circle(c1, psurface_vertices[c1], c2, psurface_vertices[c2]):
				continue

			tangent_line = cet2cr(c1, psurface_vertices[c1], c2, psurface_vertices[c2])
			
			if not tangent_line:
				continue

			p1 = tangent_line[0]
			p2 = tangent_line[1]

			for u in range(len(endpoints)):
				t1 = endpoints[u]
				t2 = endpoints[(u + 1) % len(endpoints)]

				if line_intersects_segment(p1, p2, t1, t2):
					p1 = None
					p2 = None
					break

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
					if line_intersects_circle(a, b, c, t1, psurface_vertices[t1]):
						p1 = None
						p2 = None
						break

			if p1 and p2:
				break

		if p1 and p2:
			edges.append(Edge(p1, p2))

	return edges