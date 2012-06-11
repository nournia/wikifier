import Wikipedia as wiki
import json
from math import *

# read indexes
translations = json.load(open('data/translations.txt'))
links = json.load(open('data/links.txt'))
sources = json.load(open('data/sources.txt'))
destinations = json.load(open('data/destinations.txt'))

def augment(article):
	""" augment each linked phrase in article with it's commonness, relatedness and context_quality

	article: includes text and annotations of an article
	returns whole article with augmented links
	"""

	def relatedness(a, b):
		""" link-based semantic relatedness between two articles
		only considers incoming links following original paper

		a, b: article
		returns relatedness
		"""
		
		if (a not in destinations) or (b not in destinations):
			return 0

		A, B = set(destinations[a]), set(destinations[b])

		W = log(len(translations))
		#todo fix log(len(A & B)) issue by reading relatedness article
		return (log(max(len(A), len(B))) - log(len(A & B) + 1)) / (W - log(min(len(A), len(B))))

	for annotation in article['annotations']:
		choices = {}

		alinks = links[annotation['s'].lower()]
		count = float(sum(alinks.values()))

		for link, c in alinks.items():
			choices[link] = {
				'commonness': c / count,
				'relatedness': relatedness(article['url'], link)
			}

		annotation['choices'] = choices

	return article

def disambiguate(article):
	""" use a classifier for selecting best candidate link considering it's commonness, relatedness and context_quality

	article: includes text and annotations of an article
	returns count of true and false judgements
	"""

	augment(article)


# loop through articles
for article in wiki.Wikipedia('data/articles'):
	disambiguate(article)
