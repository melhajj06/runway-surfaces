from enum import Enum
import numpy as np

class Units(Enum):
	DEGREES = 0
	METERS = 1
	FEET = 2

class RunwayTypes(Enum):
	UTILITY = 0
	VISUAL = 1
	NON_PRECISION_INSTRUMENT = 2
	PRECISION_INSTRUMENT = 3

class ApproachTypes(Enum):
	VISUAL = 0
	NON_PRECISION_INSTRUMENT = 1

class RunwayEnd:
	def __init__(self, point: tuple, approach_type: ApproachTypes):
		self.point = point
		self.approach_type = approach_type


class Runway:
	def __init__(self, units: Units, runway_type: RunwayTypes, approach_type: ApproachTypes, end1: RunwayEnd, end2: RunwayEnd, width, elevation, special_surface=False, visibility_minimums=0):
		self.units = units
		self.runway_type = runway_type
		self.approach_type = approach_type
		self.end1 = end1
		self.end2 = end2
		self.length = np.linalg.norm(np.subtract(end1.point, end2.point))
		self.width = width
		self.elevation = elevation
		self.special_surface = special_surface
		self.visiblity_minimums = visibility_minimums
	
	
	def calc_psurface_width(self):
		visual_only = self.end1.approach_type == ApproachTypes.VISUAL and self.end2.approach_type == ApproachTypes.VISUAL
		has_npia = self.end1.approach_type == ApproachTypes.NON_PRECISION_INSTRUMENT or self.end2.approach_type == ApproachTypes.NON_PRECISION_INSTRUMENT

		if self.runway_type == RunwayTypes.UTILITY:
			if visual_only:
				return 250
			return 500
		elif self.runway_type == RunwayTypes.VISUAL:
			if visual_only:
				return 500
		elif self.runway_type == RunwayTypes.NON_PRECISION_INSTRUMENT:
			if has_npia:
				if self.visiblity_minimums >= 0.75:
					return 1000
			elif self.visiblity_minimums > 0.75:
				return 500
		elif self.runway_type == RunwayTypes.PRECISION_INSTRUMENT:
			return 1000
		
		# primary surface width was not specificied at this point
		return 0
	
	def calc_hsurface_radius(self):
		if self.runway_type == RunwayTypes.UTILITY or self.runway_type == RunwayTypes.VISUAL:
			return 5000
		
		return 10000
	
	def calc_approach_width(self):
		visual_only = self.end1.approach_type == ApproachTypes.VISUAL and self.end2.approach_type == ApproachTypes.VISUAL
		has_npia = self.end1.approach_type == ApproachTypes.NON_PRECISION_INSTRUMENT or self.end2.approach_type == ApproachTypes.NON_PRECISION_INSTRUMENT

		if self.runway_type == RunwayTypes.UTILITY:
			if visual_only:
				return 1250
			else:
				return 2000
		elif visual_only:
			return 1500
		
		if self.runway_type == RunwayTypes.NON_PRECISION_INSTRUMENT:
			if has_npia and self.visiblity_minimums >= 0.75:
				return 4000
			elif self.visiblity_minimums > 0.75:
				return 3500
		
		return 16000
	
	def calc_approach_distance(self):
		if self.runway_type == RunwayTypes.VISUAL or self.runway_type == RunwayTypes.UTILITY:
			return 5000
		elif self.runway_type == RunwayTypes.NON_PRECISION_INSTRUMENT:
			return 10000
		else:
			return 50000
		