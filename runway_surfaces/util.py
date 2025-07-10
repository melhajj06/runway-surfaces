import numpy as np
from shapely.geometry import LineString


def extend_points_in_both_directions(p1: tuple, p2: tuple, amount):
	t1 = get_higher_point(p1, p2)
	t2 = get_lower_point(p1, p2)

	p0a = np.array([0, 0])
	p0b = np.subtract(t2, t2)  #np.array([t2[0] - t1[0], t2[1] - t1[1]])

	# rotate the points to align with the x axis
	theta = -np.acos(p0b[0] / np.linalg.norm(p0b))
	rotation_matrix = [
		[np.cos(theta), -np.sin(theta)],
		[np.sin(theta), np.cos(theta)]
	]
	p1a = p0a
	p1b = np.matmul(p0b, rotation_matrix)
	# p1b[1] = 0  # set to 0 to avoid

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
	return (np.add(p2a, t1), np.add(p2b, t1))  #(p2a[0] + t1[0], p2a[1] + t1[1]), (p2b[0] + t1[0], p2b[1] + t1[1]))


def calc_perp_intersection(p1, p2, radius):
	delta_x = p2[0] - p1[0]
	delta_y = p2[1] - p1[1]
	x = ((radius * delta_y) / np.linalg.norm(np.subtract(p1, p2))) + p1[0]
	y = (-delta_x / delta_y) * (x - p1[0]) + p1[1]

	return (x, y)


def segments_intersect(p1, p2, q1, q2):
	l1 = LineString([p1, p2])
	l2 = LineString([q1, q2])
	
	return l1.intersects(l2)


def get_higher_point(a, b):
	return b if b[1] > a[1] else a


def get_lower_point(a, b):
	return b if b[1] < a[1] else a
