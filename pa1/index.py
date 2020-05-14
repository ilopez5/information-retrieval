#!/usr/bin/env python3
# encoding: utf-8
import re
import os
import collections
import time
import math as m

class Index:
	def __init__(self, path):
		self.path = path
		self.index = {}
		self.doc_list = {}

	def buildIndex(self):
		# function to iterate through a collection, tokenize the docs, and
		# build the index. index also contains positional info of terms within
		# documents (e.g., term: [(doc1,[pos1,..]), (doc2, [pos1,..]),..])

		start = time.perf_counter()

		# walk through collection and increment docID
		for docID, doc in enumerate(os.listdir(self.path), 1):
			with open(os.path.join(self.path, doc), 'r') as fd:
				doc_string = fd.read().lower()

			# tokenize the string using RegEx
			tok_list = filter(None, re.split(r"\W+", doc_string))

			# map unique docID to document
			self.doc_list[docID] = doc

			# walk token list and mark position
			for pos, term in enumerate(tok_list, 1):
				# create entry if first encounter of term
				if term not in self.index:
					self.index[term] = [(docID, [pos])]
				else:
					# walk through existing term entry in index
					for entry in self.index[term]:
						current_docID, positions = entry
						# signifies another term appearance in document
						if current_docID == docID:
							positions.append(pos)
							break
						elif entry == self.index[term][-1]:
							# first appearance of term in this document
							self.index[term].append((docID, [pos]))
		end = time.perf_counter()
		print("Index built in {0} seconds.".format(round(end-start, 2)))

	def and_query(self, query_terms):
		# implements boolean AND searching: we iterate through each term's
		# posting list simultaneously, looking for document ids that are common
		# to all the query terms. an optimization that is implemented here is
		# that of skip pointers: whenever possible, move ahead a set amount
		# (relative to size of the term's posting list). Otherwise, we move
		# ahead normally and make comparisons. 'Contender' refers to a docID
		# that we are checking holds all terms.
		start = time.perf_counter()

		query_length = len(query_terms)
		query = " AND ".join(query_terms)
		result = []

		# stores pointers to indexes for query terms
		point = skip = {}

		# initialize starting point and skip length
		for term in query_terms:
			# skip length set relative to size of posting list
			skip[term] = int(m.sqrt(len(self.index[term])))
			point[term] = 0

		# set first query term to contender
		contender = self.index[query_terms[0]][0][0]
		done = False
		num_comp = 0
		while not done:
			for term in query_terms:
				if not done:
					# docID <= contender? lets pointer catch up
					while self.index[term][point[term]][0] <= contender:
						# docID = contender?
						if self.index[term][point[term]][0] == contender:
							# update comparisons
							num_comp += 1
							break
						# is curr_idx is last element? (end condition)
						elif point[term] == len(self.index[term])-1:
							done = True
							break
						else:
							# check if skip puts us out of bounds
							if point[term] <= len(self.index[term])-(skip[term]+1):
								# ensure we dont skip past current contender
								if self.index[term][point[term] + skip[term]][0] < contender:
									# safely skip ahead
									point[term] += skip[term]
									continue

							# if we could not skip, step once normally
							point[term] += 1
					else:
						# docID > contender. set new contender and reset comparisons
						contender = self.index[term][point[term]][0]
						num_comp = 0
						continue

					# if contender been compared with all
					if num_comp == query_length-1 and not done and contender not in result:
						# add contender to results list
						result.append(contender)

						# checks if curr_idx is last element
						if point[term] == len(self.index[term]) - 1:
							done = True
							break
						else:
							# step all pointers forward once (safely)
							for term in point:
								if point[term] == len(self.index[term])-1:
									done = True
									break
								point[term] += 1

							# set new contender, then reset comparisons
							contender = self.index[term][point[term]][0]
							num_comp = 0

		end = time.perf_counter()

		print("Results for Query: {0}".format(query))
		print("Total Docs retrieved: {0}".format(len(result)))
		for docID in result:
			print(self.doc_list[docID])
		print("Retrieved in {} seconds.\n".format(round(end-start, 10)))

	def print_dict(self):
		# prints the terms corresponding index entry
		for term, entry in self.index.items():
			print(term, ':', entry)

	def print_doc_list(self):
		# prints the documents and their assigned document id
		for docID, doc in self.doc_list.items():
			print("Doc ID: {0:5} ==> {1}".format(docID, doc))

if __name__ == '__main__':
	index = Index('collection')
	index.buildIndex()
	index.and_query(['red','china'])
