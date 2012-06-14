import Wikipedia as wiki
import json, collections

# index by phrase
links = collections.defaultdict(lambda: collections.defaultdict(lambda: 0))
probability = collections.defaultdict(lambda: 0)
occurances = collections.defaultdict(lambda: 0)

# index by link
content = {}
translation = {}
destinations = collections.defaultdict(lambda: [])

def processArticle(article):

	def extractContent(text):
		content = ''
		for line in text.split("\n")[1:]:
			if len(line.split(' ')) < 5: break
			content += line + ' '
		return content[:-1] # skip last space

	translation[article['url']] = article['id'][0]

	phrases = set([])
	for link in article['annotations']:
		
		phrase = link['s'].lower()
		phrases.add(phrase)
		
		# index links of a phrase
		links[phrase][link['u']] += 1
		probability[phrase] += 1

		# index destinations of an article
		destinations[article['url']].append(link['u'])

	# count occurances of phrase in text
	text = article['text'].lower()
	content[article['url']] = extractContent(text)
	for phrase in phrases:
		occurances[phrase] += text.count(phrase)

# loop through articles
for article in wiki.Wikipedia('data/articles'):
	processArticle(article)

# translate indexes
def translate(dictionary):
	trans = lambda item: (item[0], list(set([translation[x] for x in item[1] if x in translation])))
	return dict(map(trans, dictionary.items()))

for phrase in probability:
	probability[phrase] = float(probability[phrase]) / occurances[phrase]

destinations = translate(destinations)

# write indexes
json.dump(links, open('data/links.txt', 'w'))
json.dump(probability, open('data/probability.txt', 'w'))

json.dump(content, open('data/content.txt', 'w'))
json.dump(translation, open('data/translation.txt', 'w'))
json.dump(destinations, open('data/destinations.txt', 'w'))
