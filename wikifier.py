import Wikipedia as wiki
import json
from math import *

# read indexes
translations = json.load(open('data/translations.txt'))
links = json.load(open('data/links.txt'))
probabilities = json.load(open('data/probabilities.txt'))
# sources = json.load(open('data/sources.txt'))
destinations = json.load(open('data/destinations.txt'))

def relatedness(a, b):
	""" link-based semantic relatedness between two articles which only considers incoming links following original paper

	a, b: article
	returns relatedness of them
	"""
	
	if (a not in destinations) or (b not in destinations): return 0

	A, B = set(destinations[a]), set(destinations[b])
	W = log(len(translations))

	#todo fix simple +1 solution for log(0) issue by reading relatedness article
	return (log(max(len(A), len(B)) +1) - log(len(A & B) +1)) / (W - log(min(len(A), len(B)) +1))

def augment(article):
	""" augment each linked phrase in article with it's commonness, relatedness and context_quality

	article: includes text and annotations of an article
	returns whole article with augmented links
	"""

	# links without ambiguity in context (document)
	clear_links = filter(lambda annotation: len(links[annotation['s'].lower()]) == 1, article['annotations'])

	avg = lambda l: float(sum(l))/len(l)

	# todo parallel weight calculation
	for link in clear_links:
		relatednesses = []
		for link2 in clear_links:
			if link != link2:
				relatednesses.append(relatedness(link['u'], link2['u']))
		avg_relatedness = avg(relatednesses)

		# link probability effect
		link['weight'] = avg([avg_relatedness, probabilities[link['s'].lower()]])
	
	for annotation in article['annotations']:
		choices = {}

		candidate_links = links[annotation['s'].lower()]
		all_count = float(sum(candidate_links.values()))

		for link, count in candidate_links.items():
			choices[link] = {
				'commonness': count / all_count,
				'relatedness': avg([clear_link['weight'] * relatedness(link, clear_link['u'])  for clear_link in clear_links]) # weighted average of link relatedness
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
