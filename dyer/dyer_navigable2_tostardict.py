# coding: utf-8

import json,codecs,re,math,os, shutil, pprint
import struct

import cPickle 

for langprefix in ["ido-eng","eng-ido"]:    


    articles = cPickle.load(open(langprefix+".pickle", "rb"))
    
    fname = langprefix + "_dyer"
    try:
        os.makedirs("stardict/"+fname)
    except OSError:
        pass
    
    outDict = open("stardict/"+fname+"/"+fname+".dict", "wb")
    
    mapArticleToOffset = []
    searchIndex = {}

    for i,a in enumerate(articles):
        article, keywords = a
        offset = outDict.tell()
        outDict.write(article.encode('utf-8'))
        outDict.write("\0")
        size = outDict.tell()-offset
        for k in keywords:
            searchIndex.setdefault(k, [])
            searchIndex[k].append((offset, size))
        
    outDictLen = outDict.tell()
    outDict.close()
    
    keys = sorted(searchIndex.keys())
    outIdx = open("stardict/"+fname+"/"+fname+".idx", "wb")
    
    for key in keys:
        for offset, size in searchIndex[key]:
            outIdx.write(key.encode('utf-8'))
            outIdx.write("\0")
            outIdx.write(struct.pack("!II", offset, size))
    outIdxLen = outIdx.tell()
    outIdx.close()
            
    outIfo = open("stardict/"+fname+"/"+fname+".ifo", "wb")
    outIfo.write("""StarDict's dict ifo file
version=3.0.0
[options]
bookname=%s
wordcount=%d
idxfilesize=%d
idxoffsetbits=32
sametypesequence=g
""" % (langprefix+" Dyer dictionary", len(articles), outIdxLen));
    outIfo.close()
