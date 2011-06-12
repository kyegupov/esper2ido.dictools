# coding: utf-8

import json,codecs,re,math,os
from StringIO import StringIO
import glob
from HTMLParser import HTMLParser 
from htmlentitydefs import name2codepoint

import cPickle, json

   
re_separator = re.compile("[;,]")
re_optionalPart = re.compile(ur"\([a-zéèçàœæôê]+\)", re.I+re.U)

re_ulx = re.compile("^(ul[oaiu], )*(ul[oaiu])$")

    
def parse_source(langletter):
    articles = []


    S_EXPECT_WORD = 0
    S_READING_WORD = 1
    S_READING_DEF = 3

    strong = ["b","strong"]
    em = ["i","em"]




    class MyParser(HTMLParser):
        def __init__(self):
            HTMLParser.__init__(self)
            self.state = 0
            self.in_key = False
            self.key = ""
            self.curKeys = []
            self.baseword = ""
            self.lastroot = ""
            self.curArticle = ""
            self.lastword = ""
            self.c = 0
            self.is_new_entry = True
            self.chain = []
            self.in_lang_sources = False
            self.nextEntryChain = []
            self.in_cf = False
            self.in_vexp = False
            
        def handle_starttag(self, tag, attrs):
            if tag=="p":
                self.state+=1
            if self.state == 2:
                if tag in strong:
                    self.in_key = True
                    self.chain.append("b")
                    self.curArticle += "<b>"
                if tag in em:
                    self.chain.append("i")
                    self.curArticle += "<i>"
                        
                if tag=="br":
                    if self.in_key:
                        self.register_keyword()
                    self.nextEntryChain = self.chain[:]
                    self.chain.reverse()
                    for tn in self.chain:
                        self.curArticle += "</"+tn+">"
                    self.save_article(True)
                    for tn in self.nextEntryChain:
                        if tn=="b":
                            self.in_key = True
                        self.curArticle += "<"+tn+">"
                    
                else:
                    pass
                    #~ self.chain.append(tag)
            
        def handle_endtag(self, tag):
            if self.state == 2:
                
                if tag in strong:
                    if self.in_key:
                        self.register_keyword()
                        assert self.chain==[] or self.chain.pop() == "b"
                        self.curArticle += "</b>"
                        self.in_key = False
                if tag in em:
                    assert self.chain.pop() == "i"
                    self.curArticle += "</i>"
                    

        
        def handle_data(self, data):
            if self.state == 2:
                if self.in_lang_sources:
                    return
                if unichr(8212) in data:
                    data = data.split(unichr(8212))[0].rstrip()        
                    self.in_lang_sources = True
                if self.nextEntryChain:
                    data = data.lstrip()
                if self.in_key:
                    self.key += data
                    self.curArticle += data
                else:
                    self.curArticle += data
                cf = "cf." if langletter=="I" else "see"
                if data.find(cf)>-1:
                    self.in_cf = True
                if data.find(" V. exp.")>-1 or data.find("Ant.:")>-1:
                    self.in_vexp = True
        
        def handle_charref(self, name):
            cpoint = int(name)
            if cpoint>255:
                self.handle_data(unichr(cpoint))
            else:
                self.handle_data(chr(cpoint).decode("cp1252"))

        def handle_entityref(self, name):
            self.handle_data(unichr(name2codepoint[name]))

        def handle_startendtag(self, tag, attrs):
            if self.state == 2:
                if tag=="br":
                    if self.in_key:
                        self.add_corrected_key()
                    self.chain.reverse()
                    for tn in self.chain:
                        self.curArticle += "</"+tn+">"
                    self.save_article(True)
                #~ if attrs:
                    #~ print "oh boy, attrs!", attrs
                    #~ raise

        def register_keyword(self):
            self.key = self.key.replace(u"\n",u" ").replace(u"\r",u"").strip().rstrip("*")
            lbraces = self.curArticle.count("(")
            rbraces = self.curArticle.count(")")
            if self.key and (not self.in_cf) and (not self.in_vexp) and (not self.key.endswith(":") and (rbraces==lbraces)):
                pass
                #~ print (self.key, self.curArticle)
                #~ print (self.key, (not self.in_cf) , (not self.in_vexp) , (not self.key.endswith(":")))
                #~ raise hell
            self.key = self.key.rstrip(":")
            keys = []
            for k in re_separator.split(self.key):
                words = k.strip().split(" ")
                if self.baseword=="" and len(words)==1:
                    self.baseword = words[0].split("-")[0]
                words2 = []

                for w in words:
                    if langletter=="e":
                        words2.append(w)
                    else:
                        if w.startswith("-") and self.baseword!="":
                            ww = self.baseword+w[1:].replace("-","")
                        else:
                            ww = w.replace("-","")
                        words2.append(ww.replace("*", ""))
                newkey = " ".join(words2).lower()
                optionalSuffixes = re_optionalPart.findall(newkey)
                if newkey!="":
                    if len(optionalSuffixes)>0:
                        if newkey!=optionalSuffixes[0]:
                            keys.append(newkey.replace(optionalSuffixes[0], "").strip())
                            keys.append(newkey.replace(optionalSuffixes[0], optionalSuffixes[0][1:-1]))
                    else:
                        keys.append(newkey)
            
            self.curKeys.extend(keys)
            self.key = ""
            self.in_cf = False
              
        def save_article(self, end_of_entry):

            assert len(self.curKeys)!=0, self.curArticle
            for k in self.curKeys[:]:
                latinized = k.replace(u"é", "e").replace(u"è","e").replace(u"ç","c").replace(u"à","a").replace(u"œ","oe").replace(u"æ","ae").replace(u"ô", "o").replace(u"ê", "e")
                if k!=latinized:
                    self.curKeys.append(latinized)
            articles.append((self.curArticle.replace("\n"," ").replace("\r","").replace("  "," ").strip(), self.curKeys))
                    
            self.key = ""
            self.curArticle = ""
            self.curKeys = []
            self.baseword = ""
            self.chain = []
            self.in_lang_sources = False
            self.in_vexp = False

            
    for fn in glob.glob(langletter+"*.htm"):
        print fn
        p = MyParser()
        text = open(fn, "rt").read().decode('latin-1')
        text = text.replace("</b>(<b>", "(").replace("</b>)<b>", ")")
        lines = text.splitlines()
        p.feed(text)
        
    return articles    
    
   
for langprefix in ["io","en"]:    

    articles = parse_source(langprefix[0])
    cPickle.dump(articles, open(langprefix+".pickle", "wb"))
    json.dump(articles, open(langprefix+".json", "wb"), indent=4)
    
