#! /usr/bin/env python3
# encoding: utf-8
# Python 3.0
import re
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
		self.docTokens = c.defaultdict(list)
		with open(stop_name, 'r') as f:
			self.stop = f.read().lower().split()			# List of stopwords



	def clustering(self, K): 
		# Fcn to implement kmeans clustering algorithm.
		# Print out: For each cluster, its RSS values and the doc ID of the doc 
		# closest to its centroid, average RSS value, and computation time.
		start = time.perf_counter()
		self.buildIndex()									# Build Index
		for i in range(K):									# Rand Centroids
			self.centroids[r.randint(1,K)] = []
		while True:
			self.buildClusters()							# Assign/Reassign
			
		return



	def buildClusters(self, K):
		# Method to build cluster
		s_docID = set(self.docmap.keys())					# Set of Doc IDs
		s_lead = set(r.sample(s_docID, K))					# Set of Leaders
		s_follow = s_docID - s_lead							# Set of Followers
		
		# Extract tf-idf leaders
		lead_ind, clusters = {}, c.defaultdict(list)
		for key,val in self.index.items():
			lead_ind[key] = [val[0]]						# Store term idf
			for doc in val[1:]:
				if doc[0] in s_lead:
					lead_ind[key].append(doc)

		# Find most similar leader for each follower
		for docID in s_follow:
			qterms = ' '.join(self.docTokens[docID])
			query, query_length = self.calc_tfidf_query(qterms)
			results = self.cosine(query, query_length, lead_ind)
			if len(results) > 0:
				mleader = results[0][0]
				clusters[mleader].append(docID)
		return lead_ind, clusters



	def calc_tfidf_query(self, qterms):
		# Creates a TF-IDF weighted query
		query = c.defaultdict(int)
		query_length = 0
		tokens = re.split('\W+', qterms.lower())
		for term in tokens:
			if term == '':
				continue
			elif term in self.stop:
				continue
			elif term not in self.index.keys():
				continue
			query[term] += 1

		# Calc tf-idf for query terms
		for term,freq in query.items():
			idf = self.index[term][0]
			wtf = 1 + m.log10(freq)
			query[term] = wtf*idf
			query_length += m.pow((wtf*idf), 2)

		# Normalizing
		query_length = m.sqrt(query_length)
		return query, query_length



	def cosine(self, query, query_length, lead_index):
		# Computes the cosine similarity score
		scores, doc_tfidf = c.defaultdict(float), c.defaultdict(float)
		for qterm,qtfidf in query.items():						# Numerator
			docIDF = lead_index[qterm][0]
			for index,item in enumerate(lead_index[qterm][1:]):
				docID, docWTF = item[0], item[1]
				doc_tfidf[docID] = docIDF*docWTF
				scores[docID] += qtfidf*doc_tfidf[docID]
		for docID in scores:									# Denominator
			denom = self.doclen[docID]*query_length
			if denom:
				scores[docID] /= denom
			else:
				scores[docID] = 0
		return sorted(scores.items(), key=lambda x: x[1], reverse=True)
				



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
			else:
				self.docTokens[docID].append(term)
				if term not in self.index:						# Tok 1st occurs
					self.index[term] = [0, (docID, 1, [pos])]
					pos += 1
					continue
				else:
					for tup in self.index[term][1:]:			# Iter post list
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
	a.clustering(10)
