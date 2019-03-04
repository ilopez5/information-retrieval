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
		stop_list = ['a','an','and','are','as','at','be','by','for','from','has','he','in','is','it','its','of','on','that','the','to','was','were','will','with']
		for docID, doc in enumerate(os.listdir(self.path), 1):
			with open(os.path.join(self.path, doc), 'r') as file_obj:
				doc_string = file_obj.read().lower()
			tok_list = filter(None, re.split(r"\W+", doc_string))
			self.docID_map[docID] = doc

			for pos, term in enumerate(tok_list, 1):
				if term in stop_list:
					continue
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
		matches = find_match(query_terms)
		for document in matches:
			

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

	def find_match(self, query_terms:
		size_q = len(query_terms)											# store size so we calculate once
		result = []															# list to output when done
		point = {}															# 'Pointers' to indexes for query terms
		skip = {}															# 'Skip Pointers' 
		base, done = True, False											# Boolean variables to be used
		num_comp = 0														# initializing comparison counter
		
		for i in query_terms:
			skip[i] = int((len(self.index[i]))**(1/2))						# Set skip pointer relative to size of word's posting list
			point[i] = 0													# Initialize each word's pointer to 0. We will adjust these as we go

		while not done:
			for i in query_terms:											# loops through query terms
				if base:														# base case
					contender = self.index[i][0][0]								# set initial element to contender	
					base = False												# So we dont do this again
					continue
				elif done:														# Use this to break out of for loop
					break				
				else:
					while self.index[i][point[i]][0] <= contender:			# docID <= contender? This loop repeats until pointer catches up
						if self.index[i][point[i]][0] == contender:				# docID = contender?
							num_comp += 1											# comp ++
							break													# break to next word
						elif point[i] == len(self.index[i])-1:					# checks if curr_idx is last element (end condition)
							done = True												# Set condition to stop all
							break
						else:
							if point[i] <= len(self.index[i])-(skip[i]+1):			# Makes sure we dont go out of index range (for skip check)
								if self.index[i][point[i]+skip[i]][0] < contender:	# Checks if skip pointer less than current id
									point[i] += skip[i]								# increments pointer by the skip length
									continue
							point[i] += 1										# increment by 1 otherwise
					else:													# docID > contender
						contender = self.index[i][point[i]][0]					# set new contender 	
						num_comp = 0											# reset comparison counter
						continue
					if num_comp == size_q-1 and not done:					# if contender been compared with all
						result.append(contender)								# add contender to results list
						if point[i] == len(self.index[i]) - 1:					# checks if curr_idx is last element
							done = True											# set condition to stop all
							break
						else:												# we are safe to adjust pointers +1
							for k in point:										# does the incrementing
								if point[k] == len(self.index[k])-1:
									done = True
									break
								point[k] += 1
							contender = self.index[i][point[i]][0]				# sets new contender
							num_comp = 0
		return result

if __name__ == '__main__':
	index = Index('collection')
	index.buildIndex()