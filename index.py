#Python 2.7.3
import re
import os
import collections
import time

class index:
	def __init__(self,path):
		self.path = path
		self.index = {}

	def buildIndex(self):
		#function to read documents from collection, tokenize and build the index with tokens
		#index should also contain positional information of the terms in the document --- term: [(ID1,[pos1,pos2,..]), (ID2, [pos1,pos2,…]),….]
		#use unique document IDs

		docID = 1
		punct = ".,;:'!?"		
		for file in os.listdir(self.path):								# Walks through dir
			#tok_list = []											# Declare list for tokens ?Might not need?
			x = open("Text-%i.txt" %docID, "r")							# Save file contents as one string 
			tok_list = x.split().lower()								# Creates a list of lower case tokens
			pos = 1												# Counter that marks position in document

			for term in tok_list:										# Walks thru file tokens (already in list)
				if term in punct:
					#pos += 1									# Do I want to increment pos after this?
					continue
				elif term not in self.index:
					self.index[term] = [(docID, [pos])]
					pos += 1
				else:
					for i in range(len(self.index[term])):
						if self.index[term][i][0] == docID:				# Current docID: Not first case
							self.index[term][i][1].append(pos)
							pos += 1
							break
						elif i == len(self.index[term])-1:				# Current docID: First case
							self.index[term].insert(i, (docID, [pos]))
							pos += 1

			docID += 1




	def and_query(self, query_terms):
	#function for identifying relevant docs using the index

	def print_dict(self):
        #function to print the terms and posting list in the index

	def print_doc_list(self):
	# function to print the documents and their document id
