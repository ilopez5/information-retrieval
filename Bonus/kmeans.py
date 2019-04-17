#Python 3.0
import re
import os
import collections as c
import time
import random as r
import math as m

class Kmeans:
	def __init__(self, path, stop_name):
		self.index = {}										# term: [idf, ...]
		self.path = path
		self.centroids = c.defaultdict(int)
		self.docmap = {}									# docID: [doc #]
		self.doclen = c.defaultdict(int)
		with open(stop_name, 'r') as f:
			self.stop = f.read().lower().split()			# List of stopwords


	def clustering(self, k): 
		# Fcn to implement kmeans clustering algorithm.
		# Print out: For each cluster, its RSS values and the doc ID of the doc 
		# closest to its centroid, average RSS value, and computation time.
		start = time.perf_counter()
		self.buildIndex()
		for i in range(k):									# Initial Centroids
			self.centroids[r.randint(1,k)] = []
		# Initialization
		# Reassignment of vectors
		# Recomputation of centroids
		# Repeat until convergence
		return


	def buildIndex(self):
		# Fcn to build index from documents in collection
		tokens = self.parse()
		docID = 0
		for term in tokens:
			if term == "DELIM":
				newdoc = True
				docID += 1
				pos = 1
				continue
			elif newdoc:
				self.docmap[docID] = term
				newdoc, nottext = False, 0
				continue
			elif nottext < 3:
				nottext += 1
				continue
			elif term in self.stop:
				continue
			# Below actually adding term to Index
			elif term not in self.index:					# Term 1st occurs
				self.index[term] = [0, (docID, 1, [pos])]
				pos += 1
				continue
			else:
				for tup in self.index[term][1:]:			# Iterate post list
					if tup[0] == docID:
						tup[2].append(pos)
						pos += 1
						wtf = 1 + m.log10(len(tup[2]))
						tup = (tup[0], wtf, tup[2])			# Update entry
						break
				else:										# Add new entry
					self.index[term].append((docID, 1, [pos]))
					pos += 1
		N = len(self.docmap)
		for term,post in self.index.items():
			dft = len(post[1:])
			idf = m.log10(N/dft)
			post[0] = idf
			for item in post[1:]:
				docID, wtf, post = item
				self.doclen[docID] += m.pow(idf*wtf, 2)
		for docID,value in self.doclen.items():
			self.doclen[docID] = m.sqrt(value)
		return
			


	def parse(self):
		# Fcn to parse collection file
		file = ""
		with open(self.path, 'r') as f:
			file = re.sub('\*text', 'DELIM', f.read().lower())
		return list(filter(None, re.split(r"\W+", file)))


if __name__ == '__main__':
	a = Kmeans('TIME.ALL', 'TIME.STP')
	a.buildIndex()
#	a.clustering()
