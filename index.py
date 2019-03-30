#Python 3.0
import re
import os
import collections as c
import time
import math as m
#import other modules as needed

class Index:
	def __init__(self, path, stop_name):
		self.path = path
		self.index = {}							 # term: [idf, (docID, wtf, [positions]), ...)
		self.docmap = {}						 # docID: [doc#, len(doc)]
		with open(stop_name) as f:
			self.stop = f.read().lower().split() # ['a', 'about', 'above', ...]		
		
	def buildIndex(self):
		# function to read documents from collection, tokenize and build the index with tokens
		# implement additional functionality to support relevance feedback
		# use unique document integer IDs
		start = time.perf_counter()
		file = ""
		with open(self.path, 'r') as f:						# Opens file
			file = re.sub('\*text', 'DELIM', f.read().lower()) # Save into string
		tokens = list(filter(None, re.split(r"\W+", file)))	# Tokenize string

		docID = 0
		for term in tokens:									# Iterate thru tokens
			if term == "DELIM":								# First doc or new doc
				if docID >= 1:								# End of Doc
					self.docmap[docID].append(pos)			# Last pos = Length
				isdoc = True								# For docID:doc# mapping
				docID += 1
				pos = 1										# Set/Reset position
				continue
			elif isdoc:										# Map docID:doc#
				self.docmap[docID] = [term]					# Create mapping
				isdoc = False								# Only do ^ once
				nottext = 0									# Counter to skip header
				continue
			elif nottext < 3:								# Skip header info
				nottext += 1
				continue
			elif term in self.stop:							# Ignore stop words
				continue
			# Below: Actually adding term to Index
			elif term not in self.index:					# 1st appearance in index
				self.index[term] = [0, (docID,1,[pos])]		# Create post list
				pos += 1									# Increment position
				continue
			else:											# Term in index already
				for tup in self.index[term][1:]:			# Iterate post list
					if tup[0] == docID:						# Check docID
						tup[2].append(pos)					# Append new position
						pos += 1							# Increment position
						wtf = 1 + m.log10(len(tup[2]))		# Calculte weighted tf
						tup = (tup[0], wtf, tup[2])			# Tuples immutable :(
						break
				else:										# First appearance in doc
					self.index[term].append((docID,1,[pos])) # Create a tuple
					pos += 1
		for term in self.index:								# Goal: Insert IDF
			N = len(self.docmap)							# Length of Collection
			dft = len(self.index[term]) - 1					# Length of Post List
			self.index[term][0] = round(m.log10(N/dft), 8)	# Insert rounded IDF
		end = time.perf_counter()
		print("Index built in {} seconds.".format(end-start))

	
	def rocchio(self, query_terms, pos_feedback, neg_feedback, alpha, beta, gamma):
	# function to implement rocchio algorithm
	# pos_feedback - documents deemed to be relevant by the user
	# neg_feedback - documents deemed to be non-relevant by the user
	# Return the new query  terms and their weights
		pass

	def query(self, query_terms, k):
		# function for exact top K retrieval using cosine similarity
		# Returns at the minimum the document names of the top K documents ordered in decreasing order of similarity score
		start = time.perf_counter()
		query, query_length = self.calc_tfidf_query(query_terms) # Calc tfidf for query
		results = self.cosine_score(query, query_length)		 # Calc cosine score
		end = time.perf_counter()
		for count, (doc_id, score) in enumerate(results, 0):
			if count == k:
				break
			print("{0}. {1} with score {2}".format(count+1,self.docmap[doc_id][0],score))	
		print("Results found in {} seconds.".format(end-start))

	def print_dict(self):
		# function to print the terms and posting list in the index
		for term, post_list in self.index.items():
			print(term,':', post_list)

	def print_doc_list(self):
		# function to print the documents and their document id
		for docID, doc in self.docmap.items():
			print("Doc ID: {0}		==> {1}".format(docID, doc[0]))

	def cosine_score(self, query, query_length):
		# calculate the cosine similarity score of any two vectors passed in
		scores = c.defaultdict(int)										# Store rank list
		doc_tfidf = c.defaultdict(float)								# Store doc tfidf

		# Calculate numerator per doc
		for query_term, query_tfidf in query.items():
			doc_idf = self.index[query_term][0]							# Store IDF
			for index, item in enumerate(self.index[query_term][1:]):
				doc_id = item[0]										# docID
				doc_wtf = item[1]										# wtf
				doc_tfidf[doc_id] = doc_idf*doc_wtf						# Calculate tfidf
				scores[doc_id] += query_tfidf * doc_tfidf[doc_id]		# Multiply tfidfs
		# Calculate denominator per doc
		for doc_id in scores:
			denom = self.docmap[doc_id][1] * query_length				# Multiply lengths
			if not denom:
				scores[doc_id] = 0										# No Div by Zero
				continue
			scores[doc_id] /= denom										# Normalize
		return sorted(scores.items(), key=lambda x: x[1], reverse=True) # Return sorted list

	def calc_tfidf_query(self, query_terms):
		# Converts query into vector (taken from HW 2 Solution)
		query = c.defaultdict(int)
		query_length = 0

		tokens = re.split('\W+', query_terms.lower())
		for term in tokens:
			if term == '':
				continue
			elif term in self.stop:
				continue
			elif term not in self.index.keys():
				continue
			elif term not in query:
				query[term] = 1
				continue
			query[term] += 1

		# Calculate tf-idf for query terms
		for term, freq in query.items():
			idf = self.index[term][0]
			wtf = 1 + m.log10(freq)
			query[term] = wtf*idf
			query_length += m.pow((wtf*idf), 2)

		# Length of query terms
		query_length = m.sqrt(query_length)
		return query, query_length

if __name__ == '__main__':
	x = Index('TIME.ALL', 'TIME.STP')
	x.buildIndex()
	x.query('red china home', 10)	
