import numpy as np
from shapely.geometry import LineString


def extend_points_in_both_directions(p1: tuple, p2: tuple, amount):
	t1 = get_higher_point(p1, p2)
	t2 = get_lower_point(p1, p2)

	p0a = np.array([0, 0])
	p0b = np.subtract(t2, t1)

	# if the line is horizontal (0 slope) (small optimization)
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


def get_higher_point(a, b):
	return b if b[1] > a[1] else a


def get_lower_point(a, b):
	return b if b[1] < a[1] else a


def sign(x):
	return -1 if x < 0 else 1
