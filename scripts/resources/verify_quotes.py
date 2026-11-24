"""Check every quotation in the AG letter and the clerk-letter template against the official source text, word for word (whitespace, quote style and soft hyphens normalized)."""
import re,html,glob,json,sys
def norm(s):
    s=html.unescape(s).replace('\u00ad','').replace('­','')
    for a,b in [('’',"'"),('‘',"'"),('“','"'),('”','"'),('\xa0',' ')]: s=s.replace(a,b)
    return re.sub(r'\s+',' ',s).strip()
def strip_html(p):
    s=open(p,errors='ignore').read(); s=re.sub(r'<(script|style)[^>]*>.*?</\1>',' ',s,flags=re.S); return norm(re.sub(r'<[^>]+>',' ',s))
R='/workspace/kansas-resources/raw/'
src={}
for f in glob.glob(R+'statutes/sec/*.txt'): src['K.S.A. '+f.split('/')[-1][:-4]]=norm(open(f).read())
src['EO 14399']=norm(open(R+'federal/eo14399.txt').read()).replace('- ','')
src['AG Op. 2025-25']=norm(open(R+'ag/2025-025.txt').read())
src['LPA Feb 2023']=strip_html(R+'lpa/review.html')
src['U.S. Const.']=strip_html(R+'federal/constitution.html')
allsrc=' || '.join(src.values())
def check(path):
    t=norm(open(path).read()); res=[]
    for q in [q for q in re.findall(r'"([^"]*)"',t) if len(q)>=8]:
        qq=re.sub(r'\[(.)\]',r'\1',q).strip(' ,.')
        parts=[p.strip(' ,.') for p in re.split(r'\s*(?:…|\.\.\.)\s*',qq) if p.strip()]
        hits=[k for k,v in src.items() if all(p in v or p.lower() in v.lower() and p[0].isupper() and p[1:] in v for p in parts)]
        # bracketed capitalization like [t]he / [a]ll: compare case-insensitively on first char
        if not hits:
            hits=[k for k,v in src.items() if all(p[1:] in v for p in parts)]
            hits=[h+' (first letter case adjusted)' for h in hits]
        res.append(dict(quote=q,found_in=hits))
    return res
out={}
for p in sys.argv[1:]:
    r=check(p); out[p]=r
    bad=[x for x in r if not x['found_in']]
    print(p.split('/')[-1], 'quotes:',len(r),'not found:',len(bad))
    for x in bad: print('   MISSING:',x['quote'][:120])
json.dump(out,open('/workspace/kansas-resources/out/quote_check.json','w'),indent=1)
