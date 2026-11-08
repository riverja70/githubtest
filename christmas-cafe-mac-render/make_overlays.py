# Builds cover, hover-hook title layer, verse cards and CTA cards (1920x1080) for the Christmas cafe video.
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
TITLE="EMMANUEL"; REF="MATTHEW 1:23"
STRIP="1 HOUR  |  SOFT PIANO CHRISTMAS CAROLS  |  SCRIPTURE BY THE FIRE"
def spaced(d,text,f,y,fill,spc):
    ws=[d.textlength(c,font=f) for c in text]; x=(W-(sum(ws)+spc*(len(text)-1)))/2
    for c,w in zip(text,ws): d.text((x,y),c,font=f,fill=fill); x+=w+spc
def title_layer(strip=True):
    tf=font("PlayfairDisplay.ttf",132); rf=font("PlayfairDisplay.ttf",42,800); sf=font("PlayfairDisplay.ttf",34)
    txt=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(txt)
    spaced(d,TITLE,tf,60,(255,255,255,255),40); spaced(d,REF,rf,248,(250,210,120,255),16)
    a=txt.split()[3].filter(ImageFilter.GaussianBlur(16)).point(lambda v:int(v*0.8))
    sh=Image.new("RGBA",(W,H),(0,0,0,0)); sh.putalpha(a)
    # soft dark halo behind the title so it reads over the lights
    halo=Image.new("L",(W,H),0); ImageDraw.Draw(halo).ellipse((W/2-620,10,W/2+620,330),fill=120)
    halo=halo.filter(ImageFilter.GaussianBlur(70)); hl=Image.new("RGBA",(W,H),(10,6,4,0)); hl.putalpha(halo)
    out=Image.alpha_composite(Image.alpha_composite(hl,sh),txt)
    if strip:
        d=ImageDraw.Draw(out); d.rectangle((0,H-70,W,H),fill=(0,0,0,255))
        tw=d.textlength(STRIP,font=sf); d.text(((W-tw)/2,H-58),STRIP,font=sf,fill=(240,240,240,255))
    return out
VERSES=[
 ("For unto us a child is born, unto us a son is given: and the government shall be upon his shoulder: and his name shall be called Wonderful, Counsellor, The mighty God, The everlasting Father, The Prince of Peace.","Isaiah 9:6"),
 ("Behold, a virgin shall be with child, and shall bring forth a son, and they shall call his name Emmanuel, which being interpreted is, God with us.","Matthew 1:23"),
 ("And she brought forth her firstborn son, and wrapped him in swaddling clothes, and laid him in a manger; because there was no room for them in the inn.","Luke 2:7"),
 ("And the angel said unto them, Fear not: for, behold, I bring you good tidings of great joy, which shall be to all people.","Luke 2:10"),
 ("For unto you is born this day in the city of David a Saviour, which is Christ the Lord.","Luke 2:11"),
 ("Glory to God in the highest, and on earth peace, good will toward men.","Luke 2:14"),
 ("When they saw the star, they rejoiced with exceeding great joy.","Matthew 2:10"),
 ("But Mary kept all these things, and pondered them in her heart.","Luke 2:19"),
 ("And the Word was made flesh, and dwelt among us, (and we beheld his glory, the glory as of the only begotten of the Father,) full of grace and truth.","John 1:14"),
 ("For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.","John 3:16"),
]
def verse(text,ref,out):
    body=font("CormorantGaramond.ttf",52,600); rf=font("PlayfairDisplay.ttf",30,800)
    lines=textwrap.wrap(text,42); lh=64; top=80
    txt=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(txt)
    d.text((W/2,top),ref.upper(),font=rf,fill=(250,210,120,255),anchor="mt")
    y=top+58
    for ln in lines: d.text((W/2,y),ln,font=body,fill=(255,255,255,250),anchor="mt"); y+=lh
    a=txt.split()[3].filter(ImageFilter.GaussianBlur(10)).point(lambda v:int(v*0.85))
    sh=Image.new("RGBA",(W,H),(0,0,0,0)); sh.putalpha(a)
    halo=Image.new("L",(W,H),0); ImageDraw.Draw(halo).rounded_rectangle((W/2-700,top-40,W/2+700,y+30),radius=120,fill=130)
    halo=halo.filter(ImageFilter.GaussianBlur(60)); hl=Image.new("RGBA",(W,H),(10,6,4,0)); hl.putalpha(halo)
    Image.alpha_composite(Image.alpha_composite(hl,sh),txt).save(out)
def cta(kind,out):
    img=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(img)
    msgs={"sub":"Subscribe for more peaceful worship","share":"Share this peace with someone this Christmas","amen":"Type Amen if you believe"}
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
    for i,(t,r) in enumerate(VERSES): verse(t,r,A+f"v{i:02d}.png")
    for k in ("sub","share","amen"): cta(k,A+f"cta_{k}.png")
    print("ok")
