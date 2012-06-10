import os, json, collections

commonness = collections.defaultdict(lambda: 0)

def processArticle(article):

	# measuring commonness of links
	for link in article['annotations']:
		commonness[link['u']] += 1


# loop through wiki files
for root, dirs, files in os.walk('data/articles'):
	for name in files:
		file = open(os.path.join(root, name))
		for line in file:
			article = json.loads(line)
			processArticle(article)

