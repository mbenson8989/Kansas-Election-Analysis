"""Append the addendum to the published pages (commit b31867e copies) and confirm existing bytes are untouched."""
import hashlib, json, os
P='/workspace/kansas-wiki/verification/published_b31867e/'; W='/workspace/kansas-wiki/wikiclone/'; A='/workspace/kansas-wiki/addendum/'
rep={}
for page in ('Home','Reverse-Math','Locked-Kansas-Formula','Floor-and-Ceiling','Graphs'):
    old=open(P+page+'.md','rb').read(); add=open(A+page+'.append.md','rb').read() if os.path.exists(A+page+'.append.md') else b''
    open(W+page+'.md','wb').write(old+add)
    new=open(W+page+'.md','rb').read()
    rep[page]=dict(old_bytes=len(old),new_bytes=len(new),appended_bytes=len(add),old_sha256=hashlib.sha256(old).hexdigest(),
        prefix_sha256=hashlib.sha256(new[:len(old)]).hexdigest(),prefix_identical=new[:len(old)]==old,suffix_is_addendum=new[len(old):]==add)
rep['ALL_OK']=all(v['prefix_identical'] and v['suffix_is_addendum'] for v in rep.values() if isinstance(v,dict))
json.dump(rep,open('/workspace/kansas-wiki/verification/append_diff_check.json','w'),indent=1); print(json.dumps(rep,indent=1))
