from Wikipedia import Wikipedia
import json, collections, shelve

def loadTranslation():
	return shelve.open(Wikipedia.directory + 'translation.db', 'r')

def loadLinks():
	return json.load(open(Wikipedia.directory + 'links.txt'))

def loadDestinations():
	return json.load(open(Wikipedia.directory + 'destinations.txt'))

def convertTranslation():
	db = shelve.open(Wikipedia.directory + 'translation.db')
	translation = json.load(open(Wikipedia.directory + 'translation.txt'))
	for key, value in translation.iteritems():
		db[key.encode('utf8')] = value
	db.close()

def indexTranslation():
	
	translation = {}

	for article in Wikipedia():
		translation[article['url']] = article['id'][0]

	json.dump(translation, open(Wikipedia.directory + 'translation.txt', 'w'))

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
		links[phrase][''] = round(float(probability[phrase]) / occurances[phrase], 2)

	for key, value in destinations.iteritems():
		destinations[key] = list(value)

	# write indexes
	json.dump(links, open(Wikipedia.directory + 'links.txt', 'w'))
	json.dump(destinations, open(Wikipedia.directory + 'destinations.txt', 'w'))
