# coding: utf-8

import json,codecs,re,math,os, shutil
from StringIO import StringIO
import glob
from HTMLParser import HTMLParser 
from htmlentitydefs import name2codepoint

import cPickle 

try:
    os.mkdir("navigable_dict")
except:
    pass

shutil.rmtree("navigable_dict/en")
shutil.rmtree("navigable_dict/io")
os.mkdir("navigable_dict/en")
os.mkdir("navigable_dict/io")
    
    
pagesize = 300

subdivs_all = {}
wordlist_all = {}

for langprefix in ["io","en"]:    

    articles = cPickle.load(open(langprefix+".pickle", "rb"))

    re_pureword = re.compile(u"^[a-z]+$")

    re_decorators = re.compile(ur"[\*() «»:;!\.\"\…=›‹\-“”\’]+")

    titles = []

    print langprefix,len(articles)
    for i,a in enumerate(articles):
        ar = a.strip()[3:]
        j = ar.find("<")
        
        ar = ar[:j].lower()
        cleaned = re_decorators.sub("", ar).replace(u"é", "e").replace(u"è","e").replace(u"ç","c").replace(u"à","a").replace(u"œ","oe").replace(u"æ","ae").replace(u"ô", "o").replace(u"ê", "e")
        if re_pureword.match(cleaned)==None:
            print cleaned
            raise hell2

        titles.append( (cleaned, a) )
        
    titles.sort(key=lambda x:x[0])

    sections = []
    prefix_tree = {}
    
    prefixes = {"":titles}

    for prefixlimit in range(1,4):
        key_list = prefixes.keys()
        for prefix0 in key_list:
            data = prefixes[prefix0]
            if len(data)>pagesize:
                for title, a in data:
                    prefix = title[:prefixlimit]
                    while len(prefix)< prefixlimit:
                        prefix += "_"
                    prefixes.setdefault(prefix, [])
                    prefixes[prefix].append((title, a))
                del prefixes[prefix0]
                
            
    for name in sorted(prefixes.keys()):
        start_end = name.split("-")
        start = start_end[0]
        end = start_end[1] if len(start_end)>1 else start
        end = end+"zzzzzzzzz"
        sink2 = codecs.open("navigable_dict/%s/%s.html" % (langprefix,name), "wt", "utf-8")
        print >>sink2, """<html>
            <head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
            </head>
            <body>"""
        count = 0
        for t,a in prefixes[name]:
            count += 1
            a = a.replace("<k>","<b>").replace("</k>","</b>")
            a = a.replace("<ex>","<i>").replace("</ex>","</i>")
            print >>sink2, ("<a name=\"%s\"/>" % t)+a+"<br>"
        print name, count
        sink2.close()
        
    subdivs_all[langprefix] = sorted(prefixes.keys())
    allwords = list(set(t[0] for t in titles))
    allwords.sort()
    wordlist_all[langprefix] = allwords
        

out = codecs.open("navigable_dict/subdivs.js", "wt", "utf-8")
s = json.dumps(subdivs_all, indent=None, sort_keys=True, ensure_ascii=False)
out.write("subdivs_all="+s)
out.close()

out = codecs.open("navigable_dict/wordlist.js", "wt", "utf-8")
s = json.dumps(wordlist_all, indent=None, sort_keys=True, ensure_ascii=False)
out.write("wordlist_all="+s)
out.close()

