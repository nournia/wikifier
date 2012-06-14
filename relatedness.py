import json
from math import *

class WLVM:
	""" computing semantic relatedness with Wikipedia Link Vector model """

	def __init__(self):
		""" read indexes """

		self._destinations = json.load(open('data/destinations.txt'))

		# count of all articles
		self._W = log(len(json.load(open('data/translation.txt'))))


	def relatedness(self, a, b):
		""" link-based semantic relatedness between two articles which only considers incoming links following original paper

		a, b: article
		returns relatedness of them
		"""

		if (a not in self._destinations) or (b not in self._destinations): return 0

		A, B = set(self._destinations[a]), set(self._destinations[b])
		intersection = len(A & B); 
		if not intersection: return 0

		return (log(max(len(A), len(B))) - log(intersection)) / (self._W - log(min(len(A), len(B))))

class ESA:
	""" computing semantic relatedness with Explicit Semantic Analysis model """

