#Python 3.0
import re
import os
import collections
import time
import math as m
#import other modules as needed

class index:
	def __init__(self,path):
		self.path = path
		self.index = {}
		self.docmap = {}

	def buildIndex(self):
		# function to read documents from collection, tokenize and build the index with tokens
		# implement additional functionality to support relevance feedback
		# use unique document integer IDs
		file = ""
		with open(self.path, 'r') as f:						# Opens file
			file = re.sub('\*text', 'DELIM', f.read())		# Save into string
		tokens = list(filter(None, re.split(r"\W+", file)))	# Tokenize string
		pos, docID = 0, 0
		for term in tokens:									# Iterate list
			if term == "DELIM":								# First/new doc
				isdoc = True								# Used for docID mapping
				docID += 1									# Increment docID
				pos = 1										# Reset position
				continue
			elif isdoc:										# Map docID to doc #
				self.docmap[docID] = term					# Create mapping
				isdoc = False								# Set to false
				nottext = 0									# Counter to skip header
				continue
			elif nottext < 3:								# Skip header info
				nottext += 1								# Increment counter
				continue
			elif term not in self.index:					# 1st appearance in index
				self.index[term] = [0, (docID,1,[pos])]		# Create post list
				pos += 1									# Increment position
				continue
			else:											# Term in index already
				for tup in self.index[term]:				# Iterate post list
					if type(tup) != tuple:					# Skip idf
						continue
					elif tup[0] == docID:					# Check docID
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
			dft = len(self.index[term]-1)					# Length of Post List
			self.index[term][0] = rount(m.log10(N/dft), 8)	# Insert rounded IDF
	
	def rocchio(self, query_terms, pos_feedback, neg_feedback, alpha, beta, gamma):
	# function to implement rocchio algorithm
	# pos_feedback - documents deemed to be relevant by the user
	# neg_feedback - documents deemed to be non-relevant by the user
	# Return the new query  terms and their weights
	
	def query(self, query_terms, k):
	# function for exact top K retrieval using cosine similarity
	# Returns at the minimum the document names of the top K documents ordered in decreasing order of similarity score
	
	def print_dict(self):
    # function to print the terms and posting list in the index

	def print_doc_list(self):
	# function to print the documents and their document id

	def cosine_score(self, vector_1, vector_2):
	# calculate the cosine similarity score of any two vectors passed in
