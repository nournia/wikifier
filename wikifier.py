import os, json

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


# loop through wiki files
for root, dirs, files in os.walk('data/articles'):
	for name in files:
		file = open(os.path.join(root, name))
		for line in file:
			article = json.loads(line)
			disambiguate(article)
