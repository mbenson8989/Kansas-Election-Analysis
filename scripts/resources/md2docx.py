import re,sys
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
src,dst=sys.argv[1],sys.argv[2]
lines=open(src).read().split('\n')
doc=Document()
sec=doc.sections[0]; sec.page_width=Inches(8.5); sec.page_height=Inches(11)
for m in ('left_margin','right_margin'): setattr(sec,m,Inches(1))
sec.top_margin=Inches(0.9); sec.bottom_margin=Inches(0.9)
st=doc.styles['Normal']; st.font.name='Times New Roman'; st.font.size=Pt(11.5)
st.paragraph_format.space_after=Pt(6); st.paragraph_format.line_spacing=1.08
# footer page number
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
fp=sec.footer.paragraphs[0]; fp.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=fp.add_run(); 
for t,v in (('begin',None),(None,'PAGE'),('end',None)):
    if t: e=OxmlElement('w:fldChar'); e.set(qn('w:fldCharType'),t)
    else: e=OxmlElement('w:instrText'); e.set(qn('xml:space'),'preserve'); e.text=v
    r._r.append(e)
r.font.size=Pt(9)
def runs(p,text,size=None,italic=False):
    for part in re.split(r'(\*\*[^*]+\*\*|\*[^*]+\*)',text):
        if not part: continue
        if part.startswith('**'): rr=p.add_run(part[2:-2]); rr.bold=True
        elif part.startswith('*') and len(part)>2: rr=p.add_run(part[1:-1]); rr.italic=True
        else: rr=p.add_run(part)
        if size: rr.font.size=Pt(size)
        if italic: rr.italic=True
in_sources=False; block=[]
def flush():
    global block
    if block:
        p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(0) if len(block)>1 else Pt(6)
        for i,l in enumerate(block):
            runs(p,l)
            if i<len(block)-1: p.add_run().add_break()
        p.paragraph_format.space_after=Pt(8)
    block=[]
i=0
while i<len(lines):
    l=lines[i]
    if l.startswith('# '):
        flush(); p=doc.add_paragraph(); rr=p.add_run(l[2:]); rr.bold=True; rr.font.size=Pt(9); rr.font.color.rgb=RGBColor(0xA0,0,0); p.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    elif l.startswith('## '):
        flush(); in_sources = l[3:].strip()=='Sources'
        p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(8); p.paragraph_format.space_after=Pt(4); p.paragraph_format.keep_with_next=True
        rr=p.add_run(l[3:]); rr.bold=True; rr.font.size=Pt(12)
    elif l.strip()=='---':
        flush(); doc.add_page_break() if False else doc.add_paragraph()
    elif re.match(r'^\d+\. ',l):
        flush(); p=doc.add_paragraph(style='List Number' if not in_sources else None)
        if in_sources:
            p.paragraph_format.left_indent=Inches(0.3); p.paragraph_format.first_line_indent=Inches(-0.3); p.paragraph_format.space_after=Pt(2)
            runs(p,l,size=9.5)
        else:
            runs(p,re.sub(r'^\d+\. ','',l))
    elif l.strip()=='':
        flush()
    else:
        block.append(l)
    i+=1
flush()
doc.save(dst)
