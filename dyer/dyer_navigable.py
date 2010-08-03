import json,codecs,re,math,os
from StringIO import StringIO

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
    
    
pagesize = 40
letters_in_row = 9
subdivs_in_row = 2
sink_letters = StringIO() 
        

letters = [chr(x) for x in range(ord('a'),ord('z')+1)]
for li,letter in enumerate(letters):
    print >>sink_letters, """<td>%s</td> """ % letter.upper(),
    if li%letters_in_row == letters_in_row-1:
        print >>sink_letters, """</tr><tr>"""  

subdivs_all = {}
    
for langprefix in ["io","en"]:    
    dictionary = json.load(codecs.open("dyer_%s.json" % langprefix, "rt", "utf-8"))

    articles = dictionary["articles"]

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
