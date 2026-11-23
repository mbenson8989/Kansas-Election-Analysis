import numpy as np, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
OUT='/workspace/kansas-wiki/repo/resources/KS_Guarantee_Clause.png'
W,H=1080,1350; rng=np.random.default_rng(7); random.seed(7)
S=lambda b,s:ImageFont.truetype(f'/usr/share/fonts/truetype/liberation/LiberationSerif-{b}.ttf',s)
# parchment
yy,xx=np.mgrid[0:H,0:W]; base=np.array([240,226,190],float)
vig=1-0.28*(((xx-W/2)/(W/2))**2+((yy-H/2)/(H/2))**2)
noise=rng.normal(0,5,(H,W)); blur=np.array(Image.fromarray(np.clip(rng.normal(128,40,(H//20,W//20)),0,255).astype('uint8')).resize((W,H),Image.BICUBIC),float)
img=base[None,None,:]*vig[...,None]+ (noise+(blur-128)*0.12)[...,None]
im=Image.fromarray(np.clip(img,0,255).astype('uint8')); d=ImageDraw.Draw(im,'RGBA')
INK=(38,28,18); NAVY=(20,40,80); GOLD=(150,105,20); BROWN=(92,64,28)
def ctext(y,t,font,fill=INK):
    d.text(((W-d.textlength(t,font=font))/2,y),t,font=font,fill=fill)
# border
for o,wd,c in [(26,5,NAVY),(40,2,GOLD)]: d.rectangle([o,o,W-o,H-o],outline=c,width=wd)
# wheat field texture at bottom
def stalk(x,base_y,h,lean):
    tx=x+lean; ty=base_y-h
    d.line([(x,base_y),(tx,ty)],fill=(150,115,40,255),width=3)
    ang=math.atan2(ty-base_y,tx-x)
    for k in range(9):
        t=k/9; px=tx-(tx-x)*t*0.22; py=ty-(ty-base_y)*t*0.22
        for s in (-1,1):
            a=ang+s*0.55; L=16
            d.ellipse([px+math.cos(a)*L-5,py+math.sin(a)*L-9,px+math.cos(a)*L+5,py+math.sin(a)*L+9],fill=(205,160,50,235))
    d.ellipse([tx-5,ty-12,tx+5,ty+4],fill=(215,170,60,240))
d.rectangle([40,1130,W-40,H-40],fill=(214,178,86,70))
for i in range(260):
    x=random.randint(46,W-46); b=random.randint(1190,H-44); stalk(x,b,random.randint(90,170),random.randint(-22,22))
# capitol silhouette (Kansas State Capitol: cruciform building, copper dome with lantern)
cx=W//2; gy=1305; col=(36,48,70,255)
d.rectangle([cx-250,gy-120,cx+250,gy],fill=col)             # main body
d.rectangle([cx-300,gy-90,cx-250,gy],fill=col); d.rectangle([cx+250,gy-90,cx+300,gy],fill=col)
d.polygon([(cx-90,gy-120),(cx+90,gy-120),(cx+90,gy-140),(cx-90,gy-140)],fill=col)
d.rectangle([cx-105,gy-190,cx+105,gy-140],fill=col)         # drum base
for k in range(-4,5): d.rectangle([cx+k*22-4,gy-188,cx+k*22+4,gy-142],fill=(36,48,70,255),outline=(240,226,190,120))
d.pieslice([cx-100,gy-300,cx+100,gy-80],180,360,fill=col)   # dome
d.rectangle([cx-12,gy-330,cx+12,gy-290],fill=col); d.polygon([(cx,gy-372),(cx-9,gy-330),(cx+9,gy-330)],fill=col)
for k in range(-6,7): d.rectangle([cx+k*34-5,gy-112,cx+k*34+5,gy-8],fill=(240,226,190,110))  # columns hint
d.rectangle([cx-30,gy-60,cx+30,gy],fill=(20,28,44,255))
# sunflowers on each side
def sunflower(x,y,r):
    for k in range(24):
        a=2*math.pi*k/24; px=x+math.cos(a)*r*1.05; py=y+math.sin(a)*r*1.05
        pts=[(x+math.cos(a-0.16)*r*0.55,y+math.sin(a-0.16)*r*0.55),(px+math.cos(a)*r*0.45,py+math.sin(a)*r*0.45),(x+math.cos(a+0.16)*r*0.55,y+math.sin(a+0.16)*r*0.55)]
        d.polygon(pts,fill=(230,170,20,255),outline=(150,100,10,255))
    d.ellipse([x-r*0.62,y-r*0.62,x+r*0.62,y+r*0.62],fill=(70,42,16,255),outline=(40,24,8,255))
    for k in range(60):
        a=k*2.39996; rr=r*0.58*math.sqrt(k/60); d.ellipse([x+math.cos(a)*rr-2,y+math.sin(a)*rr-2,x+math.cos(a)*rr+2,y+math.sin(a)*rr+2],fill=(130,85,35,255))
for x,y,r in [(135,1150,70),(W-135,1150,70)]:
    d.line([(x,y+r),(x+(8 if x<W/2 else -8),H-40)],fill=(70,100,40,255),width=9)
    d.ellipse([x-(55 if x<W/2 else -5),y+r+60,x+(5 if x<W/2 else 55),y+r+95],fill=(80,115,45,255))
    sunflower(x,y,r)
# text
ctext(70,'THE UNITED STATES CONSTITUTION',S('Regular',30),GOLD)
ctext(110,'ARTICLE IV, SECTION 4',S('Bold',34),NAVY)
d.line([(300,160),(W-300,160)],fill=GOLD,width=3)
ctext(185,'THE GUARANTEE CLAUSE',S('Bold',74),INK)
q=['\u201cThe United States shall guarantee to every State','in this Union a Republican Form of Government\u2026\u201d']
for i,t in enumerate(q): ctext(290+i*46,t,S('Italic',38),BROWN)
d.line([(300,400),(W-300,400)],fill=GOLD,width=3)
ctext(418,'Did you know?',S('Bold',54),NAVY)
lines=['It\u2019s NOT your job to prove','our elections are free and fair.']
for i,t in enumerate(lines): ctext(492+i*74,t,S('Bold',66),INK)
ctext(650,'The Guarantee Clause puts that',S('Regular',48),INK); ctext(705,'on the government.',S('Bold',50),NAVY)
d.rounded_rectangle([110,768,W-110,935],radius=10,fill=(250,243,222,215),outline=GOLD,width=3)
ctext(780,'EXECUTIVE ORDER 14399',S('Bold',36),NAVY)
ctext(822,'signed March 31, 2026 \u00b7 91 Fed. Reg. 17125',S('Regular',30),BROWN)
ctext(862,'\u201cThe Federal Government has an unavoidable duty',S('Italic',32),INK)
ctext(896,'\u2026 to enforce Federal law.\u201d  (Sec. 1)',S('Italic',34),INK)
im.save(OUT); print('ok')
