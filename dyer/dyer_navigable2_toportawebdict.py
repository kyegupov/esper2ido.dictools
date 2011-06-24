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
    shutil.rmtree("navigable_dict/eng-ido")
    shutil.rmtree("navigable_dict/ido-eng")
except OSError:
    pass
os.mkdir("navigable_dict/eng-ido")
os.mkdir("navigable_dict/eng-ido/index")
os.mkdir("navigable_dict/eng-ido/articles")
os.mkdir("navigable_dict/ido-eng")
os.mkdir("navigable_dict/ido-eng/index")
os.mkdir("navigable_dict/ido-eng/articles")
    

class IndexNode(object):
    __slots__ = ["subnodes", "weight"]
    
    def __init__(self):
        self.weight = 0
        self.subnodes = {}
        
class IndexChunkProxy(object):
    __slots__ = ["prefix"]
    
    def __init__(self, prefix):
        self.prefix = prefix
        
class IndexNodesEncoder(json.JSONEncoder):
    def __init__(self, proxyMap, **kw):
        self.proxyMap = proxyMap
        json.JSONEncoder.__init__(self, **kw)
    
    def default(self, obj):
        if isinstance(obj, IndexNode):
            return obj.subnodes
        if isinstance(obj, IndexChunkProxy):
            return self.proxyMap[obj.prefix]
        return json.JSONEncoder.default(self, obj)        

for langprefix in ["ido-eng","eng-ido"]:    

    articles = cPickle.load(open(langprefix+".pickle", "rb"))
    
    import msgpack
    serialized = msgpack.packb(articles)
    print len(serialized)

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

    
    prev = ""
    
    keys = sorted(searchIndex.keys())
    cur = keys.pop(0)
    keys.append("")
    
    def get_char_safe(s, i):
        if i>=len(s): return ""
        return s[i]
    

    # transform search index into trie
    trie = IndexNode()
    
    for nxt in keys:
        curNode = trie
        i = 0
        for i, char in enumerate(cur+" "):
            curNode.weight += 1
            if i>=len(cur) or (get_char_safe(prev, i)!=char and get_char_safe(nxt, i)!=char):
                curNode.subnodes[cur[i:]] = list(searchIndex[cur])
                break
            curNode.subnodes.setdefault(char, IndexNode())
            curNode = curNode.subnodes[char]
        
        prev = cur
        cur = nxt

    print trie.weight
    indexChunkLimit = 1000
    # split index tree into chunks
    # tree dfs
    
    indexChunks = []
    def scan_node(path, node):
        for k,subnode in node.subnodes.iteritems():
            if type(subnode)==list:
                # can't do nothing to leaf nodes
                continue
            if subnode.weight<indexChunkLimit:
                indexChunks.append((path+k, subnode.subnodes, subnode.weight))
                node.subnodes[k]=IndexChunkProxy(path+k)
            else:
                scan_node(path+k, subnode)
    scan_node("", trie)
                
    indexChunkClusters = []
    mapPrefixToCluster = {}
    indexChunks.sort(key=lambda x:x[2])
    
    curCluster = []
    curClusterWeight = 0
    for prefix, subtree, weight in indexChunks:
        if curClusterWeight+weight>indexChunkLimit:
            indexChunkClusters.append(curCluster)
            curCluster = []
            curClusterWeight = 0
        curCluster.append((prefix, subtree))
        curClusterWeight += weight
        mapPrefixToCluster[prefix] = len(indexChunkClusters)
    indexChunkClusters.append(curCluster)
    
    

    for i,cluster in enumerate(indexChunkClusters):
        out = codecs.open("navigable_dict/%s/index/%04d.js" % (langprefix, i), "wt", "utf-8")
        for prefix, subtree in cluster:
            s = json.dumps(subtree, indent=None, sort_keys=True, ensure_ascii=False, cls=IndexNodesEncoder, separators=(',', ':'), proxyMap=None)
            prefix_path = ["["+json.dumps(c)+"]" for c in prefix]
            out.write("dictionaries[%s].index%s = " % (json.dumps(langprefix), "".join(prefix_path)))
            out.write(s)
            out.write("\n")
        out.close()    


    
    out = codecs.open("navigable_dict/%s/indexRoot.js" % langprefix, "wt", "utf-8")
    s = json.dumps(trie, indent=None, sort_keys=True, ensure_ascii=False, cls=IndexNodesEncoder, separators=(',', ':'), proxyMap=mapPrefixToCluster)
    out.write("if (!window.hasOwnProperty('dictionaries')) dictionaries = {};\n")
    out.write("dictionaries[%s] = {articleChunks:{},indexChunks:{}};\n" % json.dumps(langprefix))
    out.write("dictionaries[%s].index = " % json.dumps(langprefix))
    out.write(s)
    out.close()    
            
    # split articles into chunks
    for chunkStart in xrange(0, len(articles), 200):
        out = codecs.open("navigable_dict/%s/articles/%04d.js" % (langprefix, chunkStart/200), "wt", "utf-8")
        chunk = [a[0] for a in articles[chunkStart:chunkStart+200]]
        s = json.dumps(chunk, indent=None, sort_keys=True, ensure_ascii=False)
        out.write("dictionaries[%s].articleChunks[%s] = " % (json.dumps(langprefix), chunkStart//200))
        out.write(s)
        out.close()        
        





