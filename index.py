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
		for docID, doc in enumerate(os.listdir(self.path), 1):				# walk through collections and have docID increment
			with open(os.path.join(self.path, doc), 'r') as file_obj:		# create file object of current doc
				doc_string = file_obj.read().lower()						# read/save as string using re
			tok_list = filter(None, re.split(r"\W+", doc_string))			# tokenize string
			self.doc_list[docID] = doc										# this creates mapping from docID to doc
			for pos, term in enumerate(tok_list, 1):						# walk through token list, also increment position as we walk thru doc
				if term not in self.index:									# term not in index yet?
					self.index[term] = [(docID, [pos])]							# create appropriate key:value mapping
				else:														# term is in index already
					for i in range(len(self.index[term])):						# walks through post list
						current_docID, positions = self.index[term][i]			# grabs tuple information
						if current_docID == docID:								# compares keys
							positions.append(pos)									# updates pos list if match
							break
						elif i == len(self.index[term])-1:						# this check not really needed I guess
							self.index[term].append((docID, [pos]))				# appends new tuple

		end = time.perf_counter()
		print("Index built in {} seconds.".format(end-start))	


	def and_query(self, query_terms):
	#function for identifying relevant docs using the index
		start = time.perf_counter()

		size_q = len(query_terms)											# store size so we calculate once
		result = []															# list to output when done
		point = {}															# 'Pointers' to indexes for querie terms
		base, done = True, False											# Boolean variables to be used
		num_comp = 0														# initializing comparison counter
		
		for i in query_terms:
			point[i] = 0

		while not done:
			for i in query_terms:											# loops through query terms
				if base:														# base case
					contender = self.index[i][0][0]								# set initial element to contender	
					base = False												# So we dont do this again
					continue
				elif done:														# Use this to break out of for loop
					break				
				else:
					while self.index[i][point[i]][0] <= contender:			# docID <= contender?				
						if self.index[i][point[i]][0] == contender:				# docID = contender?
							num_comp += 1										# comp ++
							break												# break to next word
						elif point[i] == len(self.index[i])-1:					# checks if curr_idx is last element
							done = True											# Set condition to stop all
							break
						else:
							if point[i] <= len(self.index[i])-6:				# check curr_idx < 5th to last element
								if self.index[i][point[i]+5][0] < contender:	# peek to compare docID w/ contender
									point[i] += 5								# increment by 5 is less than
									continue
							point[i] += 1										# increment by 1 otherwise
					else:													# docID > contender
						contender = self.index[i][point[i]][0]					# set new contender 	
						num_comp = 0											# reset comparison counter
						continue
					if num_comp	== size_q-1 and not done:					# if contender been compared with all
						result.append(contender)								# add contender to results list
						if point[i] == len(self.index[i]) - 1:					# checks if curr_idx is last element
							done = True											# set condition to stop all
							break
						else:												# we are safe to adjust pointers +1
							for k in point:										# does the incrementing
								point[k] += 1
							contender = self.index[i][point[i]][0]				# sets new contender
							num_comp = 0										# resets comparison counter

		end = time.perf_counter()
		print("Results for the Query: {}".format(" AND ".join(query_terms)))
		print("Total Docs retrieved: {}".format(len(result)))
		for k in result:
			print(self.doc_list[k])
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
