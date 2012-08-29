from indexer import loadLinks

class LinkedCandidates:
	""" use linked words in dataset for candidate links """

	def __init__(self):
		self._links = loadLinks()

	def find(self, phrase):
		phrase = phrase.lower().encode('utf8')
		if not phrase in self._links: return {}
		links = self._links[phrase]
		probability = links.pop('', 0)
		return probability, links

	def clear_links(self, annotations):
		return filter(lambda annotation: len(annotation['links']) == 1, annotations)
