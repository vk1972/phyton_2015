#!/usr/bin/env

"""
. Write a script that takes a file containing a number of words (one per line) and sorts them 
by the number of times they occur in the file (descending order), but exclude words that only 
occur once. Ignore the case of the words and filter out any punctuation characters. The output 
should contain lines each with word and the number of times it occurs in the input separated 
by space.
"""

import re
import collections
import operator

print '\n' + 'print list of read words' + '\n' + '------------------------'
with open('words.txt',"r") as f:
    words = ["".join(re.findall('\w+',l.lower().strip().split()[0])) for l in f if len(l.strip()) > 0]
    for w in words: print w

c = collections.Counter(words)


print '\n' + 'print counter map' + '\n' + '-----------------' + '\n' + str(c)


print '\n' + 'print words count' + '\n' + '-----------------'
with open('words_count.txt',"w") as f:
    for w in (w for w in sorted(c.items(), key=operator.itemgetter(1), reverse=True) if w[1] > 1):
        print '%s %d' % (w[0], w[1])
        f.write('%s %d \n' % (w[0], w[1]))

