import numpy as np
from sympy.geometry import Point2D, Line2D, Segment2D
from functools import cmp_to_key


def extend_points_in_both_directions(p1: tuple[float, float], p2: tuple[float, float], amount: float) -> tuple:
	"""Extends a line segment
	
	Extends a line segment defined by ``p1`` and ``p2`` by ``amount`` (i.e. away from each other).
	Consider a vector, v, going from ``p1`` to the returned extension of p1. Then, the magnitude/length of v is ``amount``.
	
	:param (tuple[float, float]) p1: a 2D coordinate point
	:param (tuple[float, float]) p2: a 2D coordinate point
	:param (float) amount: the amount to extend the line segment by
	:return (tuple[float, float]): the endpoints of the extended line segment 
	"""

	t1 = get_higher_point(p1, p2)
	t2 = get_lower_point(p1, p2)

	p0a = np.array([0, 0])
	p0b = np.subtract(t2, t1)

	# if the line is horizontal (0 slope), no need to do complex math
	if p0b[0] == 0 and p0b[1] == 0:
		if p1[0] < p2[0]:
			return (np.subtract(p1, (amount, 0)), np.add(p2, (amount, 0)))
		else:
			return (np.add(p1, (amount, 0)), np.subtract(p2, (amount, 0)))


	# rotate the points to align with the x axis
	theta = -np.acos(p0b[0] / np.linalg.norm(p0b))
	rotation_matrix = [
		[np.cos(theta), -np.sin(theta)],
		[np.sin(theta), np.cos(theta)]
	]
	p1a = p0a
	p1b = np.matmul(p0b, rotation_matrix)

	# mathematically should be 0
	# set to 0 to avoid floating precision weirdness
	p1b[1] = 0

	# add the distance
	p1b[0] = p1b[0] + amount
	p1a[0] = p1a[0] - amount

	# rotate it back to original orientation
	reverse_rotation_matrix = [
		[np.cos(theta), -np.sin(-theta)],
		[np.sin(-theta), np.cos(theta)]
	]
	p2a = np.matmul(p1a, reverse_rotation_matrix)
	p2b = np.matmul(p1b, reverse_rotation_matrix)

	# translate it back to original position
	return (np.add(p2a, t1), np.add(p2b, t1))


def cet2cr(c1: tuple[float, float], r1: float, c2: tuple[float, float], r2: float) -> tuple[tuple[float, float], tuple[float, float]]:
	"""Gets the common external tangent line on the right side of two circles

	Two non-overlapping circles have 4 common tangent lines: 2 external and 2 internal.
	The external tangent lines do not cross the line passing through each circle's center,
	while the internal tangent lines does.
	When creating a vector going from ``c1`` to ``c2``, there is a right side and a left side.
	``cet2cr`` translates to \"right-side common external tangent of two circles\".
	
	:param (tuple[float, float]) c1: a 2D centerpoint of a circle
	:param (float) r1: the radius of the circle centered at ``c1``
	:param (tuple[float, float]) c2: a 2D centerpoint of a circle
	:param (float) r2: the radius of the circle centered at ``c2``
	:return (tuple[tuple[float, float], tuple[float, float]]): a 2D coordinate point on each circle the common tangent line passes through
	"""

	# if the centers of each circle are identical, then there are no possible common tangents
	# or, if one circle is completely inside of another, then there are also no possible common tangents
	if np.array_equal(c1, c2):
		return tuple()
	elif circle_in_circle(c1, r1, c2, r2):
		return tuple()
	
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

	# signs on conditionals need to be flipped if r2 is greater than r1
	f = 1
	if r2 > r1:
		f = -1

	# the comments with colors correspond to color coded lines on desmos when i was constructing these points
	# see: https://desmos.com/calculator
	if c1[1] >= c2[1]:
		if c1[0] >= c2[0]:
			if c1[0] < c2[0] - (f * r2) + (f * r1):
				# blue
				return ((c1[0] - r1 * np.sin(theta), c1[1] - np.sqrt(-(r1**2) * ((np.sin(theta))**2 - 1))), (c2[0] - r2 * np.sin(theta), c2[1] - np.sqrt(-(r2**2) * ((np.sin(theta))**2 - 1))))
			else:
				# green
				return ((c1[0] - r1 * np.sin(theta), c1[1] + np.sqrt(-(r1**2) * ((np.sin(theta))**2 - 1))), (c2[0] - r2 * np.sin(theta), c2[1] + np.sqrt(-(r2**2) * ((np.sin(theta))**2 - 1))))
		else:
			# orange
			return ((c1[0] + r1 * np.sin(theta), c1[1] - np.sqrt(-(r1**2) * ((np.sin(theta))**2 - 1))), (c2[0] + r2 * np.sin(theta), c2[1] - np.sqrt(-(r2**2) * ((np.sin(theta))**2 - 1))))
	else:
		if c1[0] < c2[0]:
			if c1[0] > c2[0] + (f * r2) - (f * r1):
				# red
				return ((c1[0] + r1 * np.sin(theta), c1[1] + np.sqrt(-(r1**2) * ((np.sin(theta))**2 - 1))), (c2[0] + r2 * np.sin(theta), c2[1] + np.sqrt(-(r2**2) * ((np.sin(theta))**2 - 1))))
			else:
				# orange
				return ((c1[0] + r1 * np.sin(theta), c1[1] - np.sqrt(-(r1**2) * ((np.sin(theta))**2 - 1))), (c2[0] + r2 * np.sin(theta), c2[1] - np.sqrt(-(r2**2) * ((np.sin(theta))**2 - 1))))
		else:
			# green
			return ((c1[0] - r1 * np.sin(theta), c1[1] + np.sqrt(-(r1**2) * ((np.sin(theta))**2 - 1))), (c2[0] - r2 * np.sin(theta), c2[1] + np.sqrt(-(r2**2) * ((np.sin(theta))**2 - 1))))


def get_higher_point(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
	"""Gets the point with the larger y-value
	
	:param (tuple[float, float]) a: a 2D coordinate point
	:param (tuple[float, float]) b: a 2D coordinate point
	:return (tuple[float, float]): the higher point
	"""

	return b if b[1] > a[1] else a


def get_lower_point(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
	"""Gets the point with the smaller y-value
	
	:param (tuple[float, float]) a: a 2D coordinate point
	:param (tuple[float, float]) b: a 2D coordinate point
	:return (tuple[float, float]): the lower point
	"""

	return b if b[1] < a[1] else a


# checks if the circle defined by {c1} and {r1} is entirely within the circle defined by {c2} and {r2} or vice versa
# 
# param c1 {tuple}: a 2D coordinate representing the centerpoint of a circle
# param r1 {float}: the radius of the circle centered at {c1}
# param c2 {tuple}: a 2D coordinate representing the centerpoint of a circle
# param r2 {float}: the radius of the circle centered at {c2}
#
# return {bool}: a boolean of whether either circle is entirely within the other
def circle_in_circle(c1: tuple[float, float], r1: float, c2: tuple[float, float], r2: float) -> bool:
	"""Checks if either circle is completely inside the other
	
	:param (tuple[float, float]) c1: a 2D centerpoint of a circle
	:param (float) r1: the radius of the circle centered at ``c1``
	:param (tuple[float, float]) c2: a 2D centerpoint of a circle
	:param (float) r2: the radius of the circle centered at ``c2``
	:return (bool): whether either circle is completely inside the other
	"""

	# if the distance between the centerpoints plus the radius of circle #1 is less than or equal to the radius of the circle #2,
	# then circle #1 is inside circle #2
	d = np.linalg.norm(np.subtract(c1, c2))
	if r1 >= (d + r2) or r2 >= (d + r1):
		return True
	
	return False


def compute_centerpoint(points: list[tuple[float, float]]) -> tuple[float, float]:
	"""Gets the center of a list of coordinate points
	
	The center or average point of a list of points has an x-value of the average of all the x-values,
	and a y-value of the average of all the y-values.
	
	:param (list[tuple[float, float]]) points: a list of 2D coordinate points
	:return (tuple[float, float]): the average point
	"""

	if len(points) == 0:
		return tuple()
	
	xsum = 0
	ysum = 0

	for point in points:
		xsum += point[0]
		ysum += point[1]

	return (xsum / len(points), ysum / len(points))


def sort_directional(points: list[tuple[float, float]], ccw: bool = True) -> None:
	"""Sorts a list of 2D coordinate points either clockwise or counter-clockwise
	
	A set of 2D coordinate points can be in any order and are usually random.
	But, they can be ordered so that they're in clockwise or counter-clockwise order about their center or average point.
	
	:param (list[tuple[float, float]]) points: _description_
	:param (bool) ccw: whether to set the direction to counter-clockwise, defaults to True
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
		
		d1 = np.linalg.norm(np.subtract(a, center))
		d2 = np.linalg.norm(np.subtract(b, center))
		return np.sign(d2 - d1)
	
	points.sort(key=cmp_to_key(compare_points), reverse=ccw)


def line_intersects_segment(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float], d: tuple[float, float]) -> list[Point2D]:
	"""Checks if the line passing through ``a`` and ``b`` intersects the line segment defined by ``c`` and ``d``
	
	:param (tuple[float, float]) a: a 2D coordinate point
	:param (tuple[float, float]) b: a 2D coordinate point
	:param (tuple[float, float]) c: a 2D coordinate point
	:param (tuple[float, float]) d: a 2D coordinate point
	:return (list[Point2D]): a list of every intersection point
	"""

	line = Line2D(Point2D(a), Point2D(b))
	segment = Segment2D(Point2D(c), Point2D(d))
	return line.intersection(segment)


def line_intersects_circle(a: float, b: float, c: float, p: tuple[float, float], r: float) -> list[tuple[float, float]]:
	"""Checks if a line intersects the circle centered at ``c`` with radius ``r``
	
	The line in question is a line in standard form :math:`ax + by + c = 0` where a = ``a``, b = ``b``, and c = ``c``.
	When solving the system of equations, a quadratic is solved using the quadratic formula.
	If the determinant is greater than or equal to 0, then the result will be a real number.
	Subsequently, the line and circle will intersect (ignoring edge cases).
	
	:param (float) a: `a` in the standard-form line equation
	:param (float) b: `b` in the standard-form line equation
	:param (float) c: `c` in the standard-form line equation
	:param (tuple[float, float]) p: a 2D centerpoint of a circle
	:param (float) r: the radius of the circle centered at ``p``
	:return (list[tuple[float, float]]): a list of every intersection point
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