# Builds cover, hover-hook title layer, verse cards and CTA cards (1920x1080) for the Great Joy village church video.
# Usage: python3 make_overlays.py <still.png>
import sys, os, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter
B=os.path.dirname(os.path.abspath(__file__)); A=B+"/assets/"
F=os.environ.get("FONTS", B+"/fonts/")
W,H=1920,1080
def font(name,size,wt=None):
    f=ImageFont.truetype(F+name,size)
    if wt:
        try: f.set_variation_by_axes([wt])
        except Exception: pass
    return f
TITLE="GREAT JOY"; REF="LUKE 2:10"; TX=500  # title over the left sky, the steeple stays free
STRIP="1 HOUR  |  CHRISTMAS PIANO & CELLO CAROLS  |  A SNOWY VILLAGE CHURCH"
def spaced(d,text,f,y,fill,spc,cx=None):
    cx=TX if cx is None else cx
    ws=[d.textlength(c,font=f) for c in text]; x=cx-(sum(ws)+spc*(len(text)-1))/2
    for c,w in zip(text,ws): d.text((x,y),c,font=f,fill=fill); x+=w+spc
def title_layer(strip=True,text=None):
    global STRIP
    if text: STRIP=text
    tf=font("PlayfairDisplay.ttf",112); rf=font("PlayfairDisplay.ttf",42,800); sf=font("PlayfairDisplay.ttf",34)
    txt=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(txt)
    spaced(d,TITLE,tf,70,(255,255,255,255),30); spaced(d,REF,rf,248,(250,210,120,255),16)
    a=txt.split()[3].filter(ImageFilter.GaussianBlur(16)).point(lambda v:int(v*0.8))
    sh=Image.new("RGBA",(W,H),(0,0,0,0)); sh.putalpha(a)
    # soft dark halo behind the title so it reads over the lights
    halo=Image.new("L",(W,H),0); ImageDraw.Draw(halo).ellipse((TX-520,10,TX+520,330),fill=110)
    halo=halo.filter(ImageFilter.GaussianBlur(70)); hl=Image.new("RGBA",(W,H),(10,6,4,0)); hl.putalpha(halo)
    out=Image.alpha_composite(Image.alpha_composite(hl,sh),txt)
    if strip:
        d=ImageDraw.Draw(out); d.rectangle((0,H-70,W,H),fill=(0,0,0,255))
        tw=d.textlength(STRIP,font=sf); d.text(((W-tw)/2,H-58),STRIP,font=sf,fill=(240,240,240,255))  # strip stays centred
    return out
VERSES=[
 ("And the angel said unto them, Fear not: for, behold, I bring you good tidings of great joy, which shall be to all people.","Luke 2:10"),
 ("O come, let us worship and bow down: let us kneel before the LORD our maker.","Psalm 95:6"),
 ("The people that walked in darkness have seen a great light: they that dwell in the land of the shadow of death, upon them hath the light shined.","Isaiah 9:2"),
 ("And the shepherds returned, glorifying and praising God for all the things that they had heard and seen, as it was told unto them.","Luke 2:20"),
 ("And the light shineth in darkness; and the darkness comprehended it not.","John 1:5"),
 ("In this was manifested the love of God toward us, because that God sent his only begotten Son into the world, that we might live through him.","1 John 4:9"),
]
def verse(text,ref,out):
    body=font("CormorantGaramond.ttf",52,600); rf=font("PlayfairDisplay.ttf",30,800)
    lines=textwrap.wrap(text,34); lh=64; top=80; VX=520
    txt=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(txt)
    d.text((VX,top),ref.upper(),font=rf,fill=(250,210,120,255),anchor="mt")
    y=top+58
    for ln in lines: d.text((VX,y),ln,font=body,fill=(255,255,255,250),anchor="mt"); y+=lh
    a=txt.split()[3].filter(ImageFilter.GaussianBlur(10)).point(lambda v:int(v*0.85))
    sh=Image.new("RGBA",(W,H),(0,0,0,0)); sh.putalpha(a)
    halo=Image.new("L",(W,H),0); ImageDraw.Draw(halo).rounded_rectangle((VX-520,top-40,VX+520,y+30),radius=120,fill=130)
    halo=halo.filter(ImageFilter.GaussianBlur(60)); hl=Image.new("RGBA",(W,H),(10,6,4,0)); hl.putalpha(halo)
    Image.alpha_composite(Image.alpha_composite(hl,sh),txt).save(out)
def cta(kind,out):
    img=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(img)
    msgs={"sub":"Subscribe for more peaceful worship","share":"Share this Christmas peace with someone you love","amen":"Type Amen if you believe"}
    t=msgs[kind]; f=font("PlayfairDisplay.ttf",28)
    tw=d.textlength(t,font=f); bw=int(tw+80); bh=64
    x1,y1=W-60,H-150; x0,y0=x1-bw,y1-bh
    d.rounded_rectangle((x0,y0,x1,y1),radius=32,fill=(15,12,10,165),outline=(240,200,110,190),width=2)
    d.text((x0+40,y0+15),t,font=f,fill=(250,245,235,255)); img.save(out)
if __name__=="__main__":
    still=Image.open(sys.argv[1]).convert("RGB").resize((W,H),Image.LANCZOS)
    still.save(A+"still_1080.png")
    cov=Image.alpha_composite(still.convert("RGBA"),title_layer()).convert("RGB")
    cov.save(A+"cover.jpg",quality=93); cov.resize((1280,720),Image.LANCZOS).save(A+"cover_1280.jpg",quality=92)
    title_layer().save(A+"title.png")   # hover hook: frame 1 = exact cover, fades out over the first seconds
    S10="CHRISTMAS PIANO & CELLO CAROLS  |  A SNOWY VILLAGE CHURCH"
    title_layer(text=S10).save(A+"title_10min.png")
    c10=Image.alpha_composite(still.convert("RGBA"),title_layer(text=S10)).convert("RGB")
    c10.save(A+"cover_10min.jpg",quality=93); c10.resize((1280,720),Image.LANCZOS).save(A+"cover_10min_1280.jpg",quality=92)
    STRIP_1H="1 HOUR  |  CHRISTMAS PIANO & CELLO CAROLS  |  A SNOWY VILLAGE CHURCH"; title_layer(text=STRIP_1H)
    for i,(t,r) in enumerate(VERSES): verse(t,r,A+f"v{i:02d}.png")
    for k in ("sub","share","amen"): cta(k,A+f"cta_{k}.png")
    print("ok")
