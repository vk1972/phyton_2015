#!/usr/bin/env

"""
Write a script that removes blank paragraphs from HTML document. A blank paragraph 
should be considered to be a <p> </p> tag containing only white spaces.
"""



import re

p = re.compile('<p>\s*</p>', re.IGNORECASE)

with open('html_in.html',"r") as inf, open('html_out.html',"w+") as outf:
   
   doc = inf.read()
   while True:
       l=re.split(p, doc)
       doc = ''.join([t for t in l])
       if len(l) == 1:  break
   outf.write(doc)  
