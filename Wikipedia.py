import os, json

class Wikipedia:
	def __init__(self, directory):
		self.files = []
		for root, dirs, files in os.walk(directory):
			for name in files:
				self.files.append(os.path.join(root, name))
		self.files.sort()

		self.fileId = 0
		self.lineId = 0
		self.currentFile = open(self.files[self.fileId])
		self.currentFile = [line for line in self.currentFile]

	def __iter__(self):
		return self

	def next(self):
		if self.lineId >= len(self.currentFile):
			self.fileId += 1
			self.lineId = 0

			if self.fileId >= len(self.files):
				raise StopIteration
			else:
				self.currentFile = open(self.files[self.fileId])
				self.currentFile = [line for line in self.currentFile]
	
		line = self.currentFile[self.lineId]
		self.lineId += 1

		return json.loads(line)
