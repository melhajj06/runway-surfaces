import numpy as np
from shapely.geometry import LineString

# extends a line segment defined by {p1} and {p2} by {amount} in both directions
#
# param p1: a 2D coordinate point of a line segment's endpoint
# param p2: a 2D coordinate point of a line segment's other endpoint
# param amount: the amount to extend the line segment by
#
# return: two tuples representing the extended line segment's endpoints 
def extend_points_in_both_directions(p1: tuple, p2: tuple, amount):
	t1 = get_higher_point(p1, p2)
	t2 = get_lower_point(p1, p2)

	p0a = np.array([0, 0])
	p0b = np.subtract(t2, t1)

	# if the line is horizontal (0 slope), no need to do complex math
	if p0b[0] == 0 and p0b[1] == 0:
		if p1[0] < p2[0]:
			return (np.subtract(p1, (amount, 0), np.add(p2, (amount, 0))))
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
	p1b[1] = 0  # mathematically should be 0
				# set to 0 to avoid floating precision weirdness

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


# cet2cr -> right-side common external tangent of two circles

# gets the common external tangent line of two circles of radii {r1} and {r2} 
# respectively where each circle is centered on {c1} and {c2} respectively.
# the external tangent line returned will be on the right hand side 
# of the line defined by {c1} and {c2} in that order.
#
# param c1: a 2D coordinate point representing the centerpoint of a circle
# param r1: the radius of the first circle
# param c2: a 2D coordinate point representing the centerpoint of a circle
# param r2: the radius of the second circle
#
# return: the two points on either circle defining the right-sided common external tangent line
def cet2cr(c1, r1, c2, r2):
	a = c2[1] - c1[1]
	b = c1[0] - c2[0]
	c = r2 - r1
	m = np.linalg.norm(np.array([a, b]))
	theta = -np.arctan(a/b) - np.arcsin(c/m)

	f = 1
	if r2 > r1:
		f = -1

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


def segments_intersect(p1, p2, q1, q2):
	l1 = LineString([p1, p2])
	l2 = LineString([q1, q2])
	
	return l1.intersects(l2)


# gets the point with a greater y-value
#
# param a: a 2D coordinate point
# param b: a 2D coordinate point
#
# return: the coordinate point with the greater y-value
def get_higher_point(a, b):
	return b if b[1] > a[1] else a

# gets the point with a lesser y-value
#
# param a: a 2D coordinate point
# param b: a 2D coordinate point
#
# return: the coordinate point with the lesser y-value
def get_lower_point(a, b):
	return b if b[1] < a[1] else a


def sign(x):
	return -1 if x < 0 else 1
