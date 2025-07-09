# Polygon Module
# 
# author: melhajj06
# version: 07-09-2025 (MM-DD-YYYY)

# gets the leftmost point from {points}
#
# param points: a list of tuples of the form (x, y) representing coordinate points
#
# return: a tuple that is the leftmost point
def find_leftmost_point(points: list[tuple]):
    if len(points) == 0:
        return 0, 0
    
    leftmost_point = (points[0][0], points[0][1])
    if len(points) == 1:
        return leftmost_point
    
    for x, y in points[1:]:
        if x < leftmost_point[0]:
            leftmost_point = (x, y)
    
    return leftmost_point

# gets the rightmost point from {points}
#
# param points: a list of tuples of the form (x, y) representing coordinate points
#
# return: a tuple that is the leftmost point
def find_rightmost_point(points: list[tuple]):
    if len(points) == 0:
        return 0, 0
    
    rightmost_point = (points[0][0], points[0][1])
    if len(points) == 1:
        return rightmost_point
    
    for x, y in points[1:]:
        if x > rightmost_point[0]:
            rightmost_point = (x, y)
    
    return rightmost_point

# gets all the points in {points} above the straight line passing through {point1} and {point2}
#
# param points: a list of tuples of the form (x, y) representing coordinate points
# param point1: coordinate that a line passes through
# param point2: another coordinate that the same line passes through
#
# return: a list of tuples that contain all of the points above a line
def get_points_above(points: list[tuple], point1: tuple, point2: tuple):
    points_above = []
    
    def line(xval):
        return ((point2[1] - point1[1]) / (point2[0] - point1[0])) * (xval - point1[0]) + point1[1]
    
    for x, y in points:
        if (x, y) == point1 or (x, y) == point2:
            continue
        elif y >= line(x):
            points_above.append((x, y))
    
    return points_above

# gets all the points in {points} below the straight line passing through {point1} and {point2}
#
# param points: a list of tuples of the form (x, y) representing coordinate points
# param point1: a tuple representing a coordinate that a line passes through
# param point2: a tuple representing another coordinate that the same line passes through
#
# return: a list of tuples that contain all of the points below a line
def get_points_below(points: list[tuple], point1: tuple, point2: tuple):
    points_above = []
    
    def line(xval):
        return ((point2[1] - point1[1]) / (point2[0] - point1[0])) * (xval - point1[0]) + point1[1]
    
    for x, y in points:
        if (x, y) == point1 or (x, y) == point2:
            continue
        elif y < line(x):
            points_above.append((x, y))
    
    return points_above

# key for sorting tuples by their first entry
#
# param point: a tuple representing a coordinate point
#
# return: a number that is the first entry in {point}
def sort_point(point):
    return point[0]

# sorts all points in {points} such that, when connecting each subsequent point, a polygon without self-intersections is formed
#
# param points: a list of tuples of the form (x, y) representing coordinate points
#
# return: a list of tuples representing coordinate points of a polygon in counterclockwise direction
def get_polygon_vertices(points):
    l = find_leftmost_point(points)
    r = find_rightmost_point(points)
    above = get_points_above(points, l, r)
    above.sort(reverse=True, key=sort_point)
    below = get_points_below(points, l, r)
    below.sort(key=sort_point)
    
    polygon = [l]
    for p in below:
        polygon.append(p)
    polygon.append(r)
    for p in above:
        polygon.append(p)
    polygon.append(l)
    
    return polygon