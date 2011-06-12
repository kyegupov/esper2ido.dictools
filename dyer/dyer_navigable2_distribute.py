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
searchIndex_all = {}

for langprefix in ["io","en"]:    

    articles = cPickle.load(open(langprefix+".pickle", "rb"))

    re_pureword = re.compile(u"^[a-z]+$")

    re_decorators = re.compile(ur"[\*() «»:;!\.\"\…=›‹\-“”\’]+")

    titles = []

    print langprefix,len(articles)
    
    articles.sort(key = lambda x:x[1][0])
    searchIndex = {}
    for i,a in enumerate(articles):
        article, keywords = a
        for k in keywords:
            searchIndex.setdefault(k, set())
            searchIndex[k].add(i)

    trie = {}
    prev = ""
    
    keys = sorted(searchIndex.keys())
    cur = keys.pop(0)
    keys.append("")
    
    def get_char_safe(s, i):
        if i>=len(s): return ""
        return s[i]
    
    count = 0
    for nxt in keys:
        curNode = trie
        i = 0
        for i, char in enumerate(cur+" "):
            if i>=len(cur) or (get_char_safe(prev, i)!=char and get_char_safe(nxt, i)!=char):
                curNode[cur[i:]] = list(searchIndex[cur])
                break
            curNode.setdefault(char, {})
            curNode = curNode[char]
        
        prev = cur
        cur = nxt
            

    searchIndex_all[langprefix] = trie
        
    for chunkStart in xrange(0, len(articles), 100):
        out = codecs.open("navigable_dict/%s/%04d.js" % (langprefix, chunkStart/100), "wt", "utf-8")
        chunk = [a[0] for a in articles[chunkStart:chunkStart+100]]
        s = json.dumps(chunk, indent=None, sort_keys=True, ensure_ascii=False)
        out.write(("articleChunks.%s[%s]=" % (langprefix, chunkStart//100))+s)
        out.close()        
        



out = codecs.open("navigable_dict/searchIndex.js", "wt", "utf-8")
s = json.dumps(searchIndex_all, indent=None, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
out.write("searchIndex_all="+s)
out.close()

