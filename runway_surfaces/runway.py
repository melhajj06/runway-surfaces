from enum import Enum
import numpy as np


class RunwayTypes(Enum):
	UTILITY = 0
	VISUAL = 1
	NON_PRECISION_INSTRUMENT = 2
	PRECISION_INSTRUMENT = 3

class ApproachTypes(Enum):
	VISUAL = 0
	NON_PRECISION_INSTRUMENT = 1
	PRECISION_INSTRUMENT = 2

class RunwayEnd:
	def __init__(self, point: tuple, approach_type: ApproachTypes):
		self.point = point
		self.approach_type = approach_type


class Runway:
	def __init__(self, runway_type: RunwayTypes, approach_type: ApproachTypes, end1: RunwayEnd, end2: RunwayEnd, width: float, elevation, special_surface=False, visibility_minimums=0):
		self.runway_type = runway_type
		self.approach_type = approach_type
		self.end1 = end1
		self.end2 = end2
		# TODO: is length and width really necessary?
		self.length = np.linalg.norm(np.subtract(end1.point, end2.point))
		self.width = width
		self.elevation = elevation
		self.special_surface = special_surface
		self.visiblity_minimums = visibility_minimums
	
	
	def calc_psurface_width(self) -> int:
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
	
	# regulations on approach surfaces dimensions are all over the fucking place
	def calc_approach_dimensions(self):
		dim = {"end1": {}, "end2": {}}
		end1_type = self.end1.approach_type
		end2_type = self.end2.approach_type

		dim["end1"]["type"] = end1_type
		dim["end2"]["type"] = end2_type
		
		if end1_type == RunwayTypes.VISUAL:
			if self.runway_type == RunwayTypes.UTILITY:
				dim["end1"]["width"] = 1250
			else:
				dim["end1"]["width"] = 1500
			dim["end1"]["length"] = 5000
			dim["end1"]["slope"] = 0.05
		elif end1_type == ApproachTypes.NON_PRECISION_INSTRUMENT:
			if self.runway_type == RunwayTypes.UTILITY:
				dim["end1"]["width"] = 2000
				dim["end1"]["length"] = 5000
				dim["end1"]["slope"] = 0.05
			else:
				dim["end1"]["length"] = 10000
				dim["end1"]["slope"] = 1.0 / 34.0
				if self.visiblity_minimums > 0.75:
					dim["end1"]["width"] = 3500
				elif self.visiblity_minimums == 0.75:
					dim["end1"]["width"] = 4000
		elif end1_type == ApproachTypes.PRECISION_INSTRUMENT:
			dim["end1"]["width"] = dim["end2"]["width"] = 16000
			dim["end1"]["length"] = 60000
			dim["end1"]["primary_slope"] = 0.02
			dim["end1"]["secondary_slope"] = 0.025
			
		if end2_type == RunwayTypes.VISUAL:
			if self.runway_type == RunwayTypes.UTILITY:
				dim["end2"]["width"] = 1250
			else:
				dim["end2"]["width"] = 1500
			dim["end2"]["length"] = 5000
			dim["end2"]["slope"] = 0.05
		elif end2_type == ApproachTypes.NON_PRECISION_INSTRUMENT:
			if self.runway_type == RunwayTypes.UTILITY:
				dim["end2"]["width"] = 2000
				dim["end2"]["length"] = 5000
				dim["end2"]["slope"] = 0.05
			else:
				dim["end2"]["length"] = 10000
				dim["end2"]["slope"] = 1.0 / 34.0
				if self.visiblity_minimums > 0.75:
					dim["end2"]["width"] = 3500
				elif self.visiblity_minimums == 0.75:
					dim["end2"]["width"] = 4000
		elif end2_type == ApproachTypes.PRECISION_INSTRUMENT:
			dim["end2"]["width"] = dim["end2"]["width"] = 16000
			dim["end2"]["length"] = 50000
			dim["end2"]["primary_slope"] = 0.02
			dim["end2"]["secondary_slope"] = 0.025
		
		return dim
		