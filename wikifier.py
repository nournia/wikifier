import sys, json, math
import numpy as np
from sklearn.naive_bayes import GaussianNB

from relatedness import WLVM, ESA
from indexer import loadTranslation, loadLinks

encyclopedic = True
if len(sys.argv) == 2 and sys.argv[1] == 'content':
	encyclopedic = False

if encyclopedic:
	relatedness_model = WLVM()
else:
	relatedness_model = ESA()

# read indexes
translation = loadTranslation()
links = loadLinks()

def getLinks(phrase):
	phrase = phrase.lower().encode('utf8')
	if not phrase in links: return {}
	result = links[phrase]
	result.pop('', 0)
	return result

def getProbability(phrase):
	return links[phrase.lower().encode('utf8')].get('', 0)

# constants
minimum_sense_probability = .02

avg = lambda l: float(sum(l))/len(l) if l else 0

def features(article, data, target):
	""" augment each linked phrase in article with it's commonness, relatedness and context_quality

	article: includes text and annotations of an article
	returns whole article with augmented links
	"""

	global baseline_judgement

	annotations = []
	for annotation in article['annotations']:
		if annotation['u'].encode('utf8') in translation:
			annotation['u'] = translation[annotation['u'].encode('utf8')]
			annotations.append(annotation)

	# links without ambiguity in featurecontext (document)
	clear_links = filter(lambda annotation: len(getLinks(annotation['s'])) == 1, annotations)

	# todo parallel weight calculation
	for link in clear_links:
		relatednesses = []
		for link2 in clear_links:
			if link != link2:
				relatednesses.append(relatedness_model.relatedness(link['u'], link2['u']))
		avg_relatedness = avg(relatednesses)

		# link probability effect
		link['weight'] = avg([avg_relatedness, getProbability(link['s'])])
	
	for annotation in annotations:
		candidate_links = getLinks(annotation['s'])
		all_count = float(sum(candidate_links.values()))

		# filter candidate_links with minimum_sense_probability
		candidate_links = dict(filter(lambda (link, count): (count / all_count) > minimum_sense_probability, candidate_links.items()))
		
		# baseline_judgement as the most common link selection
		if len(candidate_links) and annotation['u'] == int(max(candidate_links)): baseline_judgement += 1
		
		context_quality = sum([clear_link['weight'] for clear_link in clear_links])
		for link, count in candidate_links.items():
			commonness = count / all_count
			relatedness = avg([clear_link['weight'] * relatedness_model.relatedness(link, clear_link['u'])  for clear_link in clear_links]) # weighted average of link relatedness

			data.append([commonness, relatedness, context_quality])
			target.append([int(link) == annotation['u'], annotation['o']])



def extract_features(articles, data, target):
	size, progress = float(len(articles)), 0
	for i, article in enumerate(articles):

		# extract features from article
		features(json.loads(article), data, target)

		# show progress bar
		p = int(100 * i / size)
		if p > progress:
			progress = p
			sys.stdout.write('.')
			sys.stdout.flush()

	data = np.array(data, dtype=float)
	print ';'

# load articles
total_size = 1000
articles = [article for article in open('data/samples.txt')]
train_size = int(len(articles) * .8)

# train
print 'Train'
data, target = [], []
baseline_judgement = 0
extract_features(articles[:train_size], data, target)
target = np.array([t[0] for t in target], dtype=bool)

disambiguator = GaussianNB()
disambiguator.fit(data, target)

# test
print 'Test'
data, target = [], []
baseline_judgement = 0
extract_features(articles[train_size:], data, target)
target = np.array(target)

predict = disambiguator.predict(data)
predict_proba = disambiguator.predict_proba(data)

# mesurements on data
tp = float((predict[predict == target[:, 0]] == True).sum())
data_precision = tp / (predict == True).sum()
data_recall = tp / (target[:, 0] == True).sum()

# fill results
results = np.append(target, predict_proba, axis=1)
indices = []
i, count = 0, 0
last_offset = -1
for result in results:
	if last_offset != result[1]:
		if count:
			indices.append((i-count, i))
		last_offset = result[1]
		count = 0
	i += 1; count += 1
indices.append((i-count, i))

# mesurements on links
judgements = []
for index in indices:
	link = results[index[0]:index[1]]
	mi = link[:, 3].argmax()
	judgements.append([link[mi][0] == 1, link[mi][3]])
judgements = np.array(judgements)

precision = 1 # that's it
recall = float(judgements[:, 0].sum()) / len(judgements)
baseline_recall = float(baseline_judgement) / len(judgements)

print 'Results:'
print 'Link Recall: %.2f' % recall
print 'Baseline Recall: %.2f' % baseline_recall
print 'Classifier - Precision: %.2f, Recall: %.2f' % (data_precision, data_recall)

# wrong judgements: judgements[judgements[:, 0] == 0]
