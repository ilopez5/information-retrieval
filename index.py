#Python 3.0
import re
import os
import collections
import time
#import other modules as needed

class index:
	def __init__(self,path):

	def buildIndex(self):
		#function to read documents from collection, tokenize and build the index with tokens
<<<<<<< HEAD
		#index should also contain positional information of the terms in the document --- term: [(ID1,[pos1,pos2,..]), (ID2, [pos1,pos2,…]),….]
		#use unique document IDs
		start = time.perf_counter()
		for docID, doc in enumerate(os.listdir(self.path), 1):				# walk through collections and have docID increment
			with open(os.path.join(self.path, doc), 'r') as file_obj:		# create file object of current doc
				doc_string = file_obj.read().lower()						# read/save as string using re
			tok_list = filter(None, re.split(r"\W+", doc_string))			# tokenize string
			self.doc_list[docID] = doc										# this creates mapping from docID to doc

			for pos, term in enumerate(tok_list, 1):						# walk through token list, also increment position as we walk thru doc
				if term not in self.index:									# term not in index yet?
					self.index[term] = [(docID, ,[pos])]							# create appropriate key:value mapping
				else:														# term is in index already
					for i in range(len(self.index[term])):						# walks through post list
						current_docID, positions = self.index[term][i]			# grabs tuple information
						if current_docID == docID:								# compares keys
							positions.append(pos)									# updates pos list if match
							break
						elif i == len(self.index[term])-1:						# this check not really needed I guess
							self.index[term].append((docID, [pos]))				# appends new tuple
			#:for term in tok_list:
				
				
		end = time.perf_counter()
		print("Index built in {} seconds.".format(end-start))	







	def and_query(self, query_terms):
	#function for identifying relevant docs using the index
		start = time.perf_counter()

		size_q = len(query_terms)											# store size so we calculate once
		result = []															# list to output when done
		point = {}															# 'Pointers' to indexes for query terms
		skip = {}															# 'Skip Pointers' 
		base, done = True, False											# Boolean variables to be used
		num_comp = 0														# initializing comparison counter
		
		for i in query_terms:
			skip[i] = int((len(self.index[i]))**(1/2))						# Set skip pointer relative to size of word's posting list
			point[i] = 0													# Initialize each word's pointer to 0. We will adjust these as we go
=======
		# implement additional functionality to support methods 1 - 4
		#use unique document integer IDs
>>>>>>> 59c826006a69c65b3fd6016c943ca3443bcea2b6

	def exact_query(self, query_terms, k):
	#function for exact top K retrieval (method 1)
	#Returns at the minimum the document names of the top K documents ordered in decreasing order of similarity score
	
	def inexact_query_champion(self, query_terms, k):
	#function for exact top K retrieval using champion list (method 2)
	#Returns at the minimum the document names of the top K documents ordered in decreasing order of similarity score
	
	def inexact_query_index_elimination(self, query_terms, k):
	#function for exact top K retrieval using index elimination (method 3)
	#Returns at the minimum the document names of the top K documents ordered in decreasing order of similarity score
	
	def inexact_query_cluster_pruning(self, query_terms, k):
	#function for exact top K retrieval using cluster pruning (method 4)
	#Returns at the minimum the document names of the top K documents ordered in decreasing order of similarity score

	def print_dict(self):
        #function to print the terms and posting list in the index

	def print_doc_list(self):
	# function to print the documents and their document id
