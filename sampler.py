import Wikipedia as wiki
import json, random

output = open('data/samples.txt', 'w')

articles = []
for article in wiki.Wikipedia('data/articles'):
	if len(article['annotations']) > 100:
		articles.append(article)

for article in random.sample(articles, 200):
	print len(article['annotations']), article['url']
	output.write(json.dumps(article) + "\n")

output.close()