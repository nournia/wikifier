import os, sys, json

class Wikipedia:
	directory = 'data/'
	data = 'data/'

	def __init__(self):
		self.files = []
		for root, dirs, files in os.walk(self.data + 'articles'):
			for name in files:
				self.files.append(os.path.join(root, name))
		self.files.sort()

		self.fileId = 0
		self.progress = 0
		self.currentFile = open(self.files[self.fileId])

	def __iter__(self):
		return self

	def next(self):

		try:
			line = 0
			line = self.currentFile.next()

		except StopIteration:
			self.fileId += 1

			if self.fileId >= len(self.files):
				print
				raise StopIteration
			else:
				self.currentFile = open(self.files[self.fileId])
				line = self.currentFile.next()

				# show progress
				progress = int(100 * float(self.fileId) / len(self.files))
				if progress > self.progress:
					self.progress = progress
					sys.stdout.write('.')
					sys.stdout.flush()

		return json.loads(line)
