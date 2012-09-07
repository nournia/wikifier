from Wikipedia import Wikipedia
import json, collections, shelve, os

def loadTranslation():
	return shelve.open(Wikipedia.directory + 'translation.db', 'r')

def loadLinks():
	return shelve.open(Wikipedia.directory + 'links.db', 'r')

def loadDestinations():
	return shelve.open(Wikipedia.directory + 'destinations.db', 'r')

def indexTranslation():

	translation = {}

	for article in Wikipedia():
		translation[article['url']] = article['id'][0]

	# write index
	db = shelve.open(Wikipedia.directory + 'translation.db')
	for key, value in translation.iteritems():
		db[key.encode('utf8')] = value
	db.close()

def indexLinks():

	def processArticle(article):
		phrases = set([])
		url = article['id'][0]
		for link in article['annotations']:
			
			phrase = link['s'].lower()
			phrases.add(phrase)
			probability[phrase] += 1

			linkUrl = translation.get(link['u'].encode('utf8'))
			if linkUrl:
				# index links of a phrase
				links[phrase][linkUrl] += 1

				# index destinations of an article
				destinations[url].add(linkUrl)

		# count occurances of phrase in text
		text = article['text'].lower()
		for phrase in phrases:
			occurances[phrase] += text.count(phrase)


	# load translations index
	translation = loadTranslation()

	# indexed by phrase
	links = collections.defaultdict(lambda: collections.defaultdict(lambda: 0))
	probability = collections.defaultdict(lambda: 0)
	occurances = collections.defaultdict(lambda: 0)

	# indexed by link
	destinations = collections.defaultdict(lambda: set([]))

	# loop through articles
	for article in Wikipedia():
		processArticle(article)

	# compute phrase probabilities
	for phrase in probability:
		links[phrase]['-1'] = round(float(probability[phrase]) / occurances[phrase], 2)

	for key, value in destinations.iteritems():
		destinations[key] = list(value)

	# write indexes
	db = shelve.open(Wikipedia.directory + 'links.db')
	for key, value in links.iteritems():
		db[key.encode('utf8')] = dict([(int(k), v) for k, v in value.items()])
	db.close()

	db = shelve.open(Wikipedia.directory + 'destinations.db')
	for key, value in destinations.iteritems():
		db[str(key)] = value
	db.close()


import xml.etree.cElementTree as et

def resolveRedirects():

	translation = shelve.open(Wikipedia.directory + 'translation.db', 'w')
	
	eid, etitle = '', ''
	for event, element in et.iterparse(Wikipedia.directory + 'redir.xml'):
		if element.tag == 'id':
			eid = element.text
		elif element.tag == 'name':
			etitle = element.text
		elif element.tag == 'from':
			key = etitle.encode('utf-8') if eid == 'unknown' else None
		elif element.tag == 'to':
			if eid != 'unknown' and key and not translation.get(key):
				translation[key] = int(eid)
				key = etitle.encode('utf-8')
				if not translation.get(key): translation[key] = int(eid)
			else:
				print key, eid, translation.get(key)

import lucene
from lucene import SimpleFSDirectory, IndexWriter, File, Document, Field, EnglishAnalyzer, Version

def indexDocuments():
	# empty index directory
	indexDir = Wikipedia.directory + 'index/'
	for filename in os.listdir(indexDir): os.remove(indexDir + filename)

	# index documents
	lucene.initVM()
	version = Version.LUCENE_CURRENT
	analyzer = EnglishAnalyzer(version)
	writer = IndexWriter(SimpleFSDirectory(File(indexDir)), analyzer, True, IndexWriter.MaxFieldLength.LIMITED)

	for article in Wikipedia():
		doc = Document()
		doc.add(Field('id', str(article['id'][0]), Field.Store.YES, Field.Index.NOT_ANALYZED))
		doc.add(Field('title', article['url'], Field.Store.YES, Field.Index.NOT_ANALYZED))
		doc.add(Field('content', article['text'], Field.Store.NO, Field.Index.ANALYZED))
		writer.addDocument(doc)

	print 'Optimization'
	writer.optimize()
	writer.close()


if __name__ == '__main__':
	
	print 'Index Translation'
	indexTranslation()
	resolveRedirects()

	print 'Index Links'
	indexLinks()
	
	print 'Index Documents'
	indexDocuments()
