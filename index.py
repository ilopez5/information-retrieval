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
		start = time.time()
		docID = 1		
		for doc in os.listdir(self.path):							# Walks through dir
			file_obj = open(doc, "r")								# Save file contents as one string 
			doc_string = os.read(file_obj).lower()					# Creates a list of lower case tokens
			tok_list = re.split(r"\W", doc_string)

			pos = 1													# Counter that marks position in document
			for term in tok_list:									# Walks thru file tokens (already in list)
				if term not in self.index:
					self.index[term] = [(docID, [pos])]
					pos += 1
				else:
					for i in range(len(self.index[term])):
						if self.index[term][i][0] == docID:			# Current docID: Not first case
							self.index[term][i][1].append(pos)
							pos += 1
							break
						elif i == len(self.index[term])-1:			# Current docID: First case
							self.index[term].insert(i, (docID, [pos]))
							pos += 1

			docID += 1
		end = time.time()
		print("Index built in {} seconds.".format(end-start))	




	def and_query(self, query_terms):
	#function for identifying relevant docs using the index
		print('Results for the Query: ')



	def print_dict(self):
		#function to print the terms and posting list in the index
		for term,pos_list in self.index.items():
			print(term, ':', pos_list)



	def print_doc_list(self):
	# function to print the documents and their document id
		docID = 1
		for doc in os.listdir(self.path):
			print("Doc ID: {0}  ==> Text-{0}.txt".format(docID))
