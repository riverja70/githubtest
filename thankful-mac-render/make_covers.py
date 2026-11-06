# THANKFUL covers: main (pop) + B + C for YouTube Test & Compare. Same style as Jesus Heals cover v4.
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
B=os.path.dirname(os.path.abspath(__file__)); C=B+"/covers/"
F=os.environ.get("FONTS","/mnt/project-files/scripts/fonts/")
GOLD=(246,208,128)
def spaced(d,text,f,y,fill,sp,W):
    ws=[d.textlength(c,font=f) for c in text]; x=(W-(sum(ws)+sp*(len(text)-1)))/2
    for c,w in zip(text,ws): d.text((x,y),c,font=f,fill=fill); x+=w+sp
def cover(src,out,ty=70,band=0.42,vig=0.55):
    im=Image.open(src).convert("RGB"); W,H=im.size
    im=ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(1.12)).enhance(1.06)
    # darker edges (vignette)
    m=Image.new("L",(W,H),0); ImageDraw.Draw(m).ellipse((-W*0.15,-H*0.2,W*1.15,H*1.25),fill=255)
    m=m.filter(ImageFilter.GaussianBlur(160)).point(lambda v:int(255-(255-v)*vig))
    im=Image.composite(im,Image.new("RGB",(W,H),(0,0,0)),m)
    # soft dark band behind the title
    b=Image.new("L",(W,H),0); ImageDraw.Draw(b).rectangle((0,ty+10,W,ty+250),fill=int(255*band))
    b=b.filter(ImageFilter.GaussianBlur(60)); im.paste((0,0,0),(0,0),b)
    t=ImageFont.truetype(F+"PlayfairDisplay.ttf",150); r=ImageFont.truetype(F+"PlayfairDisplay.ttf",46)
    try: r.set_variation_by_axes([700])
    except Exception: pass
    s=ImageFont.truetype(F+"PlayfairDisplay.ttf",34)
    sh=Image.new("L",(W,H),0); d=ImageDraw.Draw(sh)
    spaced(d,"THANKFUL",t,ty,255,44,W); spaced(d,"PSALM 100:4",r,ty+200,255,18,W)
    im.paste((0,0,0),(0,0),sh.filter(ImageFilter.GaussianBlur(14)).point(lambda v:int(v*0.75)))
    im.paste((0,0,0),(0,0),sh.filter(ImageFilter.GaussianBlur(5)).point(lambda v:int(v*0.55)))  # tighter shadow so gold reads on leaves
    d=ImageDraw.Draw(im)
    spaced(d,"THANKFUL",t,ty,(255,255,255),44,W); spaced(d,"PSALM 100:4",r,ty+200,GOLD,18,W)
    d.rectangle((0,H-70,W,H),fill=(0,0,0))
    st="3 HOURS  |  SOAKING WORSHIP INSTRUMENTAL  |  PRAYER & GRATITUDE"
    tw=d.textlength(st,font=s); d.text(((W-tw)/2,H-58),st,font=s,fill=(240,240,240))
    im.save(out,quality=92)
if __name__=="__main__":
    cover(C+"frame1.png",C+"THANKFUL cover (main, pop).jpg")
    cover(C+"frame2.png",C+"THANKFUL cover B (oak sunset).jpg",band=0.6)
    cover(C+"frame3.png",C+"THANKFUL cover C (chapel dusk).jpg")
    print("covers OK")
