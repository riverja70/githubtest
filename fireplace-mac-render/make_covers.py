# Christmas Fireplace covers: big spaced "JESUS" + gold MATTHEW 1:21 + thin strip. usage: python3 make_covers.py src.png out.jpg [title_y]
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
F=os.environ.get("FONTS","/mnt/project-files/scripts/fonts/"); GOLD=(246,208,128)
def spaced(d,text,f,y,fill,sp,W):
    ws=[d.textlength(c,font=f) for c in text]; x=(W-(sum(ws)+sp*(len(text)-1)))/2
    for c,w in zip(text,ws): d.text((x,y),c,font=f,fill=fill); x+=w+sp
def cover(src,out,ty=60,band=0.40,vig=0.5,strip="3 HOURS  |  CHRISTMAS PIANO WORSHIP  |  PRAYER & REST",text=True,size=(1920,1080)):
    im=Image.open(src).convert("RGB").resize(size,Image.LANCZOS); W,H=im.size
    im=ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(1.06)).enhance(1.04)
    m=Image.new("L",(W,H),0); ImageDraw.Draw(m).ellipse((-W*0.15,-H*0.2,W*1.15,H*1.25),fill=255)
    m=m.filter(ImageFilter.GaussianBlur(160)).point(lambda v:int(255-(255-v)*vig)); im=Image.composite(im,Image.new("RGB",(W,H)),m)
    if not text: im.save(out,quality=95) if out.endswith('.jpg') else im.save(out); return
    b=Image.new("L",(W,H),0); ImageDraw.Draw(b).rectangle((0,ty+10,W,ty+250),fill=int(255*band)); im.paste((0,0,0),(0,0),b.filter(ImageFilter.GaussianBlur(60)))
    t=ImageFont.truetype(F+"PlayfairDisplay.ttf",160); r=ImageFont.truetype(F+"PlayfairDisplay.ttf",46)
    try: r.set_variation_by_axes([700])
    except Exception: pass
    s=ImageFont.truetype(F+"PlayfairDisplay.ttf",34)
    sh=Image.new("L",(W,H),0); d=ImageDraw.Draw(sh); spaced(d,"JESUS",t,ty,255,60,W); spaced(d,"MATTHEW 1:21",r,ty+210,255,18,W)
    im.paste((0,0,0),(0,0),sh.filter(ImageFilter.GaussianBlur(14)).point(lambda v:int(v*0.75)))
    im.paste((0,0,0),(0,0),sh.filter(ImageFilter.GaussianBlur(5)).point(lambda v:int(v*0.55)))
    d=ImageDraw.Draw(im); spaced(d,"JESUS",t,ty,(255,255,255),60,W); spaced(d,"MATTHEW 1:21",r,ty+210,GOLD,18,W)
    d.rectangle((0,H-70,W,H),fill=(0,0,0)); tw=d.textlength(strip,font=s); d.text(((W-tw)/2,H-58),strip,font=s,fill=(240,240,240))
    im.save(out,quality=92)
if __name__=="__main__":
    cover(sys.argv[1],sys.argv[2],int(sys.argv[3]) if len(sys.argv)>3 else 60)
