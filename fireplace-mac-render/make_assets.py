# Christmas Fireplace 3 Hour - builds overlay PNGs (20 KJV verse cards, CTA cards) + verses .srt. Cloud only (Pillow + fonts).
import os, json, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter
B=os.path.dirname(os.path.abspath(__file__)); A=B+"/assets/"
F=os.environ.get("FONTS","/mnt/project-files/scripts/fonts/")
W,H=1920,1080; GOLD=(246,208,128,255)
VERSES=json.load(open(B+"/verses.json"))
CTA={"sub":"Subscribe for more peaceful worship","share":"Share this with someone you love this Christmas","amen":"Type Amen below if Jesus is your peace"}
def font(name,size,wt=None):
    f=ImageFont.truetype(F+name,size)
    if wt:
        try: f.set_variation_by_axes([wt])
        except Exception: pass
    return f
def shadowed(fn,blur=10,k=0.8):
    txt=Image.new("RGBA",(W,H),(0,0,0,0)); fn(ImageDraw.Draw(txt))
    a=txt.split()[3].filter(ImageFilter.GaussianBlur(blur)).point(lambda v:int(min(255,v*k)))
    sh=Image.new("RGBA",(W,H),(0,0,0,0)); sh.putalpha(a); return Image.alpha_composite(sh,txt)
def spaced(d,text,f,y,fill,sp,cx=W/2):
    ws=[d.textlength(c,font=f) for c in text]; x=cx-(sum(ws)+sp*(len(text)-1))/2
    for c,w in zip(text,ws): d.text((x,y),c,font=f,fill=fill); x+=w+sp
def band(y0,y1,a=0.5):
    m=Image.new("L",(W,H),0); ImageDraw.Draw(m).rounded_rectangle((240,y0,W-240,y1),radius=80,fill=int(255*a))
    m=m.filter(ImageFilter.GaussianBlur(70)); im=Image.new("RGBA",(W,H),(12,8,6,0)); im.putalpha(m); return im
def verse(ref,text,out):
    body=font("CormorantGaramond.ttf",54,600); rf=font("PlayfairDisplay.ttf",28,700)
    lines=textwrap.wrap(text,46)
    def draw(d):
        spaced(d,ref.upper(),rf,58,GOLD,6); y=106
        for ln in lines:
            tw=d.textlength(ln,font=body); d.text(((W-tw)/2,y),ln,font=body,fill=(255,255,255,248)); y+=66
    tx=Image.alpha_composite(shadowed(draw,4,0.7),shadowed(draw,12,1.0))
    Image.alpha_composite(band(40,130+66*len(lines)),tx).save(out)
def cta(kind,out):
    img=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(img)
    t=CTA[kind]; f=font("PlayfairDisplay.ttf",28); tw=d.textlength(t,font=f); bw=int(tw+150); bh=64
    x1,y1=W-60,H-150; x0,y0=x1-bw,y1-bh
    d.rounded_rectangle((x0,y0,x1,y1),radius=32,fill=(15,12,10,150),outline=(240,200,110,180),width=2)
    cx,cy=x0+46,y0+bh//2; d.ellipse((cx-18,cy-18,cx+18,cy+18),outline=(240,200,110,255),width=3)
    sym={"sub":"♪","share":"➦","amen":"✝"}[kind]
    try: d.text((cx,cy),sym,font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",22),fill=(240,200,110,255),anchor="mm")
    except Exception: pass
    d.text((x0+82,y0+15),t,font=f,fill=(250,245,235,255)); img.save(out)
def srt(out):
    fmt=lambda s:"%02d:%02d:%02d,000"%(s//3600,s%3600//60,s%60)
    with open(out,"w") as f:
        for i,(ref,txt) in enumerate(VERSES):
            s=60+540*i; f.write(f"{i+1}\n{fmt(s)} --> {fmt(s+25)}\n{txt}\n{ref} (KJV)\n\n")
if __name__=="__main__":
    os.makedirs(A,exist_ok=True)
    for i,(r,t) in enumerate(VERSES): verse(r,t,A+f"v{i:02d}.png")
    for k in CTA: cta(k,A+f"cta_{k}.png")
    srt(B+"/Christmas verses (English subtitles).srt"); print("assets OK")
