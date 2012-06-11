import Wikipedia as wiki
import json

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
