#! /usr/bin/env python3
# encoding: utf-8
#Python 3.0
import collections as c
import time
import math as m
#import other modules as needed

class PageRank:
	def __init__(self):
		self.tmatrix = []


	def pagerank(self, input_file):
		# function to implement pagerank algorithm input_file - input file 
		# that follows the format provided in the assignment description
		start = time.perf_counter()
		graph = self.parse(input_file)					# Parse file
		N, status = graph[0], True						# Variables
		self.trans_matrix(graph, N)						# Generate Trans Matrix
		pi = [1/N]*N									# Initial pi vector
		while status:
			pi, status = self.power_iter(pi, N, status)	# Power Iteration
		end = time.perf_counter()
		self.print_vect(pi, input_file, N)					# Print Top Results
		print("PageRank generated in {} seconds.".format(end-start))
		return


	def trans_matrix(self, graph, N):
		# Creates Transition Matrix
		alpha = .15
		self.tmatrix = [0] * N							# Init N docs to 0
		count = c.defaultdict(int)						# Keeps count to div by

		# Initialize Matrix
		for i in range(2, len(graph), 2):
			src, dest = graph[i], graph[i+1]
			if self.tmatrix[src] == 0:
				self.tmatrix[src] = [0] * N
			self.tmatrix[src][dest] += 1
			count[src] += 1								# Increment count

		# Finalize Matrix
		for ind, row in enumerate(self.tmatrix, 0):
			nalpha, a, b = 1-alpha, (1-alpha) / N, alpha / N
			if count[ind] == 0:							# Dead End
				self.tmatrix[ind] = [1/N]*N				# Replace row w/ 1/N
			else:
				for entry in range(len(row)):
					row[entry] = ((row[entry] / count[ind]) * nalpha) + b
		return


	def power_iter(self, oldpi, N, status):
		# Multiplying current Pi vector with Trans Matrix
		pi = [0] * N									# Init new vector
		for col in range(N):							# Iterate Columns
			score = 0
			for i in range(N):							# Iter ith col of rows
				score += oldpi[i] * self.tmatrix[i][col]
			pi[col] = score
		if m.fabs(pi[0]-oldpi[0]) < 0.0000000000000001:	# Converged?
			status = False
		return pi, status		


	def print_matrix(self):
		# Tool to see Transition matrix
		for row in self.tmatrix:
			print(row)
		return


	def print_vect(self, pi, input_file, N):
		# Prints the final vector
		dct = c.defaultdict(float)
		for i in range(len(pi)):
			dct[i] = pi[i]
		dct = sorted(dct.items(), key=lambda x: x[1], reverse=True)
		print("Output for file {}".format(input_file))
		print("Using initial vector with value 1/{} for each element".format(N))
		print("Doc:	PageRank Score:		\n==========================")
		for doc,score in dct:
			print("D{0}	{1}".format(doc, score))
		print("==========================")
		return


	def parse(self, input_file):
		# Opens file and parses into list of integers
		file = ""
		with open(input_file, 'r') as f:
			file = f.read().lower()
		return self.str_int(file.split())
		

	def str_int(self, lst):
		# Used to convert strs to ints
		for i in range(len(lst)):
			lst[i] = int(lst[i])
		return lst


if __name__ == '__main__':
	a = PageRank()
	a.pagerank('test3.txt')		# Lecture Example, Correct
