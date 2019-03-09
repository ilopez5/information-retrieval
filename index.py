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
        self.documents = {}
        self.champion = {}
        self.stop_list = ['a','an','and','are','as','at','be','by','for','from','has','he','in','is','it','its','of','on','that','the','to','was','were','will','with']

    def buildIndex(self):
        #function to read documents from collection, tokenize and build the index with tokens
        start = time.perf_counter()
        for docID, doc in enumerate(os.listdir(self.path), 1):
            with open(os.path.join(self.path, doc), 'r') as file_obj:
                doc_string = file_obj.read().lower()
            tok_list = filter(None, re.split(r"\W+", doc_string))
            self.documents[docID] = [doc, [], [], []]
            for pos, term in enumerate(tok_list, 1):
                if term in self.stop_list:
                    continue
                elif term not in self.index: # first time term appears in INDEX
                    self.index[term] = [0, (docID, 1, [pos])]
                else:
                    for i in range(1,len(self.index[term])):
                        curr_docID, _, positions, _ = self.index[term][i]
                        if curr_docID == docID: # not the first time term appears in THIS document
                            positions.append(pos)
                            break
                        elif i == len(self.index[term])-1: # First time term appears in this document
                            self.index[term].append((docID, 1, [pos]))
        ################# Index Built, Now Insert IDF & Weighted TF ##################
        # N = len(self.documents)	| df_t = len(self.index[term]) - 1	| idf_t = log10(N/df_t)
        for term in self.index:
            self.index[term][0] = round(math.log10((len(self.documents)) / (len(self.index[term]) - 1)), 4) # IDF
            for i in range(1,len(self.index[term])):
                self.index[term][i] = (self.index[term][i][0], 1 + math.log10(len(self.index[term][i][2])), self.index[term][i][2])
        end = time.perf_counter()
        print("Index built in {} seconds.".format(end-start))

    def exact_query(self, query_terms, k):
        start = time.perf_counter()
        rank_list = [(0,0)]
        ############### Generating Query Vector ###############################
        q_list = re.split(r"\W+", query_terms.lower())
        vector_q = [(term, self.index[term][0]) for term in q_list if term not in self.stop_list]
        ltwo_q = 0
        for i in range(len(vector_q)):
            ltwo_q += (vector_q[i][1])**(2)
        norm_q = math.sqrt(ltwo_q)
        for i in range(len(vector_q)):
            vector_q[i] = (vector_q[i][0], vector_q[i][1] / norm_q)
        ############# Query vector is now normalized ##########################

        if not len(self.documents[1][1]): # Only generates vectors once.
            ################ Generating Doc Vectors For All Docs ##################
            for term in self.index:
                for i in range(1, len(self.index[term])):
                        self.documents[self.index[term][i][0]][1].append((term, self.index[term][i][1]*self.index[term][0]))
            #######################################################################
            
            ###################### Normalizing Doc Vectors ########################
            ltwo_d = 0
            for doc in self.documents:
                for i in range(len(self.documents[doc][1])):
                    ltwo_d += (self.documents[doc][1][i][1])**(2)
                norm_d = math.sqrt(ltwo_d)
                for i in range(len(self.documents[doc][1])):
                    self.documents[doc][1][i] = (self.documents[doc][1][i][0], self.documents[doc][1][i][1] / norm_d)
            #######################################################################

        ################## Calculate the Cosine Score #########################
        for doc in self.documents: # iterate over every document
            cos_score = 0
            for i in range(len(vector_q)): # iterate through query
                for tup in range(len(self.documents[doc][1])): # iterate through document vector's elements
                    if self.documents[doc][1][tup][0] == vector_q[i][0]:
                        cos_score += self.documents[doc][1][tup][1]*vector_q[i][1]
                        break
                    elif tup == len(self.documents[doc][1])-1:
                        break
            # Inserts doc/score, keeps rank order 
            for i in range(len(rank_list)):
                if cos_score == 0:
                    rank_list.append((doc, cos_score))
                    break
                if rank_list[i][1] <= cos_score:
                    rank_list.insert(i, (doc, cos_score))
                    break
        ###################### Ranked List Now Populated ######################

        ################### Print Top K & Performance Time ####################
        for i in range(k):
            print(f"{self.documents[rank_list[i][0]][0]:<13}, Score: {round(rank_list[i][1], 6)}")
        end = time.perf_counter()
        print("Results retrieved in {} seconds".format(end-start))
        ########################## End of Function ############################

    def inexact_query_champion(self, query_terms, k):
        start = time.perf_counter()
        rank_list = [(0,0)]
        ############### Generating Query Vector ###############################
        q_list = re.split(r"\W+", query_terms.lower())
        vector_q = [(term, self.index[term][0]) for term in q_list if term not in self.stop_list]
        ltwo_q = 0
        for i in range(len(vector_q)):
            ltwo_q += (vector_q[i][1])**(2)
        norm_q = math.sqrt(ltwo_q)
        for i in range(len(vector_q)):
            vector_q[i] = (vector_q[i][0], vector_q[i][1] / norm_q)
        ############# Query vector is now normalized ##########################

        if not len(self.documents[1][1]): # Only generates vectors once.
            ################ Generating Doc Vectors For All Docs ##################
            for term in self.index:
                for i in range(1, len(self.index[term])):
                        self.documents[self.index[term][i][0]][1].append((term, self.index[term][i][1]*self.index[term][0]))
            #######################################################################
            
            ###################### Normalizing Doc Vectors ########################
            ltwo_d = 0
            for doc in self.documents:
                for i in range(len(self.documents[doc][1])):
                    ltwo_d += (self.documents[doc][1][i][1])**(2)
                norm_d = math.sqrt(ltwo_d)
                for i in range(len(self.documents[doc][1])):
                    self.documents[doc][1][i] = (self.documents[doc][1][i][0], self.documents[doc][1][i][1] / norm_d)
            #######################################################################

        ################## Calculate the Cosine Score #########################
        for doc in self.documents: # iterate over every document
            cos_score = 0
            for i in range(len(vector_q)): # iterate through query
                for tup in range(len(self.documents[doc][1])): # iterate through document vector's elements
                    if self.documents[doc][1][tup][0] == vector_q[i][0]:
                        cos_score += self.documents[doc][1][tup][1]*vector_q[i][1]
                        break
                    elif tup == len(self.documents[doc][1])-1:
                        break
            # Inserts doc/score, keeps rank order 
            for i in range(len(rank_list)):
                if cos_score == 0:
                    rank_list.append((doc, cos_score))
                    break
                if rank_list[i][1] <= cos_score:
                    rank_list.insert(i, (doc, cos_score))
                    break
        ###################### Ranked List Now Populated ######################

        ################### Print Top K & Performance Time ####################
        for i in range(k):
            print(f"{self.documents[rank_list[i][0]][0]:<13}, Score: {round(rank_list[i][1], 6)}")
        end = time.perf_counter()
        print("Results retrieved in {} seconds".format(end-start))
        ########################## End of Function ############################



    def inexact_query_index_elimination(self, query_terms, k):
        #function for inexact top K retrieval using index elimination (method 3)
        start = time.perf_counter()
        rank_list = [(0,0)]
        ####################### Generating Query Vector #######################
        q_list = re.split(r"\W+", query_terms.lower())
        vector_q = sorted([(term, self.index[term][0]) for term in q_list if term not in self.stop_list], key=lambda tup: -tup[1])
        cut_off = len(vector_q) // 2
        vector_q = vector_q[:-cut_off]
        ######################## Shorter Vector Created #######################

        ####################### Normalize the vector ##########################
        ltwo_q = 0
        for i in range(len(vector_q)):
            ltwo_q += (vector_q[i][1])**(2)
        norm_q = math.sqrt(ltwo_q)
        for i in range(len(vector_q)):
            vector_q[i] = (vector_q[i][0], vector_q[i][1] / norm_q)
        ############# Query vector is now normalized ##########################

        if not len(self.documents[2][2]): # Only generates vectors once.
            ################ Generating Doc Vectors For All Docs ##################
            for term in self.index:
                for i in range(1, len(self.index[term])):
                    self.documents[self.index[term][i][0]][2].append((term, self.index[term][i][1]*self.index[term][0]))
            #######################################################################
            
            ###################### Normalizing Doc Vectors ########################
            ltwo_d = 0
            for doc in self.documents:
                for i in range(len(self.documents[doc][2])):
                    ltwo_d += (self.documents[doc][2][i][1])**(2)
                norm_d = math.sqrt(ltwo_d)
                for i in range(len(self.documents[doc][2])):
                    self.documents[doc][2][i] = (self.documents[doc][2][i][0], self.documents[doc][2][i][1] / norm_d)
            #######################################################################

        ################## Calculate the Cosine Score #########################
        for doc in self.documents: # iterate over every document
            cos_score = 0
            for i in range(len(vector_q)): # iterate through query
                for term in range(len(self.documents[doc][2])): # iterate through document vector's elements
                    if self.documents[doc][2][term][0] == vector_q[i][0]:
                        cos_score += self.documents[doc][2][term][1]*vector_q[i][1]
                        break
                    elif term == len(self.documents[doc][2])-1:
                        break
            # Inserts doc/score, keeps rank order
            for i in range(len(rank_list)):
                if cos_score == 0:
                    rank_list.append((doc, cos_score))
                    break
                if rank_list[i][1] <= cos_score:
                    rank_list.insert(i, (doc, cos_score))
                    break
        ###################### Ranked List Now Populated ######################

        ################### Print Top K & Performance Time ####################
        for i in range(k):
            print(f"{self.documents[rank_list[i][0]][0]:<13}, Score: {round(rank_list[i][1], 6)}")
        end = time.perf_counter()
        print("Results retrieved in {} seconds".format(end-start))
        ########################## End of Function ############################

    def inexact_query_cluster_pruning(self, query_terms, k):
        #function for exact top K retrieval using cluster pruning (method 4)
        #Returns at the minimum the document names of the top K docIDs ordered in decreasing order of similarity score
        pass

    def print_dict(self):
        #function to print the terms and posting list in the index
        for term,pos_list in self.index.items():
            print(term, ':', pos_list)

    def print_doc_list(self):
        # function to print the documents and their document id
        for docID, doc in self.documents.items():
            print("Doc ID: {0}  ==> {1}".format(docID, doc))

if __name__ == '__main__':
    index = Index('collection')
    index.buildIndex()
    index.exact_query('red china home', 5)
    index.inexact_query_index_elimination('red china home', 5)
    #index.inexact_query_champion('red china home', 5)
    #index.inexact_query_cluster_pruning('red china home', 5)
