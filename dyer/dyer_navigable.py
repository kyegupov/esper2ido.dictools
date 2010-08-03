# coding: utf-8

import json,codecs,re,math,os
from StringIO import StringIO
import glob
from HTMLParser import HTMLParser 
from htmlentitydefs import name2codepoint

def distribute(accum):
    weights = [min(e[1],pagesize) for e in accum]
    s = sum(weights)
    if s<=pagesize:
        name = accum[0][0]+"-"+accum[-1][0]
        if accum[0][0] == accum[-1][0]:
            name = accum[0][0]        
        return [(name,s)]
    n = int(math.ceil(s/pagesize))
    maxmin = 0
    best = []
    #~ print weights
    while True:
        assert n<len(weights)
        found = False
        for res in bruteforce_distribution(weights, n, 0, 0):
            found = True
            borders = zip([0]+res,res+[len(weights)])
            distrib = [sum(weights[i0:i1]) for i0,i1 in borders]
            if min(distrib)>maxmin:
                maxmin = min(distrib)
                best = borders
        if found:
            break
        n+=1
    r = []
    for i0,i1 in best:
        name = accum[i0][0]+"-"+accum[i1-1][0]
        if accum[i0][0] == accum[i1-1][0]:
            name = accum[i0][0]
        r.append((name,sum(e[1] for e in accum[i0:i1])))
    return r

def bruteforce_distribution(weights, max_pieces,  already, last_occupied):
    for i in range(last_occupied+1, len(weights)-(max_pieces-already-1)):
        if sum(weights[last_occupied:i])>pagesize:
            break
        if already+1==max_pieces:
            if sum(weights[i:])<=pagesize:
                yield [i]
        else:
            for residue in bruteforce_distribution(weights, max_pieces, already+1, i):
                yield [i]+residue



def process_node(node):
    snk = sorted(node.keys())
    accum = []
    global c
    for k in snk:
        if node[k]["count"]>pagesize and node[k]["kids"]:
            if accum:
                for e in distribute(accum):
                    yield e
            for e in process_node(node[k]["kids"]):
                yield e
            accum = []
        else:
            accum.append((k,node[k]["count"]))
    if accum:
        for e in distribute(accum):
            yield e
        
try:
    os.mkdir("navigable_dict")
except:
    pass
try:
    os.mkdir("navigable_dict/en")
except:
    pass
try:
    os.mkdir("navigable_dict/io")
except:
    pass
    
    
def parse_source(langletter):
    articles = []

    re_w = re.compile("[a-zA-Z]*-?[a-zA-Z]+")

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
            self.baseword = ""
            self.lastroot = ""
            self.article = ""
            self.lastword = ""
            self.c = 0
            self.is_new_entry = True
            self.chain = []
            self.in_lang_sources = False
            
        def handle_starttag(self, tag, attrs):
            if tag=="p":
                self.state+=1
            if self.state == 2:
                #~ if attrs:
                    #~ print "oh boy, attrs!", attrs
                    #~ raise
                if tag in strong:
                    self.in_key = True
                if tag in em:
                    self.chain.append("ex")
                    self.article += "<ex>"
                        
                if tag=="br":
                    if self.in_key:
                        self.add_corrected_key()
                    self.chain.reverse()
                    for tn in self.chain:
                        self.article += "</"+tn+">"
                    self.save_article(True)
                    
                else:
                    pass
                    #~ self.chain.append(tag)
            
        def handle_endtag(self, tag):
            if self.state == 2:
                
                if tag in strong:
                    if self.in_key:
                        self.add_corrected_key()
                        self.in_key = False
                if tag in em:
                    assert self.chain.pop() == "ex"
                    self.article += "</ex>"
                    

        
        def handle_data(self, data):
            if self.state == 2:
                if self.in_lang_sources:
                    return
                if unichr(8212) in data:
                    data = data.split(unichr(8212))[0].rstrip()        
                    self.in_lang_sources = True
                if self.in_key:
                    self.key += data
                else:
                    self.article += data
        
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
                        self.article += "</"+tn+">"
                    self.save_article(True)
                #~ if attrs:
                    #~ print "oh boy, attrs!", attrs
                    #~ raise

        def add_corrected_key(self):
            self.key = self.key.replace(u"\n",u" ").strip()
            keys = []
            for k in self.key.split(u","):
                words = k.strip().split(" ")
                if self.baseword=="" and len(words)==1:
                    self.baseword = words[0].split("-")[0]
                words2 = []

                for w in words:
                    if langletter=="e":
                        words2.append(w)
                    else:
                        if w.startswith("-") and self.baseword!="":
                            words2.append(self.baseword+w[1:].replace("-",""))
                        else:
                            words2.append(w.replace("-",""))
                keys.append(" ".join(words2))
            
            wrapped = ", ".join(["<k>"+key.strip()+"</k>" for key in keys])
            self.article += " "+wrapped+" "
            self.key = ""
            
              
        def save_article(self, end_of_entry):

            articles.append(self.article.replace("  "," ").strip())
                    
            self.key = ""
            self.article = ""
            self.baseword = ""
            self.chain = []
            self.in_lang_sources = False

            
    for fn in glob.glob(langletter+"*.htm"):
        print fn
        p = MyParser()
        p.feed(open(fn).read().decode('latin-1'))
        
        #~ soup = BeautifulSoup(open(fn).read())

        #~ p = soup.findAll('p')[1]

        #~ c.key = ""
        #~ c.value = ""
        #~ for child in p:
            #~ process_node(child, c, toplevel = True)
        #~ register_word(c)
        #~ print fn, len(dic)

    return articles    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
pagesize = 40

subdivs_all = {}
    
for langprefix in ["io","en"]:    

    articles = parse_source(langprefix[0])

    re_pureword = re.compile("[a-z]+")

    titles = []


    print langprefix,len(articles)
    for i,a in enumerate(articles):
        ar = a.strip()[3:]
        j = ar.index("<")
        ar = ar[:j].lower()
        mo = re_pureword.search(ar)

        titles.append( (mo.group(), i) )
        
    titles.sort(key=lambda x:x[0])

    sections = []
    prefix_tree = {}

    for title, idx in titles:
        current_node = prefix_tree
        for i in range(6):
            prefix = title[:i+1]
            while len(prefix)<i+1:
                prefix += "_"
            try:
                current_node[prefix]["count"] += 1
            except KeyError:
                current_node[prefix] = {"count":1,"kids":{}}
            current_node = current_node[prefix]["kids"]
        
    c = 0





            
    for li,letter in enumerate(sorted(prefix_tree.keys())):
        cnt = prefix_tree[letter]["count"]
        print langprefix,letter,cnt
        pagesize = 30
        if cnt>1500:
            pagesize = 40
        if cnt>2000:
            pagesize = 50
        pairs = list(process_node(prefix_tree[letter]["kids"]))
        subdivs = [e[0].replace("_","") for e in pairs]
        subdivs_all[langprefix+"_"+letter] = subdivs
        for name in subdivs:
            start_end = name.split("-")
            start = start_end[0]
            end = start_end[1] if len(start_end)>1 else start
            end = end+"zzzzzzzzz"
            sink2 = codecs.open("navigable_dict/%s/%s.html" % (langprefix,name), "wt", "utf-8")
            print >>sink2, """<html>
                <head>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
                <body>"""
            for t,idx in titles:
                if t>=start and t<=end:
                    a = articles[idx]
                    a = a.replace("<k>","<b>").replace("</k>","</b>")
                    a = a.replace("<ex>","<i>").replace("</ex>","</i>")
                    print >>sink2, a+"<br>"
            sink2.close()
        

out = codecs.open("navigable_dict/subdivs.js", "wt", "utf-8")

s = json.dumps(subdivs_all, indent=None, sort_keys=True, ensure_ascii=False)
out.write("subdivs_all="+s)
out.close()
