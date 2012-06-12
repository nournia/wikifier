import Wikipedia as wiki
import json, collections

# index by phrase
links = collections.defaultdict(lambda: collections.defaultdict(lambda: 0))
probabilities = collections.defaultdict(lambda: 0)
occurances = collections.defaultdict(lambda: 0)

# index by link
translations = {}
# sources = collections.defaultdict(lambda: [])
destinations = collections.defaultdict(lambda: [])

def processArticle(article):

	translations[article['url']] = article['id'][0]

	phrases = set([])
	for link in article['annotations']:
		
		phrase = link['s'].lower()
		phrases.add(phrase)
		
		# index links of a phrase
		links[phrase][link['u']] += 1
		probabilities[phrase] += 1

		# index sources of an article
		# sources[link['u']].append(article['url'])

		# index destinations of an article
		destinations[article['url']].append(link['u'])

	# count occurances of phrase in text
	text = article['text'].lower()
	for phrase in phrases:
		occurances[phrase] += text.count(phrase)

# loop through articles
for article in wiki.Wikipedia('data/articles'):
	processArticle(article)

# translate indexes
def translate(dictionary):
	dict2list = lambda dic: [(k, v) for (k, v) in dic.iteritems()]
	list2dict = lambda lis: dict(lis)
	trans = lambda item: (item[0], list(set([translations[x] for x in item[1] if x in translations])))
	
	return list2dict(map(trans, dict2list(dictionary)))

# links = translate(links)
for phrase in probabilities:
	probabilities[phrase] = float(probabilities[phrase]) / occurances[phrase]

# sources = translate(sources)
destinations = translate(destinations)

# write indexes
json.dump(translations, open('data/translations.txt', 'w'))
json.dump(links, open('data/links.txt', 'w'))
json.dump(probabilities, open('data/probabilities.txt', 'w'))
# json.dump(sources, open('data/sources.txt', 'w'))
json.dump(destinations, open('data/destinations.txt', 'w'))
