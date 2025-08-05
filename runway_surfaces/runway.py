from enum import Enum


class RunwayTypes(Enum):
	"""An enumeration of all the types of runways
	"""

	UTILITY = 0
	VISUAL = 1
	NON_PRECISION_INSTRUMENT = 2
	PRECISION_INSTRUMENT = 3


class ApproachTypes(Enum):
	"""An enumeration of all the types of approaches found at the ends of runways
	"""

	VISUAL = 0
	NON_PRECISION_INSTRUMENT = 1
	PRECISION_INSTRUMENT = 2


class RunwayEnd:
	"""Represents the end of a runway
	"""

	def __init__(self, point: tuple, approach_type: ApproachTypes):
		r"""Creates a new ``RunwayEnd`` object

		:param tuple point: the coordinate point of this endpoint of the runway
		:param ApproachTypes approach_type: the type of approach found at this end of the runway
		"""
		self.point = point
		self.approach_type = approach_type


class Runway:
	"""Represents an airport's runway
	"""

	def __init__(self, runway_type: RunwayTypes, end1: RunwayEnd, end2: RunwayEnd, special_surface: bool = False, visibility_minimums: int = 0):
		"""Creates a new ``Runway`` object

		:param RunwayTypes runway_type: the type of runway
		:param RunwayEnd end1: one endpoint of the runway
		:param RunwayEnd end2: the opposite endpoint of the runway
		:param bool special_surface: whether this runway is prepared with a special hard surface, defaults to False
		:param int visibility_minimums: the visibility minimums of the runway, defaults to 0
		"""

		self.runway_type = runway_type
		self.end1 = end1
		self.end2 = end2
		self.special_surface = special_surface
		self.visiblity_minimums = visibility_minimums
	
	
	def calc_psurface_width(self) -> int:
		"""Calculates the width of the primary surface given the information about this runway

		:return int: the width of the primary surface
		"""

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
	

	def calc_hsurface_radius(self) -> int:
		"""Calculates the radius from the runway's endpoints to the horizontal surface

		:return int: the radius of the runway to the horizontal surface
		"""
		if self.runway_type == RunwayTypes.UTILITY or self.runway_type == RunwayTypes.VISUAL:
			return 5000
		
		return 10000
	

	# regulations on approach surfaces dimensions are all over the fucking place
	def calc_approach_dimensions(self) -> dict[RunwayEnd, dict[str, float]]:
		"""Calculates the dimensions of the approaches at either end of the runway

		:return dict[RunwayEnd, dict[str, float]]: a mapping of the runway's end to its dimensions
		"""

		dim = {self.end1: {}, self.end2: {}}
		end1_type = self.end1.approach_type
		end2_type = self.end2.approach_type

		dim[self.end1]["type"] = end1_type
		dim[self.end2]["type"] = end2_type
		
		if end1_type == ApproachTypes.VISUAL:
			if self.runway_type == RunwayTypes.UTILITY:
				dim[self.end1]["width"] = 1250
			else:
				dim[self.end1]["width"] = 1500
			dim[self.end1]["length"] = 5000
			dim[self.end1]["slope"] = 0.05
		elif end1_type == ApproachTypes.NON_PRECISION_INSTRUMENT:
			if self.runway_type == RunwayTypes.UTILITY:
				dim[self.end1]["width"] = 2000
				dim[self.end1]["length"] = 5000
				dim[self.end1]["slope"] = 0.05
			else:
				dim[self.end1]["length"] = 10000
				dim[self.end1]["slope"] = 1.0 / 34.0
				if self.visiblity_minimums > 0.75:
					dim[self.end1]["width"] = 3500
				elif self.visiblity_minimums == 0.75:
					dim[self.end1]["width"] = 4000
		elif end1_type == ApproachTypes.PRECISION_INSTRUMENT:
			dim[self.end1]["width"] = dim[self.end2]["width"] = 16000
			dim[self.end1]["length"] = 50000
			dim[self.end1]["primary_slope"] = 0.02
			dim[self.end1]["secondary_slope"] = 0.025
			
		if end2_type == ApproachTypes.VISUAL:
			if self.runway_type == RunwayTypes.UTILITY:
				dim[self.end2]["width"] = 1250
			else:
				dim[self.end2]["width"] = 1500
			dim[self.end2]["length"] = 5000
			dim[self.end2]["slope"] = 0.05
		elif end2_type == ApproachTypes.NON_PRECISION_INSTRUMENT:
			if self.runway_type == RunwayTypes.UTILITY:
				dim[self.end2]["width"] = 2000
				dim[self.end2]["length"] = 5000
				dim[self.end2]["slope"] = 0.05
			else:
				dim[self.end2]["length"] = 10000
				dim[self.end2]["slope"] = 1.0 / 34.0
				if self.visiblity_minimums > 0.75:
					dim[self.end2]["width"] = 3500
				elif self.visiblity_minimums == 0.75:
					dim[self.end2]["width"] = 4000
		elif end2_type == ApproachTypes.PRECISION_INSTRUMENT:
			dim[self.end2]["width"] = dim[self.end2]["width"] = 16000
			dim[self.end2]["primary_length"] = 10000
			dim[self.end2]["secondary_length"] = 40000
			dim[self.end2]["primary_slope"] = 0.02
			dim[self.end2]["secondary_slope"] = 0.025
		
		return dim