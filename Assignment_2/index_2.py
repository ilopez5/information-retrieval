#!/usr/bin/env python3
# encoding: utf-8

#Python 3.0
import re
import os
import collections
import time
import math
import random
#import other modules as needed

class Index:
    def __init__(self,path):
        self.path = path
        self.index = {}
        self.documents = {}
        self.champion = {}
        self.stop_list = ['a','an','and','are','as','at','be','by','for','from','has','he','in','is','it','its','of','on','that','the','to','was','were','will','with']
        self.group = {}

    def buildIndex(self):
        #function to read documents from collection, tokenize and build the index with tokens
        start = time.perf_counter()
        ########################### Building our Index ###############################
        for docID, doc in enumerate(os.listdir(self.path), 1):
            with open(os.path.join(self.path, doc), 'r') as file_obj:
                doc_string = file_obj.read().lower()
            tok_list = filter(None, re.split(r"\W+", doc_string))
            self.documents[docID] = [doc, [], [], [], []]
            for pos, term in enumerate(tok_list, 1):
                if term in self.stop_list:
                    continue
                elif term not in self.index: # first time term appears in INDEX
                    self.index[term] = [0, (docID, 1, [pos])]
                else:
                    for i in range(1,len(self.index[term])):
                        curr_docID, _, positions = self.index[term][i]
                        if curr_docID == docID: # not the first time term appears in THIS document
                            positions.append(pos)
                            break
                        elif i == len(self.index[term])-1: # First time term appears in this document
                            self.index[term].append((docID, 1, [pos]))
        ################# Index Built, Now Insert IDF & Weighted TF ##################
        # N = len(self.documents)	| df_t = len(self.index[term]) - 1	| idf_t = log10(N/df_t)
        for term in self.index:
            self.index[term][0] = round(math.log10((len(self.documents)) / (len(self.index[term]) - 1)), 4)     # IDF
            for i in range(1,len(self.index[term])):
                ############ Determine R #################
                if (len(self.index[term]) - 1) <= 5:
                    r = len(self.index[term])
                else:
                    r = (len(self.index[term]) // 2) + 1
                ##########################################

                ##################### Insert weighted tf into index ######################
                w = 1 + math.log10(len(self.index[term][i][2]))
                self.index[term][i] = (self.index[term][i][0], w, self.index[term][i][2]) # Insert weighted frequency
                ##########################################################################

                ##################### Champions List (for Method 2) #######################
                if term not in self.champion:                                                    # Empty Champions List
                    self.champion[term] = [(self.index[term][i][0], w)]
                else:                                                                               # Existing Champions list
                    for j in range(len(self.champion[term])):                                       # Iterate thru, comparing scores
                        if self.champion[term][j][1] <= w:                                              # Insert, keeping list sorted
                            self.champion[term].insert(j, (self.index[term][i][0], w))
                            if len(self.champion[term]) >= r:                                           # Keeps length of list at r 
                                _ = self.champion[term].pop()
                            break
                        elif j == (len(self.champion[term]) - 1) and len(self.champion[term]) <= r: # We have reached end of list and still under r
                            self.champion[term].append((self.index[term][i][0], w))
                            break
                ###########################################################################
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
        print("Exact Top {}".format(k))
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

        ############# Generating Doc Vectors For Champion Docs ################
        count = 0
        for term in q_list: # Iterate over query terms
            if term in self.stop_list:
                continue
            for cdoc in range(len(self.champion[term])): # Iterate through champion documents
                count += 1
                # Want to check if document vector has this term already
                if len(self.documents[self.champion[term][cdoc][0]][3]) == 0: # Vector is empty
                    self.documents[self.champion[term][cdoc][0]][3].append((term, self.champion[term][cdoc][1]*self.index[term][0]))
                else:
                    for i in range(len(self.documents[self.champion[term][cdoc][0]][3])): # Iterate over doc vector
                        if self.documents[self.champion[term][cdoc][0]][3][i][0] == term: # term already in vector
                            break
                        elif i == len(self.documents[self.champion[term][cdoc][0]][3]) - 1: # End of vector, term not in here
                            self.documents[self.champion[term][cdoc][0]][3].append((term, self.champion[term][cdoc][1]*self.index[term][0]))
        #######################################################################

        ##################### If number of docs < k ###########################
        while count < k:
            for term in q_list: # Iterating through these terms so that the added docs are relevant
                if term in self.stop_list:
                        continue
                for tup in range(1, len(self.index[term])): # Iterate thru posting list
                    if not len(self.documents[self.index[term][tup][0]][3]):
                        self.documents[self.index[term][tup][0]][3].append((term, self.index[term][tup][1]*self.index[term][0]))
                        count += 1
                    if count >= k:
                        break
        #######################################################################

        ###################### Normalizing Doc Vectors ########################
        ltwo_d = 0
        for doc in self.documents:
            for i in range(len(self.documents[doc][3])):
                ltwo_d += (self.documents[doc][3][i][1])**(2)
            norm_d = math.sqrt(ltwo_d)
            for i in range(len(self.documents[doc][3])):
                self.documents[doc][3][i] = (self.documents[doc][3][i][0], self.documents[doc][3][i][1] / norm_d)
        #######################################################################

        ################## Calculate the Cosine Score #########################
        for doc in self.documents: # iterate over every document
            if len(self.documents[doc][3]) == 0:
                continue
            cos_score = 0
            for i in range(len(vector_q)): # iterate through query
                for tup in range(len(self.documents[doc][3])): # iterate through document vector's elements
                    if self.documents[doc][3][tup][0] == vector_q[i][0]:
                        cos_score += self.documents[doc][3][tup][1]*vector_q[i][1]
                        break
                    elif tup == len(self.documents[doc][3])-1:
                        break
            # Inserts doc/score, keeps rank order 
            for i in range(len(rank_list)):
                #print(doc, cos_score)
                if cos_score == 0:
                    rank_list.append((doc, cos_score))
                    break
                if rank_list[i][1] <= cos_score:
                    rank_list.insert(i, (doc, cos_score))
                    break
        ###################### Ranked List Now Populated ######################

        ################### Print Top K & Performance Time ####################
        print("Champs Top {}".format(k))        
        for i in range(k):
            print(f"{self.documents[rank_list[i][0]][0]:<13}, Score: {round(rank_list[i][1], 6)}")
        end = time.perf_counter()
        print("Results retrieved in {} seconds".format(end-start))
        ########################## End of Function ############################

    def inexact_query_index_elimination(self, query_terms, k):
        #function for inexact top K retrieval using index elimination (method 3)
        start = time.perf_counter()
        rank_list = []
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

        if not len(self.documents[1][2]): # Only generates vectors once.
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
            if len(rank_list) == 0:
                rank_list.append((doc, cos_score))
            else:
                for i in range(len(rank_list)):
                    if cos_score == 0:
                        rank_list.append((doc, cos_score))
                        break
                    if rank_list[i][1] <= cos_score:
                        rank_list.insert(i, (doc, cos_score))
                        break
        ###################### Ranked List Now Populated ######################

        ################### Print Top K & Performance Time ####################
        print("Index C. Top {}".format(k))        
        for i in range(k):
            print(f"{self.documents[rank_list[i][0]][0]:<13}, Score: {round(rank_list[i][1], 6)}")
        end = time.perf_counter()
        print("Results retrieved in {} seconds".format(end-start))
        ########################## End of Function ############################

    def inexact_query_cluster_pruning(self, query_terms, k):
        # function for exact top K retrieval using cluster pruning (method 4)
        start = time.perf_counter()
        rank_list = []
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
        
        ############# Create Clusters! #################
        if len(self.group) == 0:
            ################## Generate Leaders ####################
            leaders = []
            for i in range(int(math.sqrt(len(self.documents)))):
                leaders.append(random.randint(1,len(self.documents)))
            for lead in leaders:
                self.group[lead] = []
            ########################################################
            
            ###################### Generating Vectors for All Docs ####################
            for term in self.index:
                for i in range(1, len(self.index[term])):
                    self.documents[self.index[term][i][0]][4].append((term, self.index[term][i][1]*self.index[term][0]))
            #######################################################################

            ###################### Normalizing Doc Vectors ########################
            ltwo_d = 0
            for doc in self.documents:
                for i in range(len(self.documents[doc][4])):
                    ltwo_d += (self.documents[doc][4][i][1])**(2)
                norm_d = math.sqrt(ltwo_d)
                for i in range(len(self.documents[doc][4])):
                    self.documents[doc][4][i] = (self.documents[doc][4][i][0], self.documents[doc][4][i][1] / norm_d)
            #######################################################################

            ################## Pair Followers with Leaders ########################
            for doc in self.documents: # Iterate over all non-leader documents
                if doc in leaders: # ignore leaders, we are dealing with followers here
                    continue
                my_lead = []
                for lead in leaders: # Iterate over all leaders
                    cos_score = 0
                    for i in range(len(self.documents[doc][4])): # Iterate over doc vector
                        for j in range(len(self.documents[lead][4])): # Iterate over leader vector
                            if self.documents[doc][4][i][0] == self.documents[lead][4][j][0]: # If term == term
                                cos_score += self.documents[doc][4][i][1]*self.documents[lead][4][j][1] # multiply them and add to total
                                break
                    my_lead.append((lead, cos_score))
                my_lead = sorted(my_lead, key=lambda tup: -tup[1])
                for lead in my_lead:
                    if len(self.group[lead[0]]) < len(self.documents) // len(self.group):
                        self.group[lead[0]].append(doc)
                        break
        ############## Clusters have been created ##############
        
        ############## Compare Vector with Leaders #######################
        order = []
        for lead in self.group: # iterate over every leader
            cos_score = 0
            for q in range(len(vector_q)): # iterate through query vector
                for tup in range(len(self.documents[lead][4])): # iterate through document vector's elements
                    if self.documents[lead][4][tup][0] == vector_q[q][0]:
                        cos_score += self.documents[lead][4][tup][1]*vector_q[q][1]
                        break
            order.append((lead, cos_score))
        order = sorted(order, key=lambda tup: -tup[1])
        rank_list.append(order[0])
        # ##################################################################

        # ############# List of Documents to Score (in order) ##############
        doc_list = []
        for lead in self.group:
            doc_list.append(lead)
            for doc in self.group[lead]:
                doc_list.append(doc)
        # ##################################################################

        # ##################### Populate Ranked List #######################
        for doc in doc_list:
            if doc == rank_list[0][0]:
                continue
            cos_score = 0
            for term in range(len(vector_q)):
                for tup in range(len(self.documents[doc][4])):
                    if self.documents[doc][4][tup][0] == vector_q[term][0]:
                        cos_score += self.documents[doc][4][tup][1]*vector_q[term][1]
                        break
            for i in range(len(rank_list)):
                if rank_list[i][1] == doc:
                    continue
                if cos_score == 0:
                    rank_list.append((doc, cos_score))
                    break
                if rank_list[i][1] <= cos_score:
                    rank_list.insert(i, (doc, cos_score))
                    break
        # ##################################################################

        # ################### Print Top K & Performance Time ####################
        print("Cluster P. Top {}".format(k))        
        for i in range(k):
            print(f"{self.documents[rank_list[i][0]][0]:<13}, Score: {round(rank_list[i][1], 6)}")
        end = time.perf_counter()
        print("Results retrieved in {} seconds".format(end-start))
        ########################## End of Function ############################

    def print_dict(self):
        #function to print the terms and posting list in the index
        for term,pos_list in self.index.items():
            print(term, ':', pos_list)

    def print_doc_list(self):
        # function to print the documents and their document id
        for docID, doc in self.documents.items():
            print("Doc ID: {0}  ==> {1}".format(docID, doc[0]))

if __name__ == '__main__':
    index = Index('collection')
    index.buildIndex()
    ########################################################
    index.exact_query('red china home', 3)
    index.inexact_query_index_elimination('red china home', 3)
    index.inexact_query_champion('red china home', 3)
    index.inexact_query_cluster_pruning('red china home', 3)
    ########################################################
    index.exact_query('foreign town location', 4)
    index.inexact_query_index_elimination('foreign town location', 4)
    index.inexact_query_champion('foreign town location', 4)
    index.inexact_query_cluster_pruning('foreign town location', 4)
    ########################################################
    index.exact_query('band russian soviet', 5)
    index.inexact_query_index_elimination('band russian soviet', 5)
    index.inexact_query_champion('band russian soviet', 5)
    index.inexact_query_cluster_pruning('band russian soviet', 5)
    ########################################################
    index.exact_query('democratic institutions lobbies', 6)
    index.inexact_query_index_elimination('democratic institutions lobbies', 6)
    index.inexact_query_champion('democratic institutions lobbies', 6)
    index.inexact_query_cluster_pruning('democratic institutions lobbies', 6)
    ########################################################
    index.exact_query('government party political', 7)
    index.inexact_query_index_elimination('government party political', 7)
    index.inexact_query_champion('government party political', 7)
    index.inexact_query_cluster_pruning('government party political', 7)
    ########################################################