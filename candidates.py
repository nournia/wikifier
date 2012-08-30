from indexer import loadLinks, loadTranslation

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


import lucene
from lucene import SimpleFSDirectory, System, File, Document, Field, StandardAnalyzer, IndexSearcher, Version, QueryParser
from urllib2 import quote

class OccuredCandidates:
	indexDir = 'data/index'
	max_candidates = 10

	def __init__(self):
		lucene.initVM()
		self._lversion = Version.LUCENE_30
		self._analyzer = StandardAnalyzer(self._lversion)
		self._searcher = IndexSearcher(SimpleFSDirectory(File(self.indexDir)))

		self._translation = loadTranslation()
		self._links = loadLinks()

	def find(self, phrase):
		phrase = phrase.lower().encode('utf8')
		query = ' '.join(['+'+ word for word in phrase.split(' ')]);
		query = QueryParser(self._lversion, 'contents', self._analyzer).parse(query)
		hits = self._searcher.search(query, self.max_candidates)

		# todo stem query
		# print "%d documents for '%s':" % (hits.totalHits, query)

		# todo put article_id in lucene index instead of translating document title

		links = {}
		for hit in hits.scoreDocs:
			title = quote(self._searcher.doc(hit.doc).get("title").encode('utf-8').replace(' ', '_')).replace('%28', '(').replace('%29', ')')
			if title in self._translation:
				links[self._translation[title]] = hit.score
			# else: print title

		return self._links[phrase].get('', 0), links

	def clear_links(self, annotations):
		return filter(lambda annotation: annotation['links'] and max(annotation['links'].values()) > 1, annotations)
