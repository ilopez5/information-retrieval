#!/usr/bin/env python3
# encoding: utf-8

#Python 3.0
import re
import os
import collections
import time
import math
#import other modules as needed

class Index:
	def __init__(self,path):
		self.path = path
		self.index = {}
		self.docID_map = {}

	def buildIndex(self):
		#function to read documents from collection, tokenize and build the index with tokens
		start = time.perf_counter()
		for docID, doc in enumerate(os.listdir(self.path), 1):
			with open(os.path.join(self.path, doc), 'r') as file_obj:
				doc_string = file_obj.read().lower()
			tok_list = filter(None, re.split(r"\W+", doc_string))
			self.docID_map[docID] = doc

			for pos, term in enumerate(tok_list, 1):
				if term not in self.index:
					self.index[term] = [0, (docID, 1, [pos])]
				else:
					for i in range(1,len(self.index[term])):
						curr_docID, weight, positions = self.index[term][i]
						if curr_docID == docID:
							positions.append(pos)
							weight = 1 + math.log10(len(positions)) # tf_td = len(positions)
							break
						elif i == len(self.index[term])-1:
							self.index[term].append((docID, 1,[pos]))
		# N = len(self.docID_map)	| df_t = len(self.index[term]) - 1	| idf_t = log10(N/df_t)
		for term in self.index:
			self.index[term][0] = round(math.log10((len(self.docID_map)) / (len(self.index[term]) - 1)), 4)
		end = time.perf_counter()
		print("Index built in {} seconds.".format(end-start))

	def exact_query(self, query_terms, k):
	#function for exact top K retrieval (method 1)
	#Returns at the minimum the document names of the top K documents ordered in decreasing order of similarity score
		pass
	def inexact_query_champion(self, query_terms, k):
	#function for exact top K retrieval using champion list (method 2)
	#Returns at the minimum the document names of the top K documents ordered in decreasing order of similarity score
		pass
	def inexact_query_index_elimination(self, query_terms, k):
	#function for exact top K retrieval using index elimination (method 3)
	#Returns at the minimum the document names of the top K documents ordered in decreasing order of similarity score
		pass
	def inexact_query_cluster_pruning(self, query_terms, k):
	#function for exact top K retrieval using cluster pruning (method 4)
	#Returns at the minimum the document names of the top K documents ordered in decreasing order of similarity score
		pass
		
	def print_dict(self):
		#function to print the terms and posting list in the index
		for term,pos_list in self.index.items():
			print(term, ':', pos_list)

	def print_doc_list(self):
		# function to print the documents and their document id
		for docID, doc in self.doc_list.items():
			print("Doc ID: {0}  ==> {1}".format(docID, doc))

if __name__ == '__main__':
	index = Index('collection')
	index.buildIndex()