#!/usr/bin/env python3
# encoding: utf-8

import re
import os
import collections
import time

class Index:
	def __init__(self,path):
		self.path = path
		self.index = {}
		self.doc_list = {}

	def buildIndex(self):
		#function to read documents from collection, tokenize and build the index with tokens
		#index should also contain positional information of the terms in the document --- term: [(ID1,[pos1,pos2,..]), (ID2, [pos1,pos2,…]),….]
		#use unique document IDs
		start = time.perf_counter()
		for docID, doc in enumerate(os.listdir(self.path), 1):
			with open(os.path.join(self.path, doc), 'r') as file_obj:
				doc_string = file_obj.read().lower()
			tok_list = filter(None, re.split(r"\W+", doc_string))
			self.doc_list[docID] = doc
			for pos, term in enumerate(tok_list, 1):
				if term not in self.index:
					self.index[term] = [(docID, [pos])]
				else:
					for i in range(len(self.index[term])):
						current_docID, positions = self.index[term][i]
						if current_docID == docID:	
							positions.append(pos)
							break
						elif i == len(self.index[term])-1:		
							self.index[term].insert(i, (docID, [pos]))

		end = time.perf_counter()
		print("Index built in {} seconds.".format(end-start))	


	def and_query(self, query_terms):
	#function for identifying relevant docs using the index
		start = time.perf_counter()

		size_q = len(query_terms)
		result = []
		point = {}
		base, done = True, False
		num_comp = 0
		
		for i in query_terms:
			point[i] = 0

		while not done:
			for i in query_terms:
				if base:
					contender = self.index[i][0][0]
					base = False
					continue
				elif done:
					break
				else:
					while self.index[i][point[i]][0] <= contender:
						if self.index[i][point[i]][0] == contender:
							num_comp += 1
							break
						elif self.index[i][point[i]] == len(self.index[i])-1:
							done = True
							break
						point[i] += 1
					else:
						contender = self.index[i][point[i][0]
						num_comp = 0
						continue	
					if num_comp == self_q-1:
						result.append(contender)
						for k in point:
							point[k] += 1
						contender = self.index[i][point[i]][0]
						num_comp = 0

		end = time.perf_counter()

		print("Results for the Query: {}".format(" AND ".join(query_terms)))
		print("Total Docs retrieved: {}".format(len(result))
		print(result)
		print("Retrieved in {} seconds.".format(end-start))

		

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
	index.and_query(['with','without','yemen'])
