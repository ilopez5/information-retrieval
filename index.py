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
		self.r_counter = 0
		
	def buildIndex(self):
		# function to read documents from collection, tokenize and build the 
		# index with tokens implement additional functionality to support 
		# relevance feedback use unique document integer IDs
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
		print("TF-IDF Index built in {} seconds.".format(end-start))


	def query(self, query_terms, k=10):
		# function for exact top K retrieval using cosine similarity
		# Returns at the minimum the document names of the top K documents ordered 
		# in decreasing order o\f similarity score
		start = time.perf_counter()
		print("Query to search: \'{}\'".format(query_terms))
		print("Number of (top) results: {}\n".format(k))
		query, query_length = self.calc_tfidf_query(query_terms) # Calc tfidf for query
		results = self.cosine(query, query_length)				 # Calc cosine score
		end = time.perf_counter()
		print("Top {0} result(s) for the query \'{1}\' are:\n".format(k, query_terms))
		print(f"Doc id:  Doc Name:     Score:")
		for count, (doc_id, score) in enumerate(results, 0):
			if count == k:
				break
			print(f"{doc_id:<8} TEXT {self.docmap[doc_id][0]}.txt, {score}")	
		print("\nResults found in {} seconds.\n".format(end-start))
		return self.rocchio(query_terms, k)

	
	def rocchio(self, query_terms, k):
		# function to implement rocchio algorithm
		# Return the new query  terms and their weights
		beta, gamma = .75, .15								# Parameters given
		query = self.r_calc_query(query_terms)
		while True:
			self.r_counter += 1								# Tracks iteration
			print("=== Rocchio Algorithm ===\n\nIteration:",self.r_counter)
			pos_fb = input("Enter relevant document ids separated by space: ").split()
			neg_fb = input("Enter non-relevant document ids separated by space: ").split()
			start = time.perf_counter()
			pos_fb, neg_fb = self.r_str_to_int(pos_fb, neg_fb)
			rel_doc, nrel_doc = self.create_doc_vectors(pos_fb, neg_fb, beta, gamma)
			new_query = self.r_add_vectors(query, self.r_add_vectors(rel_doc, nrel_doc))
			end = time.perf_counter()
			print("New query computed in {} seconds.".format(end-start))
			print("New query terms with weights:\n{}".format(10)) # REPLACE 10 with new_query
			stop = input("\nContinue with new query (y/n): ")
			if stop == 'n':
				break
			else:
				query, query_length = self.r_getlength(new_query)
				self.rocchio_query(query, query_length, k)
		return


	def rocchio_query(self, query, query_length, k):
		# Will be similar to query() but geared towards modified query vector
		start = time.perf_counter()
		results = self.cosine(query, query_length)
		end = time.perf_counter()
		print("Top {0} result(s) for the modified query are:\m".format(k))
		print("Doc id:  Doc Name:	  Score:")
		for count, (docid, score) in enumerate(results, 0):
			if count == k:
				break
			print(f"{docid:<8} TEXT {self.docmap[docid][0]}.txt, {score}")
		print("\nResults found in {} seconds.\n".format(end-start))
		return

	# DEBUGGING: ISSUE LIES BELOW
	def cosine(self, query, query_length):
		# Calculate the cosine similarity score of any two vectors passed in
		scores = c.defaultdict(int)										# Store rank list
		doc_tfidf = c.defaultdict(float)								# Store doc tfidf

		# Calculate numerator per doc
		for query_term, query_tfidf in query.items():
			doc_idf = self.index[query_term][0]							# Store IDF
			for item in self.index[query_term][1:]:
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


	def create_doc_vectors(self, r_docs, nr_docs, beta, gamma):
		# Create document vectors for documents that matter
		b_dr = beta / len(r_docs)					# B/Dr coefficient
		g_dnr = gamma / len(nr_docs)				# G/Dnr coefficient
		rel_vect = c.defaultdict(float)				# Relevant doc vector
		nrel_vect = c.defaultdict(float)			# Non-relevant doc vector
		
		nrsum, rsum = 0, 0
		for term in self.index:						# Iterate -> all terms
			for item in self.index[term][1:]:		# Iterate -> post list
				pos, docID = item[2], item[0]
				if docID in r_docs:					# Curr doc in D_r
					rsum += len(pos)				# Add raw frequency
				elif docID in nr_docs:				# Curr doc in D_nr
					nrsum += len(pos)				# Add raw frequency
			if rsum:								# Term => new query
				rel_vect[term] = rsum				# Add raw freq
				if nrsum:
					nrel_vect[term] = nrsum
			elif nrsum:
				nrel_vect[term] = nrsum
		# Scaling with Beta and Gamma coefficients
		for term, freq in rel_vect.items():
			rel_vect[term] = freq * b_dr
		for term, freq in nrel_vect.items():
			nrel_vect[term] = freq * g_dnr
		return rel_vect, nrel_vect


	def r_getlength(self, query):
		# Used to get length of modified vector
		query_length = 0
		for term, val in query.items():
			query_length += m.pow(val, 2)
		return query, query_length


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


	def r_calc_query(self, query_terms):
		# Calculates a simple query vector (e.g. [1,1,2]
		query = c.defaultdict(int)
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
		return query


	def r_add_vectors(self, v_one, v_two):
		# This method will be used to sum vectors
		new_query = c.defaultdict(float)
		for term,val in v_one.items():
			if term not in v_two:
				new_query[term] = val
			else:
				new_query[term] = val + v_two[term]
		for term,val in v_two.items():
			if term in new_query:
				continue
			else:
				new_query[term] = val
		return new_query


	def r_str_to_int(self, pos, neg):
		# Converts user feedback into integers
		for i in range(len(pos)):
			pos[i] = eval(pos[i])
		for j in range(len(neg)):
			neg[j] = eval(neg[j])
		return pos, neg


	def print_dict(self):
		# function to print the terms and posting list in the index
		for term, post_list in self.index.items():
			print(term,':', post_list)


	def print_doc_list(self):
		# function to print the documents and their document id
		for docID, doc in self.docmap.items():
			print("Doc ID: {0}	==> {1}".format(docID, doc[0]))



if __name__ == '__main__':
	x = Index('TIME.ALL', 'TIME.STP')
	x.buildIndex()
	x.query(' BACKGROUND OF THE NEW CHANCELLOR OF WEST GERMANY, LUDWIG ERHARD . ', 10)
