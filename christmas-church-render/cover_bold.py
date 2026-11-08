# Bolder cover options for GREAT JOY. Usage: python3 cover_bold.py still_4k.png outdir
import sys, os, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageChops
B=os.path.dirname(os.path.abspath(__file__)); F=B+"/fonts/"; W,H=1920,1080
src=Image.open(sys.argv[1]).convert("RGB"); out=sys.argv[2]
STRIP="CHRISTMAS PIANO & CELLO CAROLS  |  A SNOWY VILLAGE CHURCH"
def font(n,s,wt=None):
    f=ImageFont.truetype(F+n,s)
    if wt:
        try: f.set_variation_by_axes([wt])
        except Exception: pass
    return f
def crop(cx,cy,cw):
    W0,H0=src.size; w=int(W0*cw); h=int(w*9/16); x0=max(0,min(W0-w,int(W0*cx-w/2))); y0=max(0,min(H0-h,int(H0*cy-h/2)))
    return src.crop((x0,y0,x0+w,y0+h)).resize((W,H),Image.LANCZOS)
def punch(im):
    im=ImageEnhance.Color(im).enhance(1.18); im=ImageEnhance.Contrast(im).enhance(1.10)
    a=np.asarray(im).astype(np.float32)/255
    lum=a.max(axis=2); warm=(a[...,0]>a[...,2]+0.08)&(lum>0.55)            # warm light: windows, lamps, bulbs
    m=Image.fromarray((warm*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(18))
    glow=Image.composite(Image.new("RGB",(W,H),(255,170,70)),Image.new("RGB",(W,H),(0,0,0)),m)
    im=ImageChops.screen(im,ImageEnhance.Brightness(glow).enhance(0.55))
    v=Image.new("L",(W,H),0); ImageDraw.Draw(v).ellipse((-300,-250,W+300,H+250),fill=255)
    v=v.filter(ImageFilter.GaussianBlur(200)); return Image.composite(im,Image.new("RGB",(W,H),(4,6,14)),v)
def spaced(d,text,f,y,fill,spc,cx):
    ws=[d.textlength(c,font=f) for c in text]; x=cx-(sum(ws)+spc*(len(text)-1))/2
    for c,w in zip(text,ws): d.text((x,y),c,font=f,fill=fill); x+=w+spc
    return cx-(sum(ws)+spc*(len(text)-1))/2, x
def title(im,cx,y,size,spc,gold=False,halo=True,maxw=860):
    im=im.convert("RGBA")
    while True:
        tf=font("PlayfairDisplay.ttf",size,800); dd=ImageDraw.Draw(im)
        tw=sum(dd.textlength(c,font=tf) for c in "GREAT JOY")+spc*8
        if tw<=maxw: break
        size-=4; spc=max(8,spc-1)
    cx=max(cx,40+tw/2)
    rf=font("PlayfairDisplay.ttf",int(size*0.36),800)
    if halo:
        h=Image.new("L",(W,H),0); ImageDraw.Draw(h).ellipse((cx-640,y-80,cx+640,y+size*2.2),fill=140)
        h=h.filter(ImageFilter.GaussianBlur(80)); hl=Image.new("RGBA",(W,H),(6,8,18,0)); hl.putalpha(h); im=Image.alpha_composite(im,hl)
    txt=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(txt)
    col=(255,226,150,255) if gold else (255,255,255,255)
    spaced(d,"GREAT JOY",tf,y,col,spc,cx); spaced(d,"LUKE 2:10",rf,y+int(size*1.42),(250,205,110,255),int(spc*0.6),cx)
    a=txt.split()[3]
    sh=Image.new("RGBA",(W,H),(0,0,0,0)); sh.putalpha(a.filter(ImageFilter.GaussianBlur(14)).point(lambda v:int(v*0.95)))
    gl=Image.new("RGBA",(W,H),(255,200,110,0)); gl.putalpha(a.filter(ImageFilter.GaussianBlur(28)).point(lambda v:int(v*0.55)))
    return Image.alpha_composite(Image.alpha_composite(Image.alpha_composite(im,sh),gl),txt)
def strip(im):
    d=ImageDraw.Draw(im); sf=font("PlayfairDisplay.ttf",36); d.rectangle((0,H-72,W,H),fill=(0,0,0,255))
    tw=d.textlength(STRIP,font=sf); d.text(((W-tw)/2,H-59),STRIP,font=sf,fill=(245,240,230,255)); return im.convert("RGB")
# A: same framing as the video, punchier color + glow, bigger gold title
a=strip(title(punch(crop(0.5,0.5,1.0)),490,60,170,20,gold=True,maxw=880)); a.save(out+"/Cover option A (bold, same view).jpg",quality=93)
# B: closer on the church, big gold title over the left sky
b=strip(title(punch(crop(0.55,0.58,0.80)),420,40,170,20,gold=True,maxw=760)); b.save(out+"/Cover option B (closer).jpg",quality=93)
# C: same framing, big white title with gold reference
c=strip(title(punch(crop(0.5,0.5,1.0)),490,60,170,20,gold=False,maxw=880)); c.save(out+"/Cover option C (white title).jpg",quality=93)
S=Image.new("RGB",(1920,360)); [S.paste(x.resize((640,360),Image.LANCZOS),(640*i,0)) for i,x in enumerate((a,b,c))]; S.save(out+"/Cover options A-C.jpg",quality=90)
print("ok")
