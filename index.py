#Python 3.0
import re
import os
import collections
import time
import math
#import other modules as needed

class index:
	def __init__(self,path):
		self.path = path
		self.index = {}
		self.documents = {}
		self.stop_list = ['a','an','and','are','as','at','be','by','for','from','has','he','in','is','it','its','of','on','that','the','to','was','were','will','with']

	def buildIndex(self):
		# function to read documents from collection, tokenize and build the index with tokens
		# implement additional functionality to support relevance feedback
		# use unique document integer IDs

		start = time.perf_counter()

		########################### Building our Index ###############################
		for docID, doc in enumerate(os.listdir(self.path), 1):
			with open(os.path.join(self.path, doc), 'r') as file_obj:
				doc_string = file_obj.read().lower()
			tok_list = filter(None, re.split(r"\W+", doc_string))		# Tok list generated
			self.documents[docID] = [doc]								# Map IDs to Docs
			for pos, term in enumerate(tok_list, 1):
				if term in self.stop_list:								# Ignore stop words
					continue
				elif term not in self.index:							# 1st appearance (index)
					self.index[term] = [0, (docID, 1, [pos])]			# Create entry
				else:
					for i in range(1,len(self.index[term])):			# Search Post list
						curr_docID, _, positions = self.index[term][i]  # Extract tuple
						if curr_docID == docID:							# Found document
							positions.append(pos)						# Append position
							break
						elif i == len(self.index[term])-1:				# 1st appearance (doc)
							self.index[term].append((docID, 1, [pos]))  # Create tuple

		################# Index Built, Now Insert IDF & Weighted TF ##################
		# N = len(self.documents)	| df_t = len(self.index[term]) - 1	| idf_t = log10(N/df_t)
		for term in self.index:
			self.index[term][0] = round(math.log10((len(self.documents)) / (len(self.index[term]) - 1)), 4)	# IDF
			for i in range(1,len(self.index[term])):
				self.index[term][i] = (self.index[term][i][0], 1 + math.log10(len(self.index[term][i][2])), self.index[term][i][2])

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
