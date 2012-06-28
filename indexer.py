import Wikipedia as wiki
import sys, json, collections

def processArticle(article):
	phrases = set([])
	for link in article['annotations']:
		
		phrase = link['s'].lower()
		phrases.add(phrase)
		
		# index links of a phrase
		links[phrase][link['u']] += 1
		probability[phrase] += 1

		# index destinations of an article
		if link['u'] in translation:
			destinations[article['url']].add(translation[link['u']])

	# count occurances of phrase in text
	text = article['text'].lower()
	for phrase in phrases:
		occurances[phrase] += text.count(phrase)

if len(sys.argv) > 1 and sys.argv[1] == 'translation':

	# index translations
	translation = {}

	for article in wiki.Wikipedia('data/articles'):
		translation[article['url']] = article['id'][0]

	json.dump(translation, open('data/translation.txt', 'w'))

else:

	# load translations index
	translation = json.load(open('data/translation.txt'))

	# indexed by phrase
	links = collections.defaultdict(lambda: collections.defaultdict(lambda: 0))
	probability = collections.defaultdict(lambda: 0)
	occurances = collections.defaultdict(lambda: 0)

	# indexed by link
	destinations = collections.defaultdict(lambda: set([]))

	# loop through articles
	for article in wiki.Wikipedia('data/articles'):
		processArticle(article)

	# compute phrase probabilities
	for phrase in probability:
		probability[phrase] = float(probability[phrase]) / occurances[phrase]

	for key, value in destinations.iteritems():
		destinations[key] = list(value)

	# write indexes
	json.dump(links, open('data/links.txt', 'w'))
	json.dump(probability, open('data/probability.txt', 'w'))
	json.dump(destinations, open('data/destinations.txt', 'w'))
