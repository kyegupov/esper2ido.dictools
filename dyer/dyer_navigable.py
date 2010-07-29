import json,codecs,re,math,os
from StringIO import StringIO

dictionary = json.load(codecs.open("../../esper2ido/esper2ido/dicts/dyer.json", "rt", "utf-8"))

articles = dictionary["articles"]

re_pureword = re.compile("[a-z]+")

titles = []


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
    for i in range(4):
        prefix = title[:i+1]
        while len(prefix)<i+1:
            prefix += "_"
        try:
            current_node[prefix]["count"] += 1
        except KeyError:
            current_node[prefix] = {"count":1,"kids":{}}
        current_node = current_node[prefix]["kids"]
    
c = 0

pagesize = 70

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
            if sum(weights[i:])<pagesize:
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
                    c+=1
                    yield e
            process_node(node[k]["kids"])
            accum = []
        else:
            accum.append((k,node[k]["count"]))
    if accum:
        for e in distribute(accum):
            c+=1
            yield e
        
try:
    os.mkdir("navigable_dict")
    os.mkdir("navigable_dict/io")
except:
    pass
sink_letters = StringIO()
sink_subdivs = StringIO()

        
for letter in sorted(prefix_tree.keys()):
    c = 0
    print >>sink_letters, """<b>%s</b> """ % letter
    print >>sink_subdivs, """<br> """
    subdivs = list(process_node(prefix_tree[letter]["kids"]))
    
    for entry in subdivs:
        name = entry[0].replace("_","")
        start_end = name.split("-")
        start = start_end[0]
        end = start_end[1] if len(start_end)>1 else start
        end = end+"zzzzzzzzz"
        print >>sink_subdivs, """<a href="io/%s.html">%s</a> """ % (name, name)
        
        sink2 = codecs.open("navigable_dict/io/%s.html" % name, "wt", "utf-8")
        for t,idx in titles:
            if t>=start and t<=end:
                a = articles[idx]
                a = a.replace("<k>","<b>").replace("</k>","</b>")
                a = a.replace("<ex>","<i>").replace("</ex>","</i>")
                print >>sink2, a+"<br>"
        sink2.close()
    print c


out = open("navigable_dict/index_io.html", "wt")
print >>out, sink_letters.getvalue()
print >>out, "<hr>"
print >>out, sink_subdivs.getvalue()

