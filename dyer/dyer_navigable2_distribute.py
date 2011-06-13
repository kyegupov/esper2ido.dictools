# coding: utf-8

import json,codecs,re,math,os, shutil, pprint
from StringIO import StringIO
import glob
from HTMLParser import HTMLParser 
from htmlentitydefs import name2codepoint

import cPickle 

try:
    os.mkdir("navigable_dict")
except:
    pass

try:
    shutil.rmtree("navigable_dict/en")
    shutil.rmtree("navigable_dict/io")
except OSError:
    pass
os.mkdir("navigable_dict/en")
os.mkdir("navigable_dict/en/index")
os.mkdir("navigable_dict/en/articles")
os.mkdir("navigable_dict/io")
os.mkdir("navigable_dict/io/index")
os.mkdir("navigable_dict/io/articles")
    
    
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
    debugIndex = {}
    for i,a in enumerate(articles):
        article, keywords = a
        for k in keywords:
            searchIndex.setdefault(k, set())
            searchIndex[k].add(i)
        for k in keywords[1:]:
            debugIndex.setdefault(k, [])
            debugIndex[k].append(keywords[0])

    out = codecs.open("navigable_dict/debugIndex_%s.json" % langprefix, "wt", "utf-8")
    s = json.dumps(debugIndex, indent=4, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    out.write(s)

    trie = {}
    prev = ""
    
    keys = sorted(searchIndex.keys())
    cur = keys.pop(0)
    keys.append("")
    
    def get_char_safe(s, i):
        if i>=len(s): return ""
        return s[i]
    

    # transform search index into trie
    indexChunks = {}
    for nxt in keys:
        curNode = trie
        i = 0
        for i, char in enumerate(cur+" "):
            if i>=len(cur) or (get_char_safe(prev, i)!=char and get_char_safe(nxt, i)!=char):
                curNode[cur[i:]] = list(searchIndex[cur])
                break
            if i==1:
                curNode.setdefault(char, "ext")
                chunkId = cur[:2]
                indexChunks.setdefault(chunkId, {})
                curNode = indexChunks[chunkId]
            else:
                curNode.setdefault(char, {})
                curNode = curNode[char]
        
        prev = cur
        cur = nxt
    

    for prefix,tree in indexChunks.iteritems():
        out = codecs.open("navigable_dict/%s/index/%s.js" % (langprefix, prefix), "wt", "utf-8")
        s = json.dumps(tree, indent=None, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
        prefix_path = ["["+json.dumps(c)+"]" for c in prefix]
        out.write("dictionaries.%s.index%s = " % (langprefix, "".join(prefix_path)))
        out.write(s)
        out.close()    


    
    out = codecs.open("navigable_dict/%s/indexRoot.js" % langprefix, "wt", "utf-8")
    s = json.dumps(trie, indent=None, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    out.write("if (!window.hasOwnProperty('dictionaries')) dictionaries = {};\n")
    out.write("dictionaries.%s = {articleChunks:{},indexChunks:{}};\n" % langprefix)
    out.write("dictionaries.%s.index = " % langprefix)
    out.write(s)
    out.close()    
            
    # split articles into chunks
    for chunkStart in xrange(0, len(articles), 200):
        out = codecs.open("navigable_dict/%s/articles/%04d.js" % (langprefix, chunkStart/200), "wt", "utf-8")
        chunk = [a[0] for a in articles[chunkStart:chunkStart+200]]
        s = json.dumps(chunk, indent=None, sort_keys=True, ensure_ascii=False)
        out.write("dictionaries.%s.articleChunks[%s] = " % (langprefix, chunkStart//200))
        out.write(s)
        out.close()        
        





