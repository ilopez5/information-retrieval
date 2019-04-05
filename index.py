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
		self.index = {}							 # term: [idf, (d, wtf, [pos]), ...)
		self.docmap = {}						 # docID: [doc#, len(doc)]
		self.doc_length = c.defaultdict(int)	 # docID: L2
		self.topscores = c.defaultdict(float)	 # Stores most recent top k
		with open(stop_name) as f:
			self.stop = f.read().lower().split() # ['a', 'about', 'above', ...]
		
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
			if term == "DELIM":								# New doc
				newdoc = True								# Next term = doc name
				docID += 1									# Increment docID
				pos = 1										# Set/Reset position
				continue
			elif newdoc:									# Map docID:doc#
				self.docmap[docID] = term					# Create mapping
				newdoc = False								# Only do ^ once
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
		N = len(self.docmap)								# Size of Collection
		for term,post in self.index.items():				# Goal: Insert IDF & Doc len
			dft = len(post[1:])								# Doc freq
			idf = m.log10(N/dft)							# Calc IDF
			post[0] = idf									# Insert rounded IDF
			for item in post[1:]:							# Iterate posting list
				docID, wtf, pos = item						# Unpack tuple
				self.doc_length[docID] += m.pow((idf*wtf), 2)
		for docID,value in self.doc_length.items():
			self.doc_length[docID] = m.sqrt(value)
		end = time.perf_counter()
		print("TF-IDF Index built in {} seconds.".format(end-start))


	def query(self, query_terms, k=10):
		# function for exact top K retrieval using cosine similarity
		# Returns at the minimum the document names of the top K documents ordered 
		# in decreasing order of similarity score
		start = time.perf_counter()
		print("Query to search: \'{}\'".format(query_terms))
		print("Number of (top) results: {}\n".format(k))
		query, query_length = self.calc_tfidf_query(query_terms)	# Calc tfidf query
		results = self.cosine(query, query_length)					# Dot with all Docs
		end = time.perf_counter()
		print("Top {0} result(s) for the query \'{1}\' are:\n".format(k, query_terms))
		self.print_results(results, k, end-start)
		return self.rocchio(query, k)							# Immediately do Rocchio

	
	def rocchio(self, query, k):
		# function to implement rocchio algorithm
		# Return the new query terms and their weights
		rcount, beta, gamma = 0, .75, .15							# Parameters given
		while True:
			rcount += 1												# Tracks iteration
			print("=== Rocchio Algorithm ===\n\nIteration:",rcount)
			pos_fb = input("Enter relevant document ids separated by space: ").split()
			neg_fb = input("Enter non-relevant document ids separated by space: ").split()
			start = time.perf_counter()
			pos_fb, neg_fb, empty = self.pseudo(pos_fb, neg_fb)		# If no feedback
			if not empty:
				pos_fb, neg_fb = self.str_to_int(pos_fb, neg_fb)	# Str => Ints
			rel_doc, nrel_doc = self.create_drdnr_vectors(pos_fb, neg_fb, beta, gamma)
			new_query = self.add_vectors(query, self.add_vectors(rel_doc, nrel_doc))
			end = time.perf_counter()
			print("New query computed in {} seconds.".format(end-start))
			print("New query terms with weights:\n{}\n\n".format(new_query.items()))
			stop = input("Continue with new query (y/n): ")
			if stop == 'n':
				break
			else:
				self.rocchio_query(new_query, k)
		return


	def rocchio_query(self, query, k):
		# Will be similar to query() but geared towards modified query vector
		start = time.perf_counter()
		query_length = self.getlength(query)
		results = self.cosine(query, query_length)
		end = time.perf_counter()
		print("\nTop {0} result(s) for the modified query are:\n".format(k))
		self.print_results(results, k, end-start)
		return


	def cosine(self, query, query_length):
		# Calculate Cosine Similarity of Query Vector with all Documents
		scores = c.defaultdict(float)									# Stores results
		# Calculate numerator per doc
		for qterm, q_tfidf in query.items():							# Iterate qry terms
			idf = self.index[qterm][0]									# Store IDF
			for item in self.index[qterm][1:]:							# Iterate post list
				docID, wtf = item[0], item[1]							# docID, wtf
				d_tfidf = idf * wtf										# Calculate tfidf
				scores[docID] += q_tfidf * d_tfidf						# Multiply tfidfs
		# Calculate denominator per doc
		for docID in scores:
			denom = self.doc_length[docID] * query_length				# Multiply L2's
			if denom:
				scores[docID] /= denom									# Normalize
			else:
				scores[docID] = 0
		return sorted(scores.items(), key=lambda x: x[1], reverse=True) # Return sorted list


	def pseudo(self, relevant, nonrelevant):
		# Checks if no feedback given. If so, sets top 3 as relevant
		sorted(self.topscores.items(), key=lambda x: x[1], reverse=True)
		empty = False
		if relevant==[] and nonrelevant==[]:
			empty = True
			for count,docID in enumerate(self.topscores):
				if count < 3:
					relevant.append(docID)								# Top 3 docs = Rel
				else:
					nonrelevant.append(docID)							# Rest => nonrelevant
		return relevant, nonrelevant, empty


	def create_drdnr_vectors(self, r_docs, nr_docs, beta, gamma):
		# Create document vectors for relevant/nonrelevant documents
		rel_vect = c.defaultdict(float)				# Relevant doc vector
		nrel_vect = c.defaultdict(float)			# Non-relevant doc vector

		# Avoid Divide by Zero for Coefficients
		if nr_docs==[]:
			g_dnr = gamma
			b_dr = beta / len(r_docs)
		elif r_docs==[]:
			g_dnr = gamma / len(nr_docs)
			b_dr = beta
		else:
			g_dnr = gamma / len(nr_docs)
			b_dr = beta / len(r_docs)
		g_dnr *= -1
		for term,post in self.index.items():		# Iterate -> all terms
			nrsum, rsum = 0, 0
			for item in post[1:]:					# Iterate -> post list
				docID, pos = item[0], item[2]
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


	def getlength(self, query):
		# Used to get length of modified vector
		query_length = 0
		for term, val in query.items():
			query_length += m.pow(val, 2)
		query_length = m.sqrt(query_length)
		return query_length


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
			query[term] += 1
		# Calculate tf-idf for query terms
		for term, tf in query.items():
			idf = self.index[term][0]
			wtf = 1 + m.log10(tf)
			tfidf = wtf * idf
			query[term] = tfidf
			query_length += m.pow(tfidf, 2)
		# Calculate L2
		query_length = m.sqrt(query_length)
		return query, query_length


	def add_vectors(self, v_one, v_two):
		# This method will be used to sum vectors
		new_query = c.defaultdict(float)
		for term,val in v_one.items():
			if term not in v_two:
				new_query[term] = val
			else:
				new_query[term] = val + v_two[term]
		for term,val in v_two.items():
			if term not in new_query:
				new_query[term] = val
		return new_query


	def str_to_int(self, pos, neg):
		# Converts user feedback into integers
		for i in range(len(pos)):
			pos[i] = int(pos[i])
		for j in range(len(neg)):
			neg[j] = int(neg[j])
		return pos, neg


	def print_results(self, results, k, time):
		# Print top k results
		self.topscores = c.defaultdict(float)
		print(f"Doc id:  Doc Name:     Score:")
		for count, (docID, score) in enumerate(results, 0):
			if count == k:
				break
			self.topscores[docID] = score					# Storing latest Top K
			print(f"{docID:<8} TEXT {self.docmap[docID]}.txt, {score}")	
		print("\nResults found in {} seconds.\n".format(time))
		return


	def print_dict(self):
		# function to print the terms and posting list in the index
		for term, post_list in self.index.items():
			print(term,':', post_list)


	def print_doc_list(self):
		# function to print the documents and their document id
		for docID, doc in self.docmap.items():
			print("Doc ID: {0}	==> {1}".format(docID, doc))



if __name__ == '__main__':
	x = Index('TIME.ALL', 'TIME.STP')
	x.buildIndex()
	x.query(' KENNEDY ADMINISTRATION PRESSURE ON NGO DINH DIEM TO STOP SUPPRESSING THE BUDDHISTS . ', 7) # Query 1
#	x.query(' ELECTION OF PARK CHUNG HEE AS PRESIDENT OF SOUTH KOREA . ', 5) # Query 15
#	x.query(' AGREEMENT BY THE UNITED ARAB REPUBLIC AND SAUDI ARABIA TO WITHDRAW THEIR FORCES FROM YEMEN, WHICH INVOLVES OBSERVERS FROM THE UNITED NATIONS EXPEDITIONARY FORCE BEING SENT TO YEMEN . ', 5) # Query 19
