#!/usr/bin/env

"""
Write a script that removes blank paragraphs from HTML document. A blank paragraph 
should be considered to be a <p> </p> tag containing only white spaces.
"""


from HTMLParser import HTMLParser

class PStripper(HTMLParser):
    def __init__(self, tag_to_strip):
        self.reset()
        self.tag_to_strip = tag_to_strip
        self.striped =[]   #buffer that contains html without tag to be stripped
        self.current_starttag = ''
        self.current_data = ''
        self.current_endtag = ''
        self.current_comment = ''
        self.current_tag_to_strip = ''  # buffer that contains current parsing result for tag to be stripped
        self.previos_tag_type = ''
        self.posible_nesting = 0
        self.empty_tag_to_strip_len = 2 + len(tag_to_strip) + 3 + len(tag_to_strip) # <tag></tag> = (2+len(tag)) + (3+len(tag)) 


    def handle_starttag(self, tag, attrs):
        if(self.previos_tag_type == 'start'):
            if tag == self.tag_to_strip: self.posible_nesting += 1   #maybe it is about form <p>data<p>something</p><p>
            self.current_data = self.current_data.translate(None, '\n\r').strip()
            self.printCurrentChunk("\033[94m" + 'No end tag, possible nesting' + "\033[00m", '')   
            self.current_endtag = ''        
        # tag of form <p>some data <p>some more data -- without closing tag
        # this kind of tag will be outputed if it is not tag to strip
        # this block handles case when this kind of tag is also tag to be striped
        if self.current_starttag == self.tag_to_strip and self.current_endtag == '' and self.current_data.strip() != '':       
            self.striped.append(self.current_tag_to_strip) # so we have tag of form <p>data that will be outputed to new html
            if tag == self.tag_to_strip: self.posible_nesting += 1   #maybe it is about form <p>data<p>something</p><p>
        
        #basic start tag case
        self.current_starttag, self.current_data, self.current_endtag = tag, '', ''
        self.current_tag_to_strip = ''

        if attrs: 
            for a in attrs: tag += " " + a[0] + "='" + a[1] + "' "
    
        if tag != self.tag_to_strip:
            self.striped.append('\n<' + tag + '>')  #output to new html
        else: 
            self.current_tag_to_strip = '\n<' + tag + '>'  #output to buffer which will be examined later (if it has some data)

        self.previos_tag_type = 'start'

    def handle_data(self, d):
        if(d.strip() != ''):
            self.current_data = d
            if self.current_starttag != self.tag_to_strip:
                self.striped.append(d)
            else: 
                self.current_tag_to_strip += d


 
    def handle_endtag(self, tag):
        msg = ''
        if(self.previos_tag_type == 'end'):
            if(self.current_starttag != self.current_endtag):
                if tag == self.tag_to_strip: self.posible_nesting += 1 
                msg = "\033[94m" + 'No start tag, possible nesting' + "\033[00m"
            self.current_starttag = ''
        # tag of form <p>some data <p>some more data -- without closing tag
        # this kind of tag will be outputed to new html if it is not tag to strip
        # this block handles case when this kind of tag is also tag to be striped
        # and whole document until </body> was outputed
        elif self.current_starttag == self.tag_to_strip and self.current_endtag == '' and len(self.current_tag_to_strip) > self.empty_tag_to_strip_len: 
            self.striped.append(self.current_tag_to_strip)
            self.current_tag_to_strip = ''
            if tag == self.tag_to_strip and self.posible_nesting > 0: 
                 self.posible_nesting -= 1
                 msg = "\033[92m" + 'Recognized as nesting' + "\033[00m"
        
	self.current_endtag = tag
        if tag != self.tag_to_strip:
            if tag != self.current_starttag: 
                self.striped.append('\n') 
                msg = "\033[92m" + 'Recognized as nesting' + "\033[00m"
            else:
                msg = ''
            self.striped.append('</' + tag + '>')
        else:
            if self.previos_tag_type == 'end' and self.posible_nesting > 0: #<p>bla<p>bla</p></p> case
                self.posible_nesting -= 1
                self.striped.append('\n</' + tag + '>')
                msg = "\033[92m" + 'Recognized as nesting' + "\033[00m"
            elif self.previos_tag_type != 'end':
                if self.current_starttag == self.tag_to_strip and self.current_data.strip() != '':  
                    #<p>bla bla</p> case
                    self.current_tag_to_strip += '</' + tag + '>'
                    self.striped.append(self.current_tag_to_strip)
                    msg = "\033[94m" + 'has data (not empty tag)' + "\033[00m"
                elif self.posible_nesting > 0:
                    self.posible_nesting -= 1
                    self.striped.append('\n</' + tag + '>')
                    msg = "\033[92m" + 'Recognized as nesting' + "\033[00m"
                else:
                    msg = "\033[91m" + 'Will be striped' + "\033[00m"
            else:
                if self.posible_nesting > 0: 
                   self.posible_nesting -= 1 
                   self.striped.append('\n</' + tag + '>')
                   msg = "\033[92m" + 'Recognized as nesting' + "\033[00m"
                                
        self.previos_tag_type = 'end'  
        self.printCurrentChunk(msg, '')

    def handle_comment(self, c):
        msg = ''
        #print "comment  :", c, " , start tag: ", self.current_starttag 
        if (self.current_starttag != self.tag_to_strip):
            self.striped.append('<!--' + c + '-->')
            msg = "\033[91m" + 'Will be striped' + "\033[00m" 
        else:
            self.current_tag_to_strip += '<!--' + c + '-->'
        self.current_comment = c
        #self.printCurrentChunk(msg, 'comment') 

    def handle_decl(self, data):
        self.striped.append('<' + data + '>')

    def get_data(self):
        return ''.join(self.striped)

    def printCurrentChunk(self, msg, type):
        if(type == 'comment'):
	    print "<!--{0}-->  {1}".format(self.current_comment, msg)
        elif(self.current_starttag == self.current_endtag):
            print "<{0}>{1}</{2}>  {3}".format(self.current_starttag, self.current_data, self.current_endtag, msg)
        elif(self.current_starttag != self.current_endtag and self.current_starttag != '' and self.current_endtag != ''):
            print "</{0}> {1}".format(self.current_endtag, msg)
        else:
            if(self.current_starttag != '' and self.current_endtag == ''):
                print "<{0}>{1}  {2}".format(self.current_starttag, self.current_data, msg)
            if(self.current_starttag == '' and self.current_endtag != ''):
                print "</{0}>  {1}".format(self.current_endtag, msg)
        #print 'previous tag type: ' + self.previos_tag_type


        

def strip_tags(html, tag_name):
    print "-------------------------------------------------"
    s = PStripper(tag_name)
    s.feed(html)
    return s.get_data()


with open('html_in.html',"r") as inf, open('html_out_1.html',"w") as outf:
   outf.write(strip_tags(inf.read(), 'p'))


   
