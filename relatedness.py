import os
from math import *
from indexer import loadDestinations

class WLVMRelatedness:
	""" computing semantic relatedness with Wikipedia Link Vector model """

	def __init__(self):
		""" read indexes """

		self._destinations = loadDestinations()

		# count of all articles
		self._W = log(len(self._destinations))

	def relatedness(self, a, b):
		""" link-based semantic relatedness between two articles which only considers incoming links following original paper

		a, b: article
		returns relatedness of them
		"""

		a, b = str(a), str(b)
		if (a not in self._destinations) or (b not in self._destinations): return 0

		A, B = set(self._destinations[a]), set(self._destinations[b])
		intersection = len(A & B); 
		if not intersection: return 0

		return (log(max(len(A), len(B))) - log(intersection)) / (self._W - log(min(len(A), len(B))))


class ESARelatedness:
	""" computing semantic relatedness with Explicit Semantic Analysis model """

	def relatedness(self, a, b):
		""" concept-based semantic relatedness between two string using Wikipedia articles through an external java module

		a, b: string
		returns relatedness of them
		"""

		res = os.popen("java -cp 'esa/*' edu.wiki.search.ESASearcher '%s' '%s'" % (a, b))
		res = float(res.readline())

		print a, b, res
		return res
