import json,csv
from PIL import Image, ImageDraw, ImageFont
OUT='/workspace/kansas-wiki/repo/resources/'
import os; os.makedirs(OUT,exist_ok=True)
FB='/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
f=lambda s:ImageFont.truetype(FB,s)
BLUE=(0,66,130); NAVY=(10,30,60); GRAY=(95,95,95); BLK=(0,0,0); WHT=(255,255,255); RED=(190,10,30); GOLD=(255,214,102)
A=json.load(open('pass1.json'))
cand={c:v for c,v in A.items() if v['reg26']<v['reg22'] and v['v26']>v['v22']}
top=sorted(cand,key=lambda c:-cand[c]['gap'])[:10]
n=lambda x:f'{int(x):,}'
def ctext(d,y,t,font,fill,W=1080):
    d.text(((W-d.textlength(t,font=font))/2,y),t,font=font,fill=fill)
def fit(d,t,size,mw):
    while d.textlength(t,font=f(size))>mw: size-=2
    return f(size)
def arrow(d,cx,top_,h,w,up,col):
    sw=w*0.42; hh=h*0.42
    pts=[(cx,top_),(cx+w/2,top_+hh),(cx+sw/2,top_+hh),(cx+sw/2,top_+h),(cx-sw/2,top_+h),(cx-sw/2,top_+hh),(cx-w/2,top_+hh)] if up else [(cx,top_+h),(cx+w/2,top_+h-hh),(cx+sw/2,top_+h-hh),(cx+sw/2,top_),(cx-sw/2,top_),(cx-sw/2,top_+h-hh),(cx-w/2,top_+h-hh)]
    d.polygon(pts,fill=col,outline=BLK,width=4)
man=[];rows=[]
for i,c in enumerate(top,1):
    v=A[c]; g=round(v['gap']); pct=100*v['gap']/v['tot26']; rd=v['reg26']-v['reg22']; vd=v['v26']-v['v22']; vp=100*vd/v['v22']
    rows.append(dict(rank=i,county=c,pop=v['pop'],reg22=v['reg22'],reg26=v['reg26'],reg_change=rd,v22=v['v22'],v26=v['v26'],v_change=vd,v_pct=round(vp,1),flip=g,pct_of_race=round(pct,1),tot26=v['tot26']))
    im=Image.new('RGB',(1080,1350),WHT); d=ImageDraw.Draw(im)
    d.rectangle([0,0,1080,210],fill=NAVY)
    ctext(d,28,f'#{i} OF 105 KANSAS COUNTIES',f(34),GOLD)
    t=c.upper()+' COUNTY'; ctext(d,78,t,fit(d,t,100,1000),WHT)
    arrow(d,130,270,170,130,False,GRAY)
    d.text((240,262),'REGISTERED DEMOCRATS',font=f(40),fill=BLK)
    t=f'{n(v["reg22"])} \u2192 {n(v["reg26"])}'; d.text((240,312),t,font=fit(d,t,84,800),fill=BLK)
    d.text((240,408),f'\u2212{n(-rd)}  (2022 \u2192 2026)',font=f(44),fill=GRAY)
    arrow(d,130,540,220,150,True,BLUE)
    d.text((240,540),'DEMOCRATIC VOTES',font=f(40),fill=BLUE); d.text((240,585),'FOR GOVERNOR',font=f(40),fill=BLUE)
    t=f'{n(v["v22"])} \u2192 {n(v["v26"])}*'; d.text((240,640),t,font=fit(d,t,84,800),fill=BLUE)
    d.text((240,738),f'+{n(vd)}*  (+{vp:.0f}%*)',font=f(48),fill=BLUE)
    d.rectangle([0,860,1080,1150],fill=BLUE)
    ctext(d,885,'VOTES BEYOND WHAT REGISTRATION EXPLAINS',f(40),WHT)
    ctext(d,945,f'+{n(g)}*',f(150),WHT)
    ctext(d,1170,f'That is {pct:.1f}% of the 2026* governor race.',f(36),BLK)
    ctext(d,1235,'Fewer Democrats registered. More Democratic votes.',f(34),BLK)
    ctext(d,1285,'Source: Kansas Secretary of State. *2026 UNOFFICIAL (SOS 11/08/2026; certification Dec 1).',f(22),GRAY)
    ctext(d,1318,'A pattern in the numbers, not a finding about cause.',f(22),GRAY)
    im.save(OUT+f'KS_Flip_{i:02d}_{c.replace(" ","_")}.png')
    man.append(dict(file=f'KS_Flip_{i:02d}_{c.replace(" ","_")}.png',strings=[c.upper()+' COUNTY',n(v['reg22']),n(v['reg26']),n(-rd),n(v['v22']),n(v['v26']),n(vd),f'{vp:.0f}',n(g),f'{pct:.1f}']))
# summary
im=Image.new('RGB',(1080,1350),WHT); d=ImageDraw.Draw(im)
d.rectangle([0,0,1080,200],fill=NAVY)
ctext(d,30,'TEN KANSAS COUNTIES',f(64),WHT); ctext(d,115,'Fewer Democrats registered. More Democratic votes.',f(36),GOLD)
ctext(d,225,'Votes beyond what registration explains, 2022 \u2192 2026*',f(34),BLK)
mx=rows[0]['flip']; y=290
for r in rows:
    d.text((40,y+8),f'{r["rank"]}. {r["county"]}',font=f(36),fill=BLK)
    L=int(480*r['flip']/mx); d.rectangle([370,y,370+max(L,6),y+56],fill=BLUE)
    d.text((370+max(L,6)+14,y+8),f'+{r["flip"]:,}*',font=f(36),fill=BLK); y+=88
ctext(d,1170,'Each county: registered Democrats fell, Democratic votes for governor rose.',f(28),BLK)
ctext(d,1215,'Value = 2026 Dem votes \u2212 2022 Dem votes \u00d7 (2026 Dem reg \u00f7 2022 Dem reg)',f(26),GRAY)
ctext(d,1265,'Source: Kansas Secretary of State. *2026 UNOFFICIAL (SOS 11/08/2026; certification Dec 1).',f(22),GRAY)
ctext(d,1298,'Ranked among the 14 counties where Dem registration fell and Dem votes rose.',f(22),GRAY)
im.save(OUT+'KS_Flip_00_Summary_Top10.png')
json.dump(rows,open('rows.json','w'),indent=1); json.dump(man,open('manifest.json','w'),indent=1)
with open(OUT+'KS_Top10_Flip_Counties.csv','w',newline='') as fh:
    w=csv.writer(fh); w.writerow(['rank','county','population_2025','dem_reg_2022','dem_reg_2026','dem_reg_change','dem_gov_votes_2022','dem_gov_votes_2026_unofficial','dem_vote_change_unofficial','dem_vote_pct_change_unofficial','flip_votes_unofficial','flip_pct_of_2026_gov_votes_unofficial'])
    for r in rows: w.writerow([r[k] for k in ['rank','county','pop','reg22','reg26','reg_change','v22','v26','v_change','v_pct','flip','pct_of_race']])
print(*[(r['rank'],r['county'],r['reg_change'],r['v_change'],r['flip'],r['pct_of_race']) for r in rows],sep='\n')
