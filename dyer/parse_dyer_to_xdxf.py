# coding: utf-8

import json, glob, re
from html.parser import HTMLParser 
from html.entities import name2codepoint
from pprint import pprint


articles = []

re_w = re.compile("[a-zA-Z]*-?[a-zA-Z]+")

S_EXPECT_WORD = 0
S_READING_WORD = 1
S_READING_DEF = 3

strong = ["b","strong"]
em = ["i","em"]

subst_file = open("substitiution_corrections_en.txt","rt")
subst_map = {}
for line in subst_file:
    base, suffix, replacement = line.strip().split(" ",2)
    subst_map[(base,suffix)] = replacement
    
subst_unused = set(subst_map.keys())

langcode = "en"

if langcode == "io":
    preps = [
        "a",
        "ad",
        "adsur",
        "ante",
        "avan",
        "de",
        "di",
        "dop",
        "dum",
        "ek",
        "en",
        "for",
        "infre",
        "inter",
        "koram",
        "kun",
        "per",
        "por",
        "pos",
        "pro",
        "sub",
        "sur",
        "vers",
        "vice",
        "ye",
        "yen",
        "olim",
        "apud",
        "proxim"
    ]

    conjs = ["o", "od", "e", "ed", "ma"]

    nums = ["zero", "un", "du", "tri", "quar", "kin", "sis", "sep", "ok", "non", "dek", "cent", "mil"]

    pronouns = ["me", "tu", "vu", "ilu", "elu", "olu", "lu", "ni", "vi", "ili", "eli", "oli", "li", "onu"]
else:
    preps = """aboard
about
above
absent
across
after
against
along
alongside
amid
amidst
among
amongst
around
as
aside
astride
at
athwart
atop
barring
before
behind
below
beneath
beside
besides
between
betwixt
beyond
but
by
circa
concerning
despite
down
during
except
excluding
failing
following
for
from
given
in
including
inside
into
like
mid
midst
minus
near
next
notwithstanding
of
off
on
onto
opposite
out
outside
over
pace
past
per
plus
pro
qua
regarding
round
save
since
than
through
thru
throughout
thruout
till
times
to
toward
towards
under
underneath
unlike
until
up
upon
versus
via
with
within
without
worth""".splitlines()
    nums = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "hundred", "thousand"]
    
    conjs = ["or", "and",  "but", "so"]
    
    pronouns = "I me myself mine my we us ourselves ourself ours our you you yourself yours your he him himself his his she her herself hers her it it itself its its they them themselves theirs their".split(" ")

skippable = set(preps + conjs + nums + pronouns)

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
                self.chain.append("i")
                self.article += "<i>"
                    
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
                assert self.chain.pop() == "i"
                self.article += "</i>"
                

    
    def handle_data(self, data):
        if self.state == 2:
            if self.in_lang_sources:
                return
            if chr(8212) in data:
                data = data.split(chr(8212))[0].rstrip()        
                self.in_lang_sources = True
            if self.in_key:
                self.key += data
            else:
                self.article += data
    
    def handle_charref(self, name):
        cpoint = int(name)
        if cpoint>255:
            self.handle_data(chr(cpoint))
        else:
            self.handle_data(bytes([cpoint]).decode("cp1252"))

    def handle_entityref(self, name):
        self.handle_data(chr(name2codepoint[name]))

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
        is_baseword = False
        self.key = self.key.replace("\n"," ").strip()
        if self.key.endswith(":"):
            sc = True
            self.key = self.key[:-1]
        else :
            sc = False
        keys = []
        multiforms = False
        if self.key.find(", -")>=0:
            multiforms = True
        if "(" in self.key:
            print(self.key)
        for k in self.key.split(","):
            words = k.strip().split(" ")
            if self.baseword=="" and len(words)==1:
                is_baseword = True
                if multiforms or langcode=="io":
                    self.baseword = words[0].rsplit("-",1)[0].rstrip(":")
                else:
                    self.baseword = words[0].rstrip(":")
                    #~ if ("-" in self.baseword) or ("," in self.baseword):
                        #~ print self.baseword.encode('cp850','replace')
            words2 = []

            for w in words:
                if w.startswith("-") and self.baseword!="":
                    if self.baseword.endswith("e"):
                        if self.baseword[-2]==w[1]:
                            w2 = self.baseword[:-1]+w[2:].replace("-","")
                        elif w[1:] in "ed er ery al ing ity en ist ism ation".split():
                            w2 = self.baseword[:-1]+w[1:].replace("-","")
                        else:
                            w2 = self.baseword+w[1:].replace("-","")
                    elif self.baseword.endswith("y") and w.startswith("-i"):
                        w2 = self.baseword[:-1]+w[1:].replace("-","")
                    else:
                        w2 = self.baseword+w[1:].replace("-","")
                    pair = (self.baseword, w)
                    if pair in subst_map:
                        w2 = subst_map[pair]
                        subst_unused.discard(pair)
                else:
                    w2 = w.replace("-","")
                    if (w in skippable) or (len(w)>0 and w[-1]=="s" and w[:-1] in nums) or (len(w)==2 and w.endswith(".")):
                        pass
                        #~ w2 = "<nu>"+w2+"</nu>"
                words2.append(w2)
            keys.append(" ".join(words2))
        
        
        tagmode = "k" if is_baseword else "ex"
        wrapped = ", ".join(["<{0}>".format(tagmode)+key.strip()+"</{0}>".format(tagmode) for key in keys])
        self.article += " "+wrapped
        if sc and not is_baseword:
            self.article += ":"
        self.article += " "
        self.key = ""
        
          
    def save_article(self, end_of_entry):

        articles.append(self.article.replace("  "," ").strip())
                
        self.key = ""
        self.article = ""
        self.baseword = ""
        self.chain = []
        self.in_lang_sources = False

        
sink = open("out.xml","wt",encoding="utf-8")
print("""<xdxf lang_from="io" lang_to="en" format="l">""", file=sink)


for fn in glob.glob("e*.htm"):
    print(fn)
    p = MyParser()
    p.feed(open(fn, encoding='latin-1').read())
    
    #~ soup = BeautifulSoup(open(fn).read())

    #~ p = soup.findAll('p')[1]

    #~ c.key = ""
    #~ c.value = ""
    #~ for child in p:
        #~ process_node(child, c, toplevel = True)
    #~ register_word(c)
    #~ print fn, len(dic)


for a in articles:
    print("<ar>"+a.replace("&","&amp;")+"</ar>", file=sink)
    
print("</xdxf>", file=sink)

pprint(subst_unused)
