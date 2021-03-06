import sys, json, math
import numpy as np
from sklearn.naive_bayes import GaussianNB

from relatedness import WLVMRelatedness, ESARelatedness
from indexer import loadTranslation
from candidates import LinkedCandidates, OccuredCandidates

encyclopedic = True
if len(sys.argv) == 2 and sys.argv[1] == 'content':
	encyclopedic = False

if encyclopedic:
	relatedness_model = WLVMRelatedness()
	candidates_model = LinkedCandidates()
else:
	relatedness_model = WLVMRelatedness()
	candidates_model = OccuredCandidates()

# read indexes
translation = loadTranslation()

# constants
minimum_sense_probability = .02

avg = lambda l: float(sum(l))/len(l) if l else 0

def features(article, data, target):
	""" augment each linked phrase in article with it's commonness, relatedness and context_quality

	article: includes text and annotations of an article
	returns whole article with augmented links
	"""

	global baseline_judgement, stat_all, stat_presence

	# translate annotations
	annotations = []
	for annotation in article['annotations']:
		if str(annotation['u']) in translation:
			annotation['u'] = translation[str(annotation['u'])]
			annotations.append(annotation)

	# extract candidate links
	for annotation in annotations:
		annotation['probability'], annotation['links'] = candidates_model.find(annotation['s'])

	# links without ambiguity in context (document)
	clear_links = candidates_model.clear_links(annotations)
	
	# todo parallel weight calculation
	for link in clear_links:
		relatednesses = []
		for link2 in clear_links:
			if link != link2:
				relatednesses.append(relatedness_model.relatedness(link['u'], link2['u']))
		avg_relatedness = avg(relatednesses)

		# link probability effect
		link['weight'] = avg([avg_relatedness, link['probability']])

	for annotation in annotations:
		candidate_links = annotation['links']
		all_count = float(sum(candidate_links.values()))

		# filter candidate_links with minimum_sense_probability
		candidate_links = dict(filter(lambda (link, count): (count / all_count) > minimum_sense_probability, candidate_links.items()))
		
		# baseline_judgement as the most common link selection
		if len(candidate_links) and annotation['u'] == max(candidate_links, key=candidate_links.get): baseline_judgement += 1
		# presence of solution in candidates
		if annotation['u'] in candidate_links: stat_presence += 1
		stat_all += 1

		context_quality = sum([clear_link['weight'] for clear_link in clear_links])
		for link, count in candidate_links.items():
			commonness = count / all_count
			relatedness = avg([clear_link['weight'] * relatedness_model.relatedness(link, clear_link['u'])  for clear_link in clear_links]) # weighted average of link relatedness

			data.append([commonness, relatedness, context_quality])
			target.append([link == annotation['u'], annotation['o']])



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
stat_all = 0; stat_presence = 0

# train
print 'Train'
data_train, target_train = [], []
baseline_judgement = 0
extract_features(articles[:train_size], data_train, target_train)
target_train = np.array([t[0] for t in target_train], dtype=bool)

disambiguator = GaussianNB()
disambiguator.fit(data_train, target_train)

# test
print 'Test'
data_test, target_test = [], []
baseline_judgement = 0
extract_features(articles[train_size:], data_test, target_test)
target_test = np.array(target_test)

predict = disambiguator.predict(data_test)
predict_proba = disambiguator.predict_proba(data_test)

# mesurements on data
tp = float((predict[predict == target_test[:, 0]] == True).sum())
classifier_precision = tp / (predict == True).sum()
classifier_recall = tp / (target_test[:, 0] == True).sum()

# fill results
results = np.append(target_test, predict_proba, axis=1)
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


tp = sum(judgements[:, 0] == 1)
fp = sum(judgements[:, 0] == 0)
fn = fp
precision = float(tp) / (tp + fp)
recall = float(tp) / (tp + fn)
baseline_recall = float(baseline_judgement) / len(judgements)

print 'Results:'
print 'Solution Presence in Candidates: %.2f' % (float(stat_presence)/stat_all)
print 'Link Recall: %.2f' % recall
print 'Baseline Recall: %.2f' % baseline_recall
print 'Classifier - Precision: %.2f, Recall: %.2f' % (classifier_precision, classifier_recall)

# wrong judgements: judgements[judgements[:, 0] == 0]
