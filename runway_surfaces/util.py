import numpy as np
from sympy.geometry import Point2D, Line2D, Segment2D, Polygon, Point
from functools import cmp_to_key
from typing import Callable

def extend_point_in_one_direction(p1: tuple[np.float64, np.float64], p2: tuple[np.float64, np.float64], amount: np.float64) -> tuple[np.float64, np.float64]:
	r"""Extends ``p2`` in the direction of ``p1`` to ``p2`` by ``amount``

	Scales a vector going from ``p1`` to ``p2`` such that the scaled vector's magnitude is the magnitude of the original vector
	plus ``amount`` and is in the same direction of the original vector.
	The coordinate point at the head of this scaled vector is returned.

	:param tuple[np.float64, np.float64] p1: a 2D coordinate point
	:param tuple[np.float64, np.float64] p2: a 2D coordinate point
	:param np.float64 amount: the amount to extend ``p2`` by
	:return tuple[np.float64, np.float64]: a 2D coordinate point that is ``amount`` away from ``p2`` in the direction of ``p1`` to ``p2``
	"""

	# translate to the origin
	v = np.subtract(p2, p1)
	length = np.linalg.norm(v)

	if length == 0:
		return tuple()
	
	# let $$ \vec{v} $$ be the scaled vector
	# let l be param `amount`
	# scale the vector such that $$ |\vec{v}| = \overrightarrow{P_{1}P_{2}} + l $$
	a = amount / length + 1
	v = a * v

	# translate back
	v = np.add(v, p1)

	return tuple(v)


def extend_points_in_both_directions(p1: tuple[np.float64, np.float64], p2: tuple[np.float64, np.float64], amount: np.float64) -> list[tuple[np.float64, np.float64]]:
	r"""Extends a line segment
	
	Extends a line segment defined by ``p1`` and ``p2`` by ``amount`` (i.e. away from each other).
	Consider a vector, v, going from ``p1`` to the returned extension of p1. Then, the magnitude/length of v is ``amount``.
	
	:param tuple[np.float64, np.float64] p1: a 2D coordinate point
	:param tuple[np.float64, np.float64] p2: a 2D coordinate point
	:param np.float64 amount: the amount to extend the line segment by
	:return list[tuple[np.float64, np.float64]]: the endpoints of the extended line segment 
	"""

	extended2 = extend_point_in_one_direction(p1, p2, amount)
	extended1 = extend_point_in_one_direction(p2, p1, amount)

	if len(extended1) == 0 or len(extended2) == 0:
		return []
	
	return [extended1, extended2]


def cet2cr(c1: tuple[np.float64, np.float64], r1: np.float64, c2: tuple[np.float64, np.float64], r2: np.float64) -> list[tuple[np.float64, np.float64]]:
	r"""Gets the common external tangent line on the right side of two circles

	Two non-overlapping circles have 4 common tangent lines: 2 external and 2 internal.
	The external tangent lines do not cross the line passing through each circle's center,
	while the internal tangent lines does.
	When creating a vector going from ``c1`` to ``c2``, there is a right side and a left side.
	``cet2cr`` translates to "right-side common external tangent of two circles".
	
	:param tuple[np.float64, np.float64] c1: a 2D centerpoint of a circle
	:param np.float64 r1: the radius of the circle centered at ``c1``
	:param tuple[np.float64, np.float64] c2: a 2D centerpoint of a circle
	:param np.float64 r2: the radius of the circle centered at ``c2``
	:return list[tuple[np.float64, np.float64]]: a 2D coordinate point on each circle the common tangent line passes through
	"""

	# if the centers of each circle are identical, then there are no possible common tangents
	# or, if one circle is completely inside of another, then there are also no possible common tangents
	if np.array_equal(c1, c2):
		return []
	elif circle_in_circle(c1, r1, c2, r2):
		return []
	
	# solutions thanks to the help John Alexiou on Math Stack Exchange
	# https://math.stackexchange.com/a/211854
	# when using arbitrary points for everything in the method described in the solution above,
	#
	#
	# a tangent line in standard form $$ ax + by + c = 0 $$ has coefficients $$ \begin{bmatrix} -sin(\theta)\\ cos(\theta)\\ -y_0cos(\theta) + x_0sin(\theta) \pm r\end{bmatrix} $$
	#
	#
	# where $$ x_0 $$ and $$ y_0 $$ are the x and y coordinates of the circle's center respectively, and $$ \theta $$ is the
	# angle the tangent line makes from horizontal.
	# switching the sign of $$ r $$ switches the direction the tangent line travels around the circle when increasing $$ \theta $$.
	#
	#
	# solving the equation $$ -y_0cos(\theta) + x_0sin(\theta) \pm r_1 = -y_1cos(\theta) + x_1sin(\theta) \pm r_2 $$ yields the formula
	# $$ (y_1 - y_0)cos(\theta) + (x_0 - x_1)sin(\theta) = \pm r2 \mp r1 $$ where theta can be solved using the identity $$ acos(\theta) + bsin(\theta) = Rsin(\theta + \alpha) $$
	# where $$ R = \sqrt{a^2 + b^2} $$ and $$ \alpha = \arctan{(\frac{a}{b})} $$
	
	a = c2[1] - c1[1]
	b = c1[0] - c2[0]
	c = r2 - r1
	m = np.linalg.norm(np.array([a, b]))
	# arcsin is odd, so negating it is equivalent to negating c which just changes the side of the circles the common tangent line is on
	theta = -np.arctan(a/b) - np.arcsin(c/m)

	# if r1 > r2, the inequalities need to be flipped
	f = 1
	if r1 > r2:
		f = -1

	# the comments with colors correspond to color coded lines on desmos when i was constructing these points
	# see: https://desmos.com/calculator
	if c1[1] >= c2[1]:
		if r1 < r2:
			if c1[0] >= c2[0]:
				# green
				return [(c1[0] - r1 * np.sin(theta), c1[1] + np.sqrt(-(r1**2) * ((np.sin(theta))**2 - 1))), (c2[0] - r2 * np.sin(theta), c2[1] + np.sqrt(-(r2**2) * ((np.sin(theta))**2 - 1)))]
			elif c1[0] >= c2[0] - r2 + r1:
				# red
				return [(c1[0] + r1 * np.sin(theta), c1[1] + np.sqrt(-(r1**2) * ((np.sin(theta))**2 - 1))), (c2[0] + r2 * np.sin(theta), c2[1] + np.sqrt(-(r2**2) * ((np.sin(theta))**2 - 1)))]
			else:
				# orange
				return [(c1[0] + r1 * np.sin(theta), c1[1] - np.sqrt(-(r1**2) * ((np.sin(theta))**2 - 1))), (c2[0] + r2 * np.sin(theta), c2[1] - np.sqrt(-(r2**2) * ((np.sin(theta))**2 - 1)))]
		else:
			if c1[0] < c2[0]:
				# orange
				return [(c1[0] + r1 * np.sin(theta), c1[1] - np.sqrt(-(r1**2) * ((np.sin(theta))**2 - 1))), (c2[0] + r2 * np.sin(theta), c2[1] - np.sqrt(-(r2**2) * ((np.sin(theta))**2 - 1)))]
			elif c1[0] <= c2[0] - r2 + r1:
				# blue
				return [(c1[0] - r1 * np.sin(theta), c1[1] - np.sqrt(-(r1**2) * ((np.sin(theta))**2 - 1))), (c2[0] - r2 * np.sin(theta), c2[1] - np.sqrt(-(r2**2) * ((np.sin(theta))**2 - 1)))]		
			else:
				# green
				return [(c1[0] - r1 * np.sin(theta), c1[1] + np.sqrt(-(r1**2) * ((np.sin(theta))**2 - 1))), (c2[0] - r2 * np.sin(theta), c2[1] + np.sqrt(-(r2**2) * ((np.sin(theta))**2 - 1)))]
	else:
		if r1 < r2:
			if c1[0] < c2[0]:
				# orange
				return [(c1[0] + r1 * np.sin(theta), c1[1] - np.sqrt(-(r1**2) * ((np.sin(theta))**2 - 1))), (c2[0] + r2 * np.sin(theta), c2[1] - np.sqrt(-(r2**2) * ((np.sin(theta))**2 - 1)))]
			elif c1[0] <= c2[0] + r2 - r1:
				# blue
				return [(c1[0] - f * r1 * np.sin(theta), c1[1] - np.sqrt(-(r1**2) * ((np.sin(theta))**2 - 1))), (c2[0] - f * r2 * np.sin(theta), c2[1] - f * np.sqrt(-(r2**2) * ((np.sin(theta))**2 - 1)))]
			else:
				# green
				return [(c1[0] - r1 * np.sin(theta), c1[1] + np.sqrt(-(r1**2) * ((np.sin(theta))**2 - 1))), (c2[0] - r2 * np.sin(theta), c2[1] + np.sqrt(-(r2**2) * ((np.sin(theta))**2 - 1)))]	
		else:
			if c1[0] >= c2[0]:
				# green
				return [(c1[0] - r1 * np.sin(theta), c1[1] + np.sqrt(-(r1**2) * ((np.sin(theta))**2 - 1))), (c2[0] - r2 * np.sin(theta), c2[1] + np.sqrt(-(r2**2) * ((np.sin(theta))**2 - 1)))]	

			elif c1[0] >= c2[0] + r2 - r1:
				# red
				return [(c1[0] + r1 * np.sin(theta), c1[1] + np.sqrt(-(r1**2) * ((np.sin(theta))**2 - 1))), (c2[0] + r2 * np.sin(theta), c2[1] + np.sqrt(-(r2**2) * ((np.sin(theta))**2 - 1)))]
			else:
				# orange
				return [(c1[0] + r1 * np.sin(theta), c1[1] - np.sqrt(-(r1**2) * ((np.sin(theta))**2 - 1))), (c2[0] + r2 * np.sin(theta), c2[1] - np.sqrt(-(r2**2) * ((np.sin(theta))**2 - 1)))]


def get_higher_point(a: tuple[np.float64, np.float64], b: tuple[np.float64, np.float64]) -> tuple[np.float64, np.float64]:
	"""Gets the point with the larger y-value
	
	:param tuple[np.float64, np.float64] a: a 2D coordinate point
	:param tuple[np.float64, np.float64] b: a 2D coordinate point
	:return tuple[np.float64, np.float64]: the higher point
	"""

	return b if b[1] > a[1] else a


def get_lower_point(a: tuple[np.float64, np.float64], b: tuple[np.float64, np.float64]) -> tuple[np.float64, np.float64]:
	"""Gets the point with the smaller y-value
	
	:param tuple[np.float64, np.float64] a: a 2D coordinate point
	:param tuple[np.float64, np.float64] b: a 2D coordinate point
	:return tuple[np.float64, np.float64]: the lower point
	"""

	return b if b[1] < a[1] else a


# checks if the circle defined by {c1} and {r1} is entirely within the circle defined by {c2} and {r2} or vice versa
# 
# param c1 {tuple}: a 2D coordinate representing the centerpoint of a circle
# param r1 {np.float64}: the radius of the circle centered at {c1}
# param c2 {tuple}: a 2D coordinate representing the centerpoint of a circle
# param r2 {np.float64}: the radius of the circle centered at {c2}
#
# return {bool}: a boolean of whether either circle is entirely within the other
def circle_in_circle(c1: tuple[np.float64, np.float64], r1: np.float64, c2: tuple[np.float64, np.float64], r2: np.float64) -> bool:
	r"""Checks if either circle is completely inside the other
	
	:param tuple[np.float64, np.float64] c1: a 2D centerpoint of a circle
	:param np.float64 r1: the radius of the circle centered at ``c1``
	:param tuple[np.float64, np.float64] c2: a 2D centerpoint of a circle
	:param np.float64 r2: the radius of the circle centered at ``c2``
	:return bool: whether either circle is completely inside the other
	"""

	# if the distance between the centerpoints plus the radius of circle #1 is less than or equal to the radius of the circle #2,
	# then circle #1 is inside circle #2
	d = calc_distance(c1, c2)
	if r1 >= (d + r2) or r2 >= (d + r1):
		return True
	
	return False


def compute_centerpoint(points: list[tuple[np.float64, np.float64]]) -> tuple[np.float64, np.float64]:
	"""Gets the center of a list of coordinate points
	
	The center or average point of a list of points has an x-value of the average of all the x-values,
	and a y-value of the average of all the y-values.
	
	:param list[tuple[np.float64, np.float64]] points: a list of 2D coordinate points
	:return tuple[np.float64, np.float64]: the average point
	"""

	if len(points) == 0:
		return tuple()
	
	xsum = 0
	ysum = 0

	for point in points:
		xsum += point[0]
		ysum += point[1]

	return (np.float64(xsum) / len(points), np.float64(ysum) / len(points))


def sort_directional(points: list[tuple[np.float64, np.float64]], ccw: bool = True) -> None:
	"""Sorts a list of 2D coordinate points either clockwise or counter-clockwise
	
	A set of 2D coordinate points can be in any order and are usually random.
	But, they can be ordered so that they're in clockwise or counter-clockwise order about their center or average point.
	
	:param list[tuple[np.float64, np.float64]] points: a list of 2D coordinate points
	:param bool ccw: whether to set the direction to counter-clockwise, defaults to True
	"""

	if len(points) == 0:
		return
	
	center = compute_centerpoint(points)
	assert len(center) != 0

	# comparison function thanks to ciamej and arghavan on Stack Overflow
	# https://stackoverflow.com/a/6989383
	def compare_points(a, b):
		if a[0] - center[0] >= 0 and b[0] - center[0] < 0:
			return -1
		elif a[0] - center[0] < 0 and b[0] - center[0] >= 0:
			return 1
		elif a[0] - center[0] == 0 and b[0] - center[0] == 0:
			if a[1] - center[1] >= 0 or b[1] - center[1] >= 0:
				return np.sign(b[1] - a[1])
			return np.sign(a[1] - b[1])
		
		det = np.linalg.det([np.subtract(a, center), np.subtract(b, center)])
		if det != 0:
			return np.sign(det)
		
		d1 = calc_distance(a, center)
		d2 = calc_distance(b, center)
		return np.sign(d2 - d1)
	
	points.sort(key=cmp_to_key(compare_points), reverse=ccw)


def lisl(a: tuple[np.float64, np.float64], b: tuple[np.float64, np.float64], c: tuple[np.float64, np.float64], d: tuple[np.float64, np.float64]) -> list[Point2D]:
	r"""Checks if the line passing through ``a`` and ``b`` intersects the line pasing through ``c`` and ``d``
	``lisl`` translates to "line intersects line".

	:param tuple[np.float64, np.float64] a: a 2D coordinate point
	:param tuple[np.float64, np.float64] b: a 2D coordinate point
	:param tuple[np.float64, np.float64] c: a 2D coordinate point
	:param tuple[np.float64, np.float64] d: a 2D coordinate point
	:return list[Point2D]: a list of every intersection point
	"""

	line1 = Line2D(Point2D(a), Point2D(b))
	line2 = Line2D(Point2D(c), Point2D(d))
	return line1.intersection(line2)


def lis_4p(a: tuple[np.float64, np.float64], b: tuple[np.float64, np.float64], c: tuple[np.float64, np.float64], d: tuple[np.float64, np.float64]) -> list[Point2D]:
	r"""Checks if the line passing through ``a`` and ``b`` intersects the line segment defined by ``c`` and ``d``

	``list_4p`` translates to "line intersects segment 4 points".
	
	:param tuple[np.float64, np.float64] a: a 2D coordinate point
	:param tuple[np.float64, np.float64] b: a 2D coordinate point
	:param tuple[np.float64, np.float64] c: a 2D coordinate point
	:param tuple[np.float64, np.float64] d: a 2D coordinate point
	:return list[Point2D]: a list of every intersection point
	"""

	line = Line2D(Point2D(a), Point2D(b))
	segment = Segment2D(Point2D(c), Point2D(d))
	return line.intersection(segment)


def lis_3p(a: tuple[np.float64, np.float64], slope: np.float64, c: tuple[np.float64, np.float64], d: tuple[np.float64, np.float64]) -> list[Point2D]:
	r"""Checks if the line passing through ``a`` with ``slope`` intersects the line segment defined by ``c`` and ``d``

	``list_3p`` translates to "line intersects segment 3 points".
	
	:param tuple[np.float64, np.float64] a: a 2D coordinate point
	:param tuple[np.float64, np.float64] slope: the slope of a 2D line
	:param tuple[np.float64, np.float64] c: a 2D coordinate point
	:param tuple[np.float64, np.float64] d: a 2D coordinate point
	:return list[Point2D]: a list of every intersection point
	"""

	line = Line2D(a, slope)
	segment = Segment2D(Point2D(c), Point2D(d))
	return line.intersection(segment)

def line_intersects_circle(a: np.float64, b: np.float64, c: np.float64, p: tuple[np.float64, np.float64], r: np.float64) -> list[tuple[np.float64, np.float64]]:
	r"""Checks if a line intersects the circle centered at ``c`` with radius ``r``
	
	The line in question is a line in standard form :math:`ax + by + c = 0` where a = ``a``, b = ``b``, and c = ``c``.
	When solving the system of equations, a quadratic is solved using the quadratic formula.
	If the determinant is greater than or equal to 0, then the result will be a real number.
	Subsequently, the line and circle will intersect (ignoring edge cases).
	
	:param np.float64 a: `a` in the standard-form line equation
	:param np.float64 b: `b` in the standard-form line equation
	:param np.float64 c: `c` in the standard-form line equation
	:param tuple[np.float64, np.float64] p: a 2D centerpoint of a circle
	:param np.float64 r: the radius of the circle centered at ``p``
	:return list[tuple[np.float64, np.float64]]: a list of every intersection point
	"""

	# if a and b are 0, then it isn't a line
	if a == 0 and b == 0:
		return []
	# vertical line
	elif b == 0:
		x = -c/a
		if p[0] - r <= x and x <= p[0] + r:
			temp = np.sqrt(r**2 - (x - p[0])**2)
			return [(x, p[1] + temp), (x, p[1] - temp)]
		return []
	# horizontal line
	elif a == 0:
		y = -c/b
		if p[1] - r <= y and y <= p[1] + r:
			temp = np.sqrt(r**2 - (y - p[1])**2)
			return [(p[0] + temp, y), (p[0] - temp, y)]
		return []
	
	# solving the system:
	#
	# $$ \left\{\begin{array}{l} ax + by = 0\\ (x - x_{0})^2 + (y - y_0)^2 = r^2 \end{array}\right. $$
	#
	# gives the following solution
	#
	#
	# $$ \large\begin{array}{l} x = \frac{-\beta \pm \sqrt{\beta^2 - \alpha\gamma}}{\alpha}\\ y = \frac{-\alpha c - a(-\beta \pm \sqrt{\beta^2 - \alpha\gamma})}{\alpha b}\\ \end{array} $$
	#
	#
	# where
	#
	#
	# $$ \begin{array}{l} \alpha = a^2 + b^2\\ \beta = ac + aby_{0} - b^2x_{0}\\ \gamma = b^2(x_{0}^2+y_{0}^2-r^2) + 2bcy_{0} + c^2 \end{array} $$
	#
	#

	alpha = a**2 + b**2
	beta = a * c + a * b * p[1] - p[0] * b**2
	gamma = (b**2) * ((p[0])**2 + (p[1])**2 - r**2) + 2 * c * b * p[1] + c**2
	disc = beta**2 - alpha * gamma

	if disc < 0:
		return []
	elif disc == 0:
		return [(-beta/alpha, (-alpha * c + a * beta) / (alpha * b))]
	
	temp = np.sqrt(disc)
	x1, y1 = (-beta + temp) / alpha, (-alpha * c - a * (-beta + temp)) / (alpha * b)
	x2, y2 = (-beta - temp) / alpha, (-alpha * c - a * (-beta - temp)) / (alpha * b)

	return [(x1, y1), (x2, y2)]


def create_right_triangle(a: tuple[np.float64, np.float64], b: tuple[np.float64, np.float64], w: np.float64) -> list[tuple[np.float64, np.float64]]:
	r"""Creates a right triangle given two coordinate points

	Given two coordinate points ``a`` and ``b`` where A = ``a`` and B = ``b``,
	a right triangle, ABC, is created such that the vector AB is orthogonal to the vector BC,
	and the magnitude of the vector BC is ``w``.
	The coordinate point C is returned.

	:param tuple[np.float64, np.float64] a: a 2D coordinate point
	:param tuple[np.float64, np.float64] b: a 2D coordinate point
	:param np.float64 w: the length of the 2nd leg of the desired right triangle
	:return list[tuple[np.float64, np.float64]]: a list of 2D coordinates that can be the third point in the triangle defined by ``a`` and ``b``
	"""

	# $$ \triangle ABC $$ is created such that $$ \overrightarrow{AB} \perp \overrightarrow{BC} $$ and $$ |\overrightarrow{BC}| = w $$ where w = ``w``.

	dx = b[0] - a[0]
	dy = b[1] - a[1]
	l = calc_distance(a, b)

	if l == 0:
		return []
	
	# 90 deg
	c1 = (b[0] - (w * dy) / l, b[1] + (w * dx) / l)
	# -90 deg
	c2 = (b[0] + (w * dy) / l, b[1] - (w * dx) / l)

	return [c1, c2]


def calc_dist_for_height(slope: np.float64, height: np.float64) -> np.float64:
	r"""Calculates the distance required in the 2D plane to reach a z-value of ``height`` with ``slope``

	:param np.float64 slope: the slope of the line in the xz-plane and yz-plane
	:param np.float64 height: the desired z-value
	:return np.float64: the distance in the 2D plane required to reach ``height`` with ``slope``
	"""

	if slope == 0 or height == 0:
		return np.float64(0)

	return (np.float64(height) / slope) * np.sqrt(2)


def calc_distance(p1: tuple[np.float64, np.float64], p2: tuple[np.float64, np.float64]) -> np.float64:
	r"""Calculates the distance between two 2D coordinate points

	:param tuple[np.float64, np.float64] p1: a 2D coordinate point
	:param tuple[np.float64, np.float64] p2: a 2D coordinate point
	:return np.float64: the distance between ``p1`` and ``p2``
	"""
	
	return np.float64(np.linalg.norm(np.subtract(p1, p2)))


def get_polygon_direction(vertices: list[tuple[np.float64, np.float64]]) -> int:
	r"""Gets the orientation of the polygon defined by ``vertices``

	If ``vertices`` are ordered clockwise, then ``1`` is returned.
	If ``vertices`` are ordered counterclockwise, then ``-1`` is returned.
	If ``vertices`` are collinear, then ``0`` is returned.

	:param list[tuple[np.float64, np.float64]] vertices: a list of 2D coordinates representing vertices of a polygon
	:return int: the orientation of ``vertices``
	"""

	a = 0
	for i in range(len(vertices)):
		v1 = vertices[i]
		v2 = vertices[(i + 1) % len(vertices)]
		a += (v2[0] - v1[0]) * (v2[1] + v1[1])
	
	return np.sign(a)


def get_side_of_line(a: tuple[np.float64, np.float64], b: tuple[np.float64, np.float64], c: tuple[np.float64, np.float64]) -> int:
	"""Gets which side point ``c`` is relative to the line going from ``a`` to ``b``

	If ``c`` is on the left, then ``1`` is returned.
	If ``c`` is on the right, then ``-1`` is returned.
	If ``c`` is collinear, then ``0`` is returned.

	:param tuple[np.float64, np.float64] a: a 2D coordinate
	:param tuple[np.float64, np.float64] b: a 2D coordinate
	:param tuple[np.float64, np.float64] c: a 2D coordinate
	:return int: what side ``c`` is on relative to the line from ``a`` to ``b``
	"""

	return np.sign(np.linalg.det([[b[0] - a[0], c[0] - a[0]], [b[1] - a[1], c[1] - a[1]]]))


def is_in_polygon(point: tuple[np.float64, np.float64], vertices: list[tuple[np.float64, np.float64]], force_ccw: bool = False, force_cw: bool = False) -> bool:
	r"""Checks if ``point`` is inside or on the boundary of the polygon defined by ``vertices``

	:param tuple[np.float64, np.float64] point: a 2D coordinate point
	:param list[tuple[np.float64, np.float64]] vertices: a list of 2D coordinate points representing vertices of a polygon
	:return bool: whether or not ``point`` is in the polygon
	:param bool force_ccw: whether to force the function to treat ``vertices`` as already sorted in counterclockwise direction, defaults to False
	:param bool force_cw: whether to force the function to treat ``vertices`` as already sorted in clockwise direction, defaults to False
	:return bool: whether ``point`` is inside or on the boundary of the polygon
	"""
	
	if len(vertices) < 3:
		return False

	direction = 0
	if force_ccw:
		direction = -1
	elif force_cw:
		direction = 1
	else:
		direction = get_polygon_direction(vertices)

	if direction == 0:
		return point[1] == ((vertices[1][0] - vertices[0][0])/(vertices[1][1] - vertices[0][1])) * (point[0] - vertices[0][0]) + vertices[0][1]

	for i in range(len(vertices)):
		if direction == 1:
			if get_side_of_line(vertices[i], vertices[(i + 1) % len(vertices)], point) > -1:
				return False
		else:
			if get_side_of_line(vertices[i], vertices[(i + 1) % len(vertices)], point) < 1:
				return False

	return True


def is_in_circle(point: tuple[np.float64, np.float64], c: tuple[np.float64, np.float64], r: np.float64) -> bool:
	r"""Checks if ``point`` is inside or on the boundary of the circle centered at ``c`` with radius ``r``

	:param tuple[np.float64, np.float64] point: a 2D coordinate point
	:param tuple[np.float64, np.float64] c: a 2D coordinate point
	:param np.float64 r: the radius of the circle centered at ``c``
	:return bool: whether ``point`` is inside or on the boundary of the circle
	"""

	return bool(calc_distance(point, c) <= r)


def get_cone(c: tuple[np.float64, np.float64, np.float64], r: np.float64, h: np.float64) -> Callable[[np.float64, np.float64], np.float64]:
	r"""Gets the equation for a cone that is centered at ``c`` and reaches a radius of ``r`` at ``h``

	Given a cone centered at ``c``,
	the circle created by slicing the cone with the plane ``z = h1`` will have a radius ``r1``

	:param tuple[np.float64, np.float64, np.float64] c: a 3D coordinate point
	:param np.float64 r1: the radius of the cone at ``z = h1``
	:param np.float64 h1: a z-value
	:return Callable[[np.float64, np.float64, np.float64, np.float64], np.float64]: the 3D equation of the cone as a lambda
	"""

	# a cone can be described with the equation: $$ (x - a)^2 + (y - b)^2 = d(z - c)^2 $$
	# at $$ z = z_{0} $$, the radius of the cone should be $$ r $$
	# using this, the following equation for $$ d $$ can be derived:
	#
	# $$ d = (\frac{r}{z_{0} - c})^2 $$
	#
	# then, the equations for either cone can be derived:
	#
	# $$ z = \sqrt{\frac{(x - a)^2 + (y - b)^2}{d}} + c $$
	#
	#

	# if the desired $$ z $$ at radius $$ r $$ is equal to the the z-value of $$ c $$,
	# then it's just a flat plane of the form $$ z = n, n \in \mathbb{R} $$
	if h == c[2]:
		return lambda x, y: h

	return lambda x, y: np.sqrt(((x - c[0])**2 + (y - c[1])**2)) / (r / (h - c[2])) + c[2]
	

def distance_to_line(point: tuple[np.float64, np.float64], a: tuple[np.float64, np.float64], b: tuple[np.float64, np.float64]) -> np.float64:
	r"""Calculates the distance from ``point`` to the closest point on the line passing through ``a`` and ``b``

	:param tuple[np.float64, np.float64] point: a 2D coordinate point
	:param tuple[np.float64, np.float64] a: a 2D coordinate point
	:param tuple[np.float64, np.float64] b: a 2D coordinate point
	:return np.float64: the distance to the closest point on the line from ``point``
	"""

	if a == 0 and b == 0:
		return np.float64(-1)

	dx = np.float64(b[0] - a[0])
	dy = np.float64(b[1] - a[1])

	if dx == 0:
		return np.abs(point[0] - a[0])
	
	if dy == 0:
		return np.abs(point[1] - a[1])
	
	m = dx / dy
	i = -1
	j = 1 / m
	k = -(a[1] / m + a[0])

	return np.abs(i * point[0] + j * point[1] + k) / (np.sqrt(i**2 + j**2))


def cross(v1: tuple[np.float64, np.float64, np.float64], v2: tuple[np.float64, np.float64, np.float64]) -> tuple:
	r"""Calculates the cross product of two 3D vectors

	:param tuple[np.float64, np.float64, np.float64] v1: a 3D vector
	:param tuple[np.float64, np.float64, np.float64] v2: a 3D vector
	:return tuple: a 3D vector that is perpendicular to ``v1`` and ``v2``
	"""

	return (np.linalg.det([[v1[1], v1[2]], [v2[1], v2[2]]]), np.linalg.det([[v1[0], v1[2]], [v2[0], v2[2]]]), np.linalg.det([[v1[0], v1[1]], [v2[0], v2[1]]]))


def get_plane(a: tuple[np.float64, np.float64, np.float64], b: tuple[np.float64, np.float64, np.float64], c: tuple[np.float64, np.float64, np.float64]) -> Callable[[np.float64, np.float64], np.float64]:
	r"""Gets the equation for the plane containing ``a``, ``b``, and ``c``

	:param tuple[np.float64, np.float64, np.float64] a: a 3D coordinate point
	:param tuple[np.float64, np.float64, np.float64] b: a 3D coordinate point
	:param tuple[np.float64, np.float64, np.float64] c: a 3D coordinate point
	:return tuple[np.float64, np.float64, np.float64]: the 3D equation of the plane containing ``a``, ``b``, and ``c``
	"""

	v = cross((b[0] - a[0], b[1] - a[1], b[2] - a[2]), (c[0] - a[0], c[1] - a[1], c[2] - a[2]))
	return lambda x, y: a[2] - ((v[0] * (x - a[0]) + v[1] * (y - a[1])) / v[2])


def t3d(p: tuple[np.float64, np.float64], z: np.float64) -> tuple[np.float64, np.float64, np.float64]:
	r"""Extends the 2D coordinate ``p`` into a 3D coordinate with z-value ``z``

	"t3d" translates to "to 3D"

	:param tuple[np.float64, np.float64] p: a 2D coordinate point
	:param np.float64 z: a z-value
	:return tuple[np.float64, np.float64, np.float64]: a 3D coordinate point with z = ``z``
	"""

	return (p[0], p[1], z)


def t2d(p: tuple[np.float64, np.float64, np.float64]) -> tuple[np.float64, np.float64]:
	r"""Projects ``p`` onto the 2D plane

	"t2d" translates to "to 2D"

	:param tuple[np.float64, np.float64, np.float64] p: a 3D coordinate point
	:return tuple[np.float64, np.float64]: a 2D coordinate point
	"""

	return (p[0], p[1])


def is_within_segment(p: tuple[np.float64, np.float64], a: tuple[np.float64, np.float64], b: tuple[np.float64, np.float64]) -> bool:
	r"""Checks if ``p`` is contained by endpoints of ``segment``

	``p`` is contained by the endpoints of ``segment`` iff ``p`` is between the lines perpendicular to ``segment``
	passing through either endpoint of ``segment``

	:param tuple[np.float64, np.float64] p: a 2D coordinate point
	:param tuple[np.float64, np.float64] a: a 2D coordinate point
	:param tuple[np.float64, np.float64] b: a 2D coordinate point
	:return bool: whether ``p`` is contained by the endpoints of ``segment``
	"""

	t1 = np.subtract(b, a)
	t2 = np.subtract(p, a)

	c = np.dot(t1, t2) / (np.linalg.norm(t1) * np.linalg.norm(t2))

	return 0 <= c and c <= 1


def proj(a: tuple[np.float64, np.float64], b: tuple[np.float64, np.float64]) -> tuple[np.float64, np.float64]:
	r"""Project the vector ``a`` onto the vector ``b``

	:param tuple[np.float64, np.float64] a: a 2D vector
	:param tuple[np.float64, np.float64] b: a 2D vector
	:return tuple[np.float64, np.float64]: the projection of ``a`` onto ``b``
	"""

	return (np.dot(a, b) / np.linalg.norm(b)**2) * b


def degrees_to_feet(coord1: tuple[np.float64, np.float64], ref_coord: tuple[np.float64, np.float64]) -> tuple[np.float64, np.float64]:
	r"""Converts ``coord1`` to feet

	:param tuple[np.float64, np.float64] coord1: a coordinate in degrees
	:param tuple[np.float64, np.float64] ref_coord: a coordinate in degrees that isn't ``coord``
	:return tuple[np.float64, np.float64]: ``coord1`` converted to feet
	"""

	# Calculate the difference in degrees
	delta_lat = ref_coord[0] - coord1[0]
	delta_lon = ref_coord[1] - coord1[1]

	# Use average latitude as reference for longitude scaling
	avg_lat = (coord1[0] + ref_coord[0]) / 2.0
	avg_lat_rad = np.radians(avg_lat)

	# Approximate conversion factors
	FEET_PER_DEG_LAT = 364000  # approx. feet per degree latitude
	FEET_PER_DEG_LON = 364000 * np.cos(avg_lat_rad)

	# Convert degree differences to feet
	delta_lat_feet = delta_lat * FEET_PER_DEG_LAT
	delta_lon_feet = delta_lon * FEET_PER_DEG_LON

	return delta_lat_feet, delta_lon_feet