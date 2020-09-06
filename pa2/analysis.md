# Assignment 3

### Methods Implemented:
1. Exact Top K
2. Inexact Top K: Champions List
3. Inexact Top K: Index Compression
4. Inexact Top K: Cluster Pruning

### Implementation:
Generally speaking, there is one python dictionary where I stored all document vectors across all methods, `self.documents`. Here, the following format was followed:
```Python
self.documents[document_ID] = ["Text-#.txt", [Mthd_1_Vector], [Mthd_2_Vector], [Mthd_3_Vector], [Mthd_4_Vector]]
```

The reason for this was primarily to keep each method independent of one another, in order to truly compare the inexact variations to the exact.

Generally, I created document vectors with elements of tuples containing a term and tf-idf score, such as `(term, tf-idf)`. When computing the dot product of two vectors, I simply iterated through both vectors, and once a term matched, I multiplied their tf-idf scores and added them to the cumulating total. I think with more time, I could implement a way to have it be sorted, as well as populating the gaps, in order to have the indices match for a given term (whether present or not).

### Performance
To measure performance, I am using **Precision**, **Recall**, and **F-measure**. After testing with 5 equal inquiries, these are my findings.
