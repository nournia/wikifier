from Wikipedia import Wikipedia
from indexer import loadDestinations
import json, random

destinations = loadDestinations()

minLinks = 100
articles = [int(key) for key, value in destinations.items() if len(value) > minLinks]

samples = 1000
articles = random.sample(articles, samples)

output = open(Wikipedia.directory + 'samples.txt', 'w')

for article in Wikipedia():
	if article['id'][0] in articles:
		print len(article['annotations']), article['url']
		output.write(json.dumps(article) + "\n")

output.close()