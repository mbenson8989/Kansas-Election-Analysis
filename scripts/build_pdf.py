"""Build the Kansas 105-county PDF from the pass B rows (asserted identical to pass A)."""
import json
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, LongTable, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import glob
V='/workspace/kansas-wiki/verification/'
assert json.load(open(V+'pdf_compare_report.json'))['CLEAN']
rows=json.load(open(V+'pdfB_rows.json'))
def font(names):
    for n in names:
        g=glob.glob(f'/usr/share/fonts/**/{n}',recursive=True)
        if g: return g[0]
reg=font(['DejaVuSans.ttf','LiberationSans-Regular.ttf']); bold=font(['DejaVuSans-Bold.ttf','LiberationSans-Bold.ttf'])
pdfmetrics.registerFont(TTFont('F',reg)); pdfmetrics.registerFont(TTFont('FB',bold))
OUT='/workspace/kansas-wiki/pdf/Kansas_105_County_Democratic_Registration_and_Vote_Change.pdf'
H=ParagraphStyle('h',fontName='FB',fontSize=6.3,leading=7.4,alignment=1,textColor=colors.white)
T=ParagraphStyle('t',fontName='FB',fontSize=12.5,leading=15)
N=ParagraphStyle('n',fontName='F',fontSize=7,leading=8.8)
hdr=['County','Population (Jul&nbsp;1, 2025)','Dem Reg Share 2026 %','Dem Reg 2022 (Nov&nbsp;1)','Dem Reg 2026 (Oct&nbsp;1)','Reg Change #','Reg Change %',
     'Dem Gov Votes 2022','Dem Gov Votes 2026*','Vote Change #','Vote Change % (on 2022 base)',
     'Total Gov Votes† 2022','Total Gov Votes† 2026*','Total Gov Vote Change #','Total Gov Vote Change %']
W=[70,50,44]+[47]*12
data=[[Paragraph(h,H) for h in hdr]]+rows
up=[i for i,r in enumerate(rows,1) if r[5].startswith('+') and r[0]!='Statewide total']
down=[i for i,r in enumerate(rows,1) if r[9].startswith('-') and r[0]!='Statewide total']
st=[('FONT',(0,1),(-1,-1),'F',6.8),('ALIGN',(1,1),(-1,-1),'RIGHT'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
    ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1f3864')),('GRID',(0,0),(-1,-1),0.25,colors.HexColor('#b4b4b4')),
    ('TOPPADDING',(0,1),(-1,-1),1.3),('BOTTOMPADDING',(0,1),(-1,-1),1.3),('LEFTPADDING',(0,0),(-1,-1),2.5),('RIGHTPADDING',(0,0),(-1,-1),2.5),
    ('FONT',(0,len(data)-1),(-1,len(data)-1),'FB',6.8),('BACKGROUND',(0,len(data)-1),(-1,len(data)-1),colors.HexColor('#e7e6e6')),('LINEABOVE',(0,len(data)-1),(-1,len(data)-1),1,colors.black)]
for i in up: st.append(('BACKGROUND',(0,i),(-1,i),colors.HexColor('#ddebf7')))
for i in down: st.append(('TEXTCOLOR',(9,i),(10,i),colors.HexColor('#c00000')))
tbl=LongTable(data,colWidths=W,repeatRows=1); tbl.setStyle(TableStyle(st))
upn=', '.join(rows[i-1][0] for i in up); dnn=', '.join(rows[i-1][0] for i in down) or 'none'
legend=LongTable([[ 'Legend:', f'Democratic registration rose ({len(up)}): {upn}', f'Democratic governor votes fell ({len(down)}): {dnn}']],colWidths=[40,420,260])
legend.setStyle(TableStyle([('FONT',(0,0),(-1,-1),'F',6.3),('FONT',(0,0),(0,0),'FB',6.5),('BACKGROUND',(1,0),(1,0),colors.HexColor('#ddebf7')),('BACKGROUND',(2,0),(2,0),colors.HexColor('#fce4d6')),('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
legend._argW[1]=420
# wrap legend text
legend=LongTable([[Paragraph('<b>Legend:</b>',N),Paragraph(f'Democratic registration rose ({len(up)}): {upn}',N),Paragraph(f'<font color="#c00000">Red vote change</font>: Democratic governor votes fell ({len(down)} counties)',N)]],colWidths=[48,462,210])
legend.setStyle(TableStyle([('BACKGROUND',(1,0),(1,0),colors.HexColor('#ddebf7')),('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
story=[Paragraph('Kansas 105 Counties — Democratic Registration, Democratic Governor Votes and Total Governor Votes, 2022 vs 2026*',T),Spacer(1,3),
 Paragraph('Sorted by 2026 Democratic share of registration (Democratic registered voters ÷ all registered voters, active + inactive, Kansas SOS report of Oct 1, 2026), highest first. Douglas leads by share; Johnson leads by raw Democratic registration. Statewide totals are the last row.',N),Spacer(1,2),
 Paragraph('*2026 votes are UNOFFICIAL: Kansas Secretary of State (SOS) election-night results, ent.sos.ks.gov, county pages last updated 11/08/2026 9:15 PM (all 4,168 precincts reporting); the State Board of Canvassers certifies Dec 1, 2026. 2022 votes: SOS official 2022 general election results. Votes are votes for the Democratic governor candidate (Kelly 2022, Holscher 2026), not a count of registered Democrats who voted.',N),Spacer(1,2),
 Paragraph('†<b>Total governor votes, all candidates — not total ballots.</b> Nebraska\'s 93-county PDF uses total ballots. Kansas uses total governor votes in both years under its locked method, because the SOS 2022 ballots-cast file is unusable in six counties (Stevens, Sumner, Washington, Wilson, Rice, Montgomery) and 2026 ballots cast by county are not posted. 2022 had four governor candidates (Kelly, Schmidt, Pyle, Cordell); 2026 had two.',N),Spacer(1,4),
 legend,Spacer(1,5),tbl,Spacer(1,6),
 Paragraph('<b>Sources.</b> Kansas Secretary of State: 2022 general election official results (governor, by county); 2026 general election unofficial results by county (ent.sos.ks.gov, last updated 11/08/2026 9:15 PM, re-downloaded 11/19/2026); voter registration by county and party, Nov 1, 2022 and Oct 1, 2026 (sos.ks.gov voter registration statistics; the Nov 2026 report is not posted). Population: U.S. Census Bureau Vintage 2025 county estimates (July 1, 2025), shown for size only. Change % = (2026 − 2022) ÷ 2022 × 100. Every figure was computed twice by independent programs from the raw SOS files with 0 mismatches. Data, scripts and verification: github.com/mbenson8989/Kansas-Election-Analysis. Compiled Nov 19, 2026. This table measures a pattern; it makes no claim about intent, fraud or cause.',N)]
class Doc(BaseDocTemplate):
    def afterFlowable(self,f): pass
def foot(c,d):
    c.saveState(); c.setFont('F',7); c.drawString(0.5*inch,0.32*inch,'*2026 figures unofficial (Kansas SOS election night, 11/08/2026); certification Dec 1, 2026.  †Total governor votes, all candidates (not ballots cast).')
    c.drawRightString(10.5*inch,0.32*inch,f'Page {d.page} of {d._total}'); c.restoreState()
def build(total):
    d=Doc(OUT,pagesize=landscape(letter),leftMargin=0.5*inch,rightMargin=0.5*inch,topMargin=0.45*inch,bottomMargin=0.5*inch,title='Kansas 105 County Democratic Registration and Vote Change, 2022 vs 2026*',author='mbenson8989 / Kansas-Election-Analysis')
    d._total=total; fr=Frame(d.leftMargin,d.bottomMargin,d.width,d.height,id='f')
    d.addPageTemplates([PageTemplate('p',[fr],onPage=foot)]); d.build(list(story)); return d.page
n=build(0); n2=build(n); assert n==n2; print(OUT,'pages',n,'reg rose',len(up),'votes fell',len(down))
