# Assignment 1


### Merge Algorithm

To keep track of _n_ lists, I make use of built-in Python dictionary to store _pointers_.
I create two dictionaries named **point** and **skip**.
For every word in the query, I pass it into both dictionaries but with different values.

#### In **_point_**:
I set them equal to 0. This signifies the index they are to be pointing at in the posting list.

#### In **_skip_**:
I calculate the length of the current word's posting length. Then, I set the skip distance to the square root of that length. In other words, the longer the posting list for a word, the longer the skip distance.

Once both these dictionaries are ready, I begin the process.

#### Comparisons and Adjusting Pointers
An overarching `while` loop continues endlessly unless the end condition is met, or `done = True`.
Within this loop, we continuously walk through each word in the query. At each iteration, we check if the docID the current pointer is pointing to is less than or equal to the current *contender*. If so, a small loop aims to shift that pointer until it finds a match with the contender or passes it, signifying the current contender is not a match and therefore setting a new one. During this inner loop, there is a check that essentially peeks ahead by the skip distance for that word to see if that docID is still smaller than the current contender. If so, we adjust the pointer by that skip distance. Otherwise, we increment by one (given we now know it is near our current index).

Now, in order to know when a contender is a good match for all query words, I keep a variable `num_comp` as a counter. It increments with each comparison and if it reaches *n-1* comparisons, i.e. it has been compared with the posting list of every other word than the one that set it, then we know the contender is a match. Thus, it is added to the result list which stores the docIDs that are shared by all query terms.

#### End conditions
The search terminates once the end of a posting list for any given word is reached. 

This algorithm only checks each item in the posting list once, and
