from enum import Enum

class Units(Enum):
	DEGREES = 0
	METERS = 1
	FEET = 2

class RunwayType(Enum):
	UTILITY = 0
	VISUAL = 1
	NON_PRECISION_INSTRUMENT = 2
	PRECISION_INSTRUMENT = 3

class ApproachTypes(Enum):
	VISUAL = 0
	NON_PRECISION_INSTRUMENT = 1

class Runway:
	def __init__(self, units, runway_type, approach_type, mid1: tuple, mid2: tuple, length, width, special_surface=False):
		self.units = units
		self.runway_type = runway_type
		self.approach_type = approach_type
		self.pos1 = mid1
		self.pos2 = mid2
		self.length = length,
		self.width = width
		self.special_surface = special_surface


	


