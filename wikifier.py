import json
from math import *
import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn import cross_validation

# read indexes
translations = json.load(open('data/translations.txt'))
links = json.load(open('data/links.txt'))
probabilities = json.load(open('data/probabilities.txt'))
destinations = json.load(open('data/destinations.txt'))

avg = lambda l: float(sum(l))/len(l) if l else 0

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

def features(article, data, target):
	""" augment each linked phrase in article with it's commonness, relatedness and context_quality

	article: includes text and annotations of an article
	returns whole article with augmented links
	"""

	# links without ambiguity in context (document)
	clear_links = filter(lambda annotation: len(links[annotation['s'].lower()]) == 1, article['annotations'])

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
		candidate_links = links[annotation['s'].lower()]
		all_count = float(sum(candidate_links.values()))

		lcontext_quality = sum([clear_link['weight'] for clear_link in clear_links])
		for link, count in candidate_links.items():
			lcommonness = count / all_count
			lrelatedness = avg([clear_link['weight'] * relatedness(link, clear_link['u'])  for clear_link in clear_links]) # weighted average of link relatedness

			data.append([lcommonness, lrelatedness, lcontext_quality])
			target.append(link == annotation['u'])


# todo use computed minimum sense probability described in section 3.2 of paper

articles = [json.loads(article) for article in open('data/samples.txt')]
train_size = int(len(articles) * .8)

# train
data, target = [], []
for article in articles[:train_size]:
	features(article, data, target)
data, target = np.array(data, dtype=float), np.array(target, dtype=bool)

disambiguator = GaussianNB()
disambiguator.fit(data, target)

# test
data, target = [], []
for article in articles[train_size:]:
	features(article, data, target)
data, target = np.array(data, dtype=float), np.array(target, dtype=bool)

predicted = disambiguator.predict(data)

# mesurements
tp = float((predicted[predicted == target] == True).sum())
precision = tp / (predicted == True).sum()
recall = tp / (target == True).sum()
