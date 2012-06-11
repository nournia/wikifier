import Wikipedia as wiki
import json, collections

translations = {}
links = collections.defaultdict(lambda: [])
sources = collections.defaultdict(lambda: [])
destinations = collections.defaultdict(lambda: [])

def processArticle(article):

	translations[article['url']] = article['id'][0]

	for link in article['annotations']:
		
		# index links of a phrase
		links[link['s'].lower()].append(link['u'])

		# index sources of an article
		sources[link['u']].append(article['url'])

		# index destinations of an article
		destinations[article['url']].append(link['u'])

# loop through articles
for article in wiki.Wikipedia('data/articles'):
	processArticle(article)

# translate indexes
def translate(dictionary):
	dict2list = lambda dic: [(k, v) for (k, v) in dic.iteritems()]
	list2dict = lambda lis: dict(lis)
	trans = lambda item: (item[0], [translations[x] for x in item[1] if x in translations])
	# trans = lambda item: (item[0], [translations[x] if x in translations else -1 for x in item[1]])
	
	return list2dict(map(trans, dict2list(dictionary)))

tlinks = translate(links)
tsources = translate(sources)
tdestinations = translate(destinations)

# write indexes
output = open('data/translations.txt', 'w')
output.write(json.dumps(translations))
output.close()

output = open('data/links.txt', 'w')
output.write(json.dumps(tlinks))
output.close()

output = open('data/destinations.txt', 'w')
output.write(json.dumps(tdestinations))
output.close()

output = open('data/sources.txt', 'w')
output.write(json.dumps(tsources))
output.close()
