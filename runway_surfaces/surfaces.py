from .runway import *
from .util import *


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

		# centerpoint of arc/circle for curved edges
		self.center = center

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
	
	arcs = {}

	for i in range(len(psurface_vertices)):
		p1 = None
		p2 = None
		
		for j in range(len(psurface_vertices)):
			# avoid trying to connect a circle to itself
			# avoid trying to connect circles inside of circles
			if j == i or circle_in_circle(psurface_vertices[i], radii[i], psurface_vertices[j], radii[j]):
				continue

			tangent_line = cet2cr(psurface_vertices[i], radii[i], psurface_vertices[j], radii[j])
			
			if not tangent_line:
				continue

			p1 = tangent_line[0]
			p2 = tangent_line[1]

			for u in range(len(psurface_vertices)):
				for v in range(len(psurface_vertices)):
					if u == v:
						continue

					if segments_intersect(p1, p2, psurface_vertices[u] ,psurface_vertices[v]):
						p1 = None
						p2 = None
						break

				if p1 == None or p2 == None:
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
					if line_intersects_circle(a, b, c, psurface_vertices[u], radii[u]):
						p1 = None
						p2 = None
						break

			if p1 != None and p2 != None:
				if not arcs[i]:
					arcs[i] = []
					arcs[i][0] = p1
				else:
					arcs[i][1] = p1

				if not arcs[j]:
					arcs[j] = []
					arcs[j][0] = p2
				else:
					arcs[j][1] = p2
				break

		if p1 != None and p2 != None:
			edges.append(Edge(p1, p2))

	for i in range(len(psurface_vertices)):
		t = arcs[i]

		if not t:
			continue

		edges.append(Edge(t[0], t[1], psurface_vertices[i]))

	return edges