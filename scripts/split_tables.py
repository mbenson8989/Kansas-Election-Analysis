"""Split the two wide 105-county tables on Reverse-Math into two narrower tables each. Cell text is copied verbatim; only County and Population repeat."""
W='/workspace/kansas-wiki/wikiclone/Reverse-Math.md'
L=open(W).read().split('\n')
def find(header_start):
    best=None
    for i in [k for k,l in enumerate(L) if l.startswith(header_start)]:
        j=i
        while j<len(L) and L[j].startswith('|'): j+=1
        if best is None or j-i>best[1]-best[0]: best=(i,j)
    assert best[1]-best[0]==107, best
    return best
def cells(l): return [x.strip() for x in l.strip().strip('|').split('|')]
def table(rows,idx): return ['| '+' | '.join(r[k] for k in idx)+' |' for r in rows]
def build(i,j,parts):
    rows=[cells(l) for l in L[i:j]]; n=len(rows[0]); assert all(len(r)==n for r in rows)
    out=[]
    for label,idx in parts:
        out+=[label,'']+table([rows[0]],idx)+['|'+'---|'*len(idx)]+table(rows[2:],idx)+['']
    used=sorted({k for _,idx in parts for k in idx}); assert used==list(range(n)),used
    return out[:-1]
# second table first (later in file) so indices stay valid
i,j=find('| County | Population | Dem reg 2022 → 2026 |')
L[i:j]=build(i,j,[('**Part A: registration and the expected loss.** Same 105 counties, same order.',[0,1,2,3,4]),
                 ('**Part B: residual and backward-solved votes.** Residual = ΔG − expected loss (Part A). Same 105 counties, same order.',[0,1,5,6,7,8,9])])
i,j=find('| County | Population | Dem gov votes 2022 |')
L[i:j]=build(i,j,[('**Part A: 2022 (official).** Votes, registration and G.',[0,1,2,3,4,5,6]),
                 ('**Part B: 2026\\* (unofficial) and the change.** Votes, registration, G and ΔG = G 2026 − G 2022 (Part A). Same 105 counties, same order.',[0,1,7,8,9,10,11,12])])
open(W,'w').write('\n'.join(L))
