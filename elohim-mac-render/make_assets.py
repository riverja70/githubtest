# ELOHIM harp 3 Hour - builds overlay PNGs (20 KJV verse cards, CTA cards) + verses .srt. Cloud only (Pillow + fonts).
import os, json, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter
B=os.path.dirname(os.path.abspath(__file__)); A=B+"/assets/"
F=os.environ.get("FONTS","/mnt/project-files/scripts/fonts/")
S=int(os.environ.get("RES","2160"))/1080; W,H=int(1920*S),int(1080*S); GOLD=(246,208,128,255)
VERSES=json.load(open(B+"/verses.json"))
CTA={"sub":"Subscribe for more peaceful worship","share":"Share this with someone who needs peace tonight","amen":"Type Amen below if God is your Creator"}
def font(name,size,wt=None):
    f=ImageFont.truetype(F+name,int(size*S))
    if wt:
        try: f.set_variation_by_axes([wt])
        except Exception: pass
    return f
def shadowed(fn,blur=10,k=0.8):
    blur=blur*S
    txt=Image.new("RGBA",(W,H),(0,0,0,0)); fn(ImageDraw.Draw(txt))
    a=txt.split()[3].filter(ImageFilter.GaussianBlur(blur)).point(lambda v:int(min(255,v*k)))
    sh=Image.new("RGBA",(W,H),(0,0,0,0)); sh.putalpha(a); return Image.alpha_composite(sh,txt)
def spaced(d,text,f,y,fill,sp,cx=W/2):
    ws=[d.textlength(c,font=f) for c in text]; x=cx-(sum(ws)+sp*(len(text)-1))/2
    for c,w in zip(text,ws): d.text((x,y),c,font=f,fill=fill); x+=w+sp
def band(y0,y1,a=0.5):
    m=Image.new("L",(W,H),0); ImageDraw.Draw(m).rounded_rectangle((240*S,y0*S,W-240*S,y1*S),radius=80*S,fill=int(255*a))
    m=m.filter(ImageFilter.GaussianBlur(70*S)); im=Image.new("RGBA",(W,H),(12,8,6,0)); im.putalpha(m); return im
def verse(ref,text,out):
    body=font("CormorantGaramond.ttf",54,600); rf=font("PlayfairDisplay.ttf",28,700)
    lines=textwrap.wrap(text,46)
    def draw(d):
        spaced(d,ref.upper(),rf,58*S,GOLD,6*S); y=106*S
        for ln in lines:
            tw=d.textlength(ln,font=body); d.text(((W-tw)/2,y),ln,font=body,fill=(255,255,255,248)); y+=66*S
    tx=Image.alpha_composite(shadowed(draw,4,0.7),shadowed(draw,12,1.0))
    Image.alpha_composite(band(40,130+66*len(lines)),tx).save(out)
def cta(kind,out):
    img=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(img)
    t=CTA[kind]; f=font("PlayfairDisplay.ttf",28); tw=d.textlength(t,font=f); bw=int(tw+150*S); bh=int(64*S)
    x1,y1=W-int(60*S),H-int(150*S); x0,y0=x1-bw,y1-bh
    d.rounded_rectangle((x0,y0,x1,y1),radius=int(32*S),fill=(15,12,10,150),outline=(240,200,110,180),width=int(2*S))
    cx,cy=x0+int(46*S),y0+bh//2; r=int(18*S); d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(240,200,110,255),width=int(3*S))
    sym={"sub":"♪","share":"➦","amen":"✝"}[kind]
    try: d.text((cx,cy),sym,font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",int(22*S)),fill=(240,200,110,255),anchor="mm")
    except Exception: pass
    d.text((x0+int(82*S),y0+int(15*S)),t,font=f,fill=(250,245,235,255)); img.save(out)
def srt(out):
    fmt=lambda s:"%02d:%02d:%02d,000"%(s//3600,s%3600//60,s%60)
    with open(out,"w") as f:
        for i,(ref,txt) in enumerate(VERSES):
            s=60+540*i; f.write(f"{i+1}\n{fmt(s)} --> {fmt(s+25)}\n{txt}\n{ref} (KJV)\n\n")
if __name__=="__main__":
    os.makedirs(A,exist_ok=True)
    for i,(r,t) in enumerate(VERSES): verse(r,t,A+f"v{i:02d}.png")
    for k in CTA: cta(k,A+f"cta_{k}.png")
    srt(B+"/ELOHIM verses (English subtitles).srt"); print("assets OK")
