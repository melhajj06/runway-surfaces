from .runway import *
from .util import *
from typing import Optional

class Edge():
	"""Represents a straight or curved edge of a horizontal surface around a series of runways
	"""

	def __init__(self, p1: tuple[np.float64, np.float64], p2: tuple[np.float64, np.float64], center: tuple[np.float64, np.float64] = tuple()):
		r"""Creates a new ``Edge`` object

		If ``center`` is not empty, then this edge is to be interpreted as an arc from ``p1`` to ``p2`` centered at ``center``.
		Otherwise, this edge is a straight line segment from ``p1`` to ``p2``
		
		:param tuple[np.float64, np.float64] p1: a 2D coordinate point
		:param tuple[np.float64, np.float64] p2: a 2D coordinate point
		:param tuple[np.float64, np.float64] center: the centerpoint of the arc from ``p1`` to ``p2``, defaults to tuple()
		"""

		self.p1 = p1
		self.p2 = p2
		self.center = center


class Arc(Edge):

	def __init__(self, center: tuple[np.float64, np.float64], radius: np.float64):
		self.center = center
		self.radius = radius



# TODO: optimize this. since it's already in ccw order, no need to check every possible common tangent at first
def get_horizontal_surface_edges(runways: list[Runway]) -> list[Edge]:
	r"""Gets the outline of the horizontal surface encompassing every runway in ``runways``
	
	See `FAR Part-77 <https://www.ecfr.gov/current/title-14/part-77/section-77.19#p-77.19(a)>`_
	
	:param list[Runway] runways: a list of ``Runway``\s
	:return list[Edge]: a list of ``Edge``s defining the outline of the horizontal surface
	"""

	edges = []
	psurface_vertices = {}

	if len(runways) == 0:
		return edges
	
	# get the correct primary surface endpoints for each runway
	for runway in runways:
		extended_endpoints = (runway.end1.point, runway.end2.point)

		if (runway.special_surface):
			extended_endpoints = extend_points_in_both_directions(runway.end1.point, runway.end2.point, np.float64(200))

		r = runway.calc_hsurface_radius()
		psurface_vertices[tuple(extended_endpoints[0])] = r
		psurface_vertices[tuple(extended_endpoints[1])] = r

	# sort points in counter-clockwise order
	endpoints = list(psurface_vertices.keys())
	sort_directional(endpoints, ccw=True)
	psurface_vertices = {point: psurface_vertices[point] for point in endpoints}

	current_circle = 0
	for i in range(len(endpoints)):
		current_circle = i
		prev_edge = edges[-1] if len(edges) > 0 else None
		c1 = endpoints[current_circle]
		p1 = None
		p2 = None

		secondary_circle = i
		c2 = tuple()
		for j in range(len(endpoints)):
			c2 = endpoints[secondary_circle]

			# avoid trying to connect a circle to itself
			# avoid trying to connect circles inside of circles // (next_point >= 0 and next_point == j)
			if secondary_circle == current_circle or circle_in_circle(c1, psurface_vertices[c1], c2, psurface_vertices[c2]):
				secondary_circle = (secondary_circle + 1) % len(endpoints)
				continue

			tangent_line = cet2cr(c1, psurface_vertices[c1], c2, psurface_vertices[c2])
			
			if len(tangent_line) == 0:
				secondary_circle = (secondary_circle + 1) % len(endpoints)
				continue

			p1 = tangent_line[0]
			p2 = tangent_line[1]

			for u in range(len(endpoints)):
				t1 = endpoints[u]
				t2 = endpoints[(u + 1) % len(endpoints)]

				# if the tangent line intersects any perimeter segment,
				# then it isn't valid
				if len(lis_4p(p1, p2, t1, t2)) > 0:
					p1 = None
					p2 = None
					break
				
				# if the tangent line intersects any other circle than those that it's tangent to,
				# then it isn't valid
				if u != current_circle and u != secondary_circle:
					a = np.float64(0)
					b = np.float64(0)
					c = np.float64(0)
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
					l = len(line_intersects_circle(np.float64(a), np.float64(b), c, t1, psurface_vertices[t1]))
					if l == 0 or l == 1:
						continue
					else:
						p1 = None
						p2 = None
						break
			
			# if the tangent line does not intersect any perimeter segments nor any other circles,
			# it is valid
			if p1 and p2:
				current_circle = secondary_circle
				break

			secondary_circle = (secondary_circle + 1) % len(endpoints)

		# if no tangent line that doesn't have an invalid intersection is found,
		# then this point would either create a concavity or a self intersection in the final surface
		if p1 and p2:
			if prev_edge:
				edges.append(Arc(c1, calc_distance(c1, p1)))
			edges.append(Edge(p1, p2))
	# since runways aren't allowed to have differing radii at their endpoints, len(edges) will always be at least 3 at this point
	edges.append(Edge(edges[-1].p2, edges[0].p1, center=endpoints[0]))
	return edges


def get_primary_surface_vertices(runway: Runway) -> dict[RunwayEnd, list[tuple[np.float64, np.float64]]]:
	r"""Gets the 2D coordinate points of the vertices of the primary surface for ``runway``

	:param Runway runway: a runway
	:return dict[RunwayEnd, list[tuple[np.float64, np.float64]]]: the ends of ``runway`` mapped to their respective primary surface vertices
	"""

	vertices: dict[RunwayEnd, list[tuple[np.float64, np.float64]]] = {}

	# extend endpoints for special surface runways
	endpoints = [runway.end1.point, runway.end2.point]
	if runway.special_surface:
		endpoints = extend_points_in_both_directions(runway.end1.point, runway.end2.point, np.float64(200))
	
	# get vertices along lines perpendicular to the line defined by the endpoints
	w = runway.calc_psurface_width() / np.float64(2.0)
	side2 = create_right_triangle(endpoints[0], endpoints[1], w)
	side1 = create_right_triangle(endpoints[1], endpoints[0], w)

	if len(side1) == 0 or len(side2) == 0:
		return dict()
	
	vertices[runway.end1] = side1
	vertices[runway.end2] = side2

	return vertices


def get_approach_surface_vertices(end_infos: dict[RunwayEnd, dict[str, np.float64]], psurface_vertices: dict[RunwayEnd, list[tuple[np.float64, np.float64]]]) -> dict[RunwayEnd, list[tuple[np.float64, np.float64]]]:
	r"""Gets the vertices of the 2D projection of the approach surface

	For each ``RunwayEnd`` in ``end_infos``,
	a list of 4 2D coordinate points is generated that create bounds for the approach surface.

	:param dict[RunwayEnd, dict[str, np.float64]] end_infos: a mapping of one runway's ends to their respective dimensions/infos as returned by ``Runway.calc_approach_dimensions``
	:param dict[RunwayEnd, list[tuple[np.float64, np.float64]]] psurface_vertices: a mapping of one runway's ends to the vertices of the primary surface of that runway's end
	:return dict[RunwayEnd, list[tuple[np.float64, np.float64]]]: a mapping of each runway end of one runway to a list of 2D vertices that are the bounds of the respective approach surface
	"""
	
	vertices: dict[RunwayEnd, list[tuple[np.float64, np.float64]]] = {}
	
	entries = list(end_infos.items())
	end1_dimensions = entries[0][1]
	end2_dimensions = entries[1][1]
	end1_vertices = psurface_vertices[entries[0][0]]
	end2_vertices = psurface_vertices[entries[1][0]]

	vertices[entries[0][0]] = []
	vertices[entries[1][0]] = []

	assert end1_vertices
	assert end2_vertices

	# get midpoints of each end
	end1_midpoint = ((end1_vertices[0][0] + end1_vertices[1][0]) / 2, (end1_vertices[0][1] + end1_vertices[1][1]) / 2)
	end2_midpoint = ((end2_vertices[0][0] + end2_vertices[1][0]) / 2, (end2_vertices[0][1] + end2_vertices[1][1]) / 2)

	type = end1_dimensions["type"]
	width = end1_dimensions["width"]
	length = 0

	if (type == ApproachTypes.PRECISION_INSTRUMENT):
		length = end1_dimensions["primary_length"] + end1_dimensions["secondary_length"]
	else:
		length = end1_dimensions["length"]

	# extend the center line to the length of the approach surface
	cl = extend_point_in_one_direction(end2_midpoint, end1_midpoint, length)
	w =  width / 2

	# create a right triangle so that the hypotenuse is the desired line
	triangle = create_right_triangle(end1_midpoint, cl, np.float64(w))
	
	# ccw direction
	vertices[entries[0][0]].append(end1_vertices[0])
	vertices[entries[0][0]].append(end1_vertices[1])
	vertices[entries[0][0]].append(triangle[1])
	vertices[entries[0][0]].append(triangle[0])

	type = end2_dimensions["type"]
	width = end2_dimensions["width"]
	length = 0

	if (type == ApproachTypes.PRECISION_INSTRUMENT):
		length = end1_dimensions["primary_length"] + end1_dimensions["secondary_length"]
	else:
		length = end1_dimensions["length"]

	cl = extend_point_in_one_direction(end1_midpoint, end2_midpoint, length)
	triangle = create_right_triangle(end2_midpoint, cl, np.float64(w))

	vertices[entries[1][0]].append(end2_vertices[0])
	vertices[entries[1][0]].append(end2_vertices[1])
	vertices[entries[1][0]].append(triangle[1])
	vertices[entries[1][0]].append(triangle[0])

	return vertices


def get_transitional_surface_vertices(psurface_vertices: dict[RunwayEnd, list[tuple[np.float64, np.float64]]], asurfaces: dict[RunwayEnd, list[tuple[np.float64, np.float64]]]) -> list[list[tuple[np.float64, np.float64]]]:
	"""Gets the vertices of the 2D projection of the transitional surface

	A 2x4 list is returned where the the first row contains all the vertices for the transitional surface on one side of the runway,
	while the second row contains all the vertices for the transitional surface on the other side of the runway.

	:param dict[RunwayEnd, list[tuple[np.float64, np.float64]]] psurface_vertices: a mapping of one runway's ends to the vertices of the primary surface of that runway's end
	:param dict[RunwayEnd, list[tuple[np.float64, np.float64]]] asurfaces: a mapping of one runway's ends to the vertices of the approach surface of that runway's end
	:return list[list[tuple[np.float64, np.float64]]]: a list containing lists of the vertices of the transitional surface for either side of the runway
	"""

	s1 = []
	s2 = []
	entries = list(psurface_vertices.items())
	end1 = entries[0][0]
	end2 = entries[1][0]
	end1_vertices = psurface_vertices[end1]
	end2_vertices = psurface_vertices[end2]

	# calculate distance from runway centerline to straight edge of transitional surface
	d = calc_dist_for_height(np.float64(1.0) / 7.0, (np.float64(150)))
	extended1 = extend_points_in_both_directions(end1_vertices[0], end1_vertices[1], d)
	extended2 = extend_points_in_both_directions(end2_vertices[0], end2_vertices[1], d)
	v1, v2 = extended1[0], extended1[1]
	v3, v4 = extended2[0], extended2[1]

	# ccw direction
	s1.append(end1_vertices[0])
	s1.append(asurfaces[end1][3])
	s1.append(v1)
	s1.append(v4)
	s1.append(asurfaces[end2][2])
	s1.append(end2_vertices[1])

	# ccw direction
	s2.append(end2_vertices[0])
	s2.append(asurfaces[end2][3])
	s2.append(v3)
	s2.append(v2)
	s2.append(asurfaces[end1][2])
	s2.append(end1_vertices[1])

	return [s1, s2]


def is_in_horizontal_surface(position: tuple[np.float64, np.float64], hsurface: list[Edge]) -> bool:
	r"""Checks if ``position`` is in or on the boundary of a horizontal surface defined by ``hsurface``

	:param tuple[np.float64, np.float64] position: a 2D coordinate point
	:param list[Edge] hsurface: a list of ``Edges`` defining a horizontal surface
	:return bool: whether ``position`` is in or on the boundary of the horizontal surface
	"""
	
	# since all lists of vertices will be in counterclockwise direction, the left of the line is considered "inside"
	for edge in hsurface:
		# check if at a curve
		if type(edge) is Arc:
			if not is_in_circle(position, edge.center, edge.radius):
				return False
			continue
		
		if get_side_of_line(position, edge.p1, edge.p2) < 1:
			return False
		
	return True


def is_in_conical_surface(position: tuple[np.float64, np.float64, np.float64], hsurface: list[Edge], eae: np.float64) -> Optional[Callable[[np.float64, np.float64], np.float64]]:
	r"""Checks if ``position`` is in or on the boundary of a conical surface around the horizontal surface defined by ``hsurface``

	:param tuple[np.float64, np.float64, np.float64] position: a 3D coordinate point
	:param list[Edge] hsurface: a list of ``Edges`` defining a horizontal surface
	:param np.float64 eae: the established airport elevation
	:return Optional[Callable[[np.float64, np.float64], np.float64]]: a function that is the equation of a 3D surface in the form of ``z = f(x,y)`` bounding ``position`` from above
	"""

	# conical surface starts at 150 ft above the established airport elevation
	if position[2] < eae + 150:
		return None

	# conical surface is generated from the perimeter of the horizontal surface
	for edge in hsurface:
		# at curved portions of the horizontal surface, the conical surface is actually conical
		if type(edge) is Arc:
			# this lower bound cone is technically just a flat circle at z = eae + 150
			cone1 = get_cone(t3d(edge.center, eae + 150), edge.radius, eae + 150)

			cone2 = get_cone(t3d(edge.center, eae + 150), edge.radius + 4000, eae + 350)
			z1 = cone1(position[0], position[1])
			z2 = cone2(position[0], position[1])
			if z2 <= position[2] and position[2] <= z1:
				return cone1
			continue
		
		# for straight portions of the horizontal surface, the conical surface is just a wedge (i.e. a right triangular prism)
		distance = distance_to_line(t2d(position), edge.p1, edge.p2)
		t = create_right_triangle(edge.p1, edge.p2, np.float64(4000))[0]
		t = t3d(t, eae + 350)

		p13d = t3d(edge.p1, eae + 150)
		p23d = t3d(edge.p2, eae + 150)

		plane = get_plane(p13d, p23d, t)

		if distance <= 4000 and is_within_segment(t2d(position), edge.p1, edge.p2) and position[2] <= plane(position[0], position[1]):
			return plane
		
	return None


def is_in_approach_surface(position: tuple[np.float64, np.float64, np.float64], asurface: list[tuple[np.float64, np.float64]], approach_dimensions: dict[str, np.float64], eae: np.float64) -> Optional[Callable[[np.float64, np.float64], np.float64]]:
	r"""Checks if ``position`` is in or on the boundary of an approach surface defined by ``asurface``

	:param tuple[np.float64, np.float64, np.float64] position: a 3D coordinate point
	:param list[tuple[np.float64, np.float64]] asurface: a list of 2D vertices bounding the approach surface
	:param dict[str, np.float64] approach_dimensions: the dimensions of the approach surface as returned by ``Runway.calc_approach_dimensions``
	:param np.float64 eae: the established airport elevation
	:return Optional[Callable[[np.float64, np.float64], np.float64]]: a function that is the equation of a 3D surface in the form of ``z = f(x,y)`` bounding ``position`` from above
	"""

	p1 = t3d(asurface[0], eae)
	p2 = t3d(asurface[1], eae)

	if approach_dimensions["type"] == ApproachTypes.PRECISION_INSTRUMENT:
		# check if within the 2D projection of the approach surface first before checking height
		if not is_in_polygon(t2d(position), asurface, force_ccw=True):
			return None

		h = eae + approach_dimensions["primary_slope"] * approach_dimensions["primary_length"]
		p31 = t3d(asurface[3], h)
		h += approach_dimensions["secondary_slope"] * approach_dimensions["secondary_length"]
		p32 = t3d(asurface[3], h)

		midpoint = ((asurface[0][0] + asurface[1][0]) / 2, (asurface[0][1] + asurface[1][1]) / 2)
		t = create_right_triangle(asurface[0], midpoint, approach_dimensions["primary_length"])[0]
		projection = proj((position[0] - midpoint[0], position[1] - midpoint[1]), (t[0] - midpoint[0], t[1] - midpoint[1]))
		projection = (projection[0] + midpoint[0], projection[1] + midpoint[1])
		if calc_distance(projection, midpoint) <= approach_dimensions["primary_length"]:
			plane = get_plane(p1, p2, p31)
			if position[2] <= plane(position[0], position[1]):
				return plane
		else:
			plane = get_plane(p1, p2, p32)
			if position[2] <= plane(position[0], position[1]):
				return plane
	else:
		h = eae + approach_dimensions["slope"] * approach_dimensions["length"]
		p3 = t3d(asurface[3], h)
		plane = get_plane(p1, p2, p3)
		
		if is_in_polygon(t2d(position), asurface, force_ccw=True) and position[2] <= plane(position[0], position[1]):
			return plane
	
	return None


def is_in_transitional_surface(position: tuple[np.float64, np.float64, np.float64], tsurface: list[tuple[np.float64, np.float64]], eae: np.float64) -> Optional[Callable[[np.float64, np.float64], np.float64]]:
	r"""Checks if ``position`` is in or on the boundary of a transitional surface defined by ``tsurface`` 

	:param tuple[np.float64, np.float64, np.float64] position: a 3D coordinate point
	:param list[tuple[np.float64, np.float64]] tsurface: a list of 2D vertices bounding the transitional surface
	:param np.float64 eae: the established airport elevation
	:return Optional[Callable[[np.float64, np.float64], np.float64]]: a function that is the equation of a 3D surface in the form ``z = f(x,y)`` bounding ``position`` from above
	"""

	p1 = t3d(tsurface[0], eae)
	p2 = t3d(tsurface[-1], eae)
	p3 = t3d(tsurface[2], eae + 150)
	
	plane = get_plane(p1, p2, p3)
	if is_in_polygon(t2d(position), tsurface, force_ccw=True) and position[2] <= plane(position[0], position[1]):
		return plane

	return None


def get_zone_information(position: tuple[np.float64, np.float64, np.float64], runways: list[Runway], eae: np.float64) -> dict[str, str]:
	r"""Gets the information about the imaginary zone that ``position`` is in

	:param list[Runway] runways: a list of runways
	:param tuple[np.float64, np.float64, np.float64] position: a 3D coordinate
	:param np.float64 eae: the established airport elevation of the airport containing ``runways``
	:return dict[str, str]: a mapping of info to its value (e.g. ``"zone": "Transitional Surface"``)
	"""
	
	info = {}
	build_limit = eae
	info["zone"] = "N/A"

	hsurface = get_horizontal_surface_edges(runways)
	in_hsurface = True
	if not is_in_horizontal_surface(t2d(position), hsurface):
		in_hsurface = False

	if not in_hsurface:
		func = is_in_conical_surface(position, hsurface, eae)
		
		if not func is None:
			z = func(position[0], position[1])
			build_limit = z
			info["zone"] = "Conical"
			info["build_limit"] = z
	else:
		info["zone"] = "Horizontal"
		info["build_limit"] = build_limit

	for runway in runways:
		approach_dimensions = runway.calc_approach_dimensions()
		psurface = get_primary_surface_vertices(runway)
		asurfaces = get_approach_surface_vertices(approach_dimensions, psurface)
		tsurfaces = get_transitional_surface_vertices(psurface, asurfaces)
		
		if in_hsurface:
			t = list(psurface.values())
			v = []
			for i in t:
				for j in i:
					v.append(j)
			
			if is_in_polygon(t2d(position), v):
				info["runway"] = runway.name
				info["zone"] = "Primary"
				info["build_limit"] = eae
				return info
			
			for tsurface in tsurfaces:
				func = is_in_transitional_surface(position, tsurface, eae)
				if func is None:
					continue
				
				z = func(position[0], position[1])
				if z > build_limit:
					build_limit = z
					info["runway"] = runway.name
					info["zone"] = "Transitional"
					info["build_limit"] = build_limit
		
		for end, asurface in list(asurfaces.items()):
			ainfo = approach_dimensions[end]
			func = is_in_approach_surface(position, asurface, ainfo, eae)
			if func is None:
				continue
			
			z = func(position[0], position[1])
			if z > build_limit:
				build_limit = z
				info["runway"] = runway.name
				info["zone"] = "Approach"
				info["end"] = end.name
				info["build_limit"] = build_limit

	return info