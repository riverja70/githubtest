# THANKFUL 3 Hour - builds the overlay PNGs (title, 20 KJV verse cards, CTA cards, light ramps) and verses .srt
# Run in the cloud (needs Pillow + the Cormorant/Playfair fonts). The Mac render only needs the finished PNGs in assets/.
import os, sys, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter
B=os.path.dirname(os.path.abspath(__file__)); A=B+"/assets/"
F=os.environ.get("FONTS","/mnt/project-files/scripts/fonts/")
W,H=1920,1080
GOLD=(246,208,128,255)
# 20 KJV verses, shown one at a time at 60s + 540s*i for 25s (exact KJV text)
VERSES=[
 ("Psalm 100:4","Enter into his gates with thanksgiving, and into his courts with praise: be thankful unto him, and bless his name."),
 ("Psalm 107:1","O give thanks unto the LORD, for he is good: for his mercy endureth for ever."),
 ("James 1:17","Every good gift and every perfect gift is from above, and cometh down from the Father of lights, with whom is no variableness, neither shadow of turning."),
 ("Psalm 65:11","Thou crownest the year with thy goodness; and thy paths drop fatness."),
 ("Genesis 8:22","While the earth remaineth, seedtime and harvest, and cold and heat, and summer and winter, and day and night shall not cease."),
 ("Psalm 145:16","Thou openest thine hand, and satisfiest the desire of every living thing."),
 ("Lamentations 3:22-23","It is of the LORD's mercies that we are not consumed, because his compassions fail not. They are new every morning: great is thy faithfulness."),
 ("Psalm 103:1","Bless the LORD, O my soul: and all that is within me, bless his holy name."),
 ("Deuteronomy 8:10","When thou hast eaten and art full, then thou shalt bless the LORD thy God for the good land which he hath given thee."),
 ("Psalm 100:5","For the LORD is good; his mercy is everlasting; and his truth endureth to all generations."),
 ("Psalm 95:2","Let us come before his presence with thanksgiving, and make a joyful noise unto him with psalms."),
 ("1 Thessalonians 5:18","In every thing give thanks: for this is the will of God in Christ Jesus concerning you."),
 ("Philippians 4:6","Be careful for nothing; but in every thing by prayer and supplication with thanksgiving let your requests be made known unto God."),
 ("Psalm 9:1","I will praise thee, O LORD, with my whole heart; I will shew forth all thy marvellous works."),
 ("Colossians 3:15","And let the peace of God rule in your hearts, to the which also ye are called in one body; and be ye thankful."),
 ("Psalm 107:8","Oh that men would praise the LORD for his goodness, and for his wonderful works to the children of men!"),
 ("Psalm 118:24","This is the day which the LORD hath made; we will rejoice and be glad in it."),
 ("Psalm 34:1","I will bless the LORD at all times: his praise shall continually be in my mouth."),
 ("Psalm 136:1","O give thanks unto the LORD; for he is good: for his mercy endureth for ever."),
 ("2 Corinthians 9:15","Thanks be unto God for his unspeakable gift."),
]
CTA={"sub":"Subscribe for more peaceful worship",
     "share":"Share this with someone you are thankful for",
     "amen":"Type Amen below if you are thankful"}
def font(name,size,wt=None):
    f=ImageFont.truetype(F+name,size)
    if wt:
        try: f.set_variation_by_axes([wt])
        except Exception: pass
    return f
def shadowed(fn,blur=10,k=0.8):
    txt=Image.new("RGBA",(W,H),(0,0,0,0)); fn(ImageDraw.Draw(txt))
    a=txt.split()[3].filter(ImageFilter.GaussianBlur(blur)).point(lambda v:int(min(255,v*k)))
    sh=Image.new("RGBA",(W,H),(0,0,0,0)); sh.putalpha(a)
    return Image.alpha_composite(sh,txt)
def spaced(d,text,f,y,fill,sp,cx=W/2):
    ws=[d.textlength(c,font=f) for c in text]; x=cx-(sum(ws)+sp*(len(text)-1))/2
    for c,w in zip(text,ws): d.text((x,y),c,font=f,fill=fill); x+=w+sp
def band(y0,y1,a=0.42):
    # soft dark band behind the text so it reads on a bright golden sky
    m=Image.new("L",(W,H),0); ImageDraw.Draw(m).rounded_rectangle((260,y0,W-260,y1),radius=80,fill=int(255*a))
    m=m.filter(ImageFilter.GaussianBlur(70)); im=Image.new("RGBA",(W,H),(20,12,6,0)); im.putalpha(m); return im
def verse(ref,text,out):
    body=font("CormorantGaramond.ttf",54,600); rf=font("PlayfairDisplay.ttf",28,700)
    lines=textwrap.wrap(text,44)
    def draw(d):
        spaced(d,ref.upper(),rf,58,GOLD,6)
        y=106
        for ln in lines:
            tw=d.textlength(ln,font=body); d.text(((W-tw)/2,y),ln,font=body,fill=(255,255,255,248)); y+=66
    tx=shadowed(draw,12,1.0); tx=Image.alpha_composite(shadowed(draw,4,0.7),tx)
    Image.alpha_composite(band(40,130+66*len(lines)),tx).save(out)
def title(out):
    t=font("PlayfairDisplay.ttf",132); r=font("PlayfairDisplay.ttf",40,700)
    def draw(d):
        spaced(d,"THANKFUL",t,330,(255,255,255,255),40)
        spaced(d,"PSALM 100:4",r,520,GOLD,16)
    Image.alpha_composite(band(300,600,0.38),shadowed(draw,14,1.0)).save(out)
def cta(kind,out):
    img=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(img)
    t=CTA[kind]; f=font("PlayfairDisplay.ttf",28)
    tw=d.textlength(t,font=f); bw=int(tw+150); bh=64
    x1,y1=W-60,H-150; x0,y0=x1-bw,y1-bh
    d.rounded_rectangle((x0,y0,x1,y1),radius=32,fill=(15,12,10,150),outline=(240,200,110,180),width=2)
    cx,cy=x0+46,y0+bh//2
    d.ellipse((cx-18,cy-18,cx+18,cy+18),outline=(240,200,110,255),width=3)
    sym={"sub":"♪","share":"➦","amen":"✝"}[kind]
    try: d.text((cx,cy),sym,font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",22),fill=(240,200,110,255),anchor="mm")
    except Exception: pass
    d.text((x0+82,y0+15),t,font=f,fill=(250,245,235,255))
    img.save(out)
def ramp(rgb,top,bot,out):
    # light ramp layer: colour with a vertical alpha gradient (stronger in the sky); render.py fades it in over each hour
    g=Image.linear_gradient("L").resize((W,H))  # 0 at top -> 255 at bottom
    a=g.point(lambda v:int(255*(top+(bot-top)*v/255)))
    im=Image.new("RGBA",(W,H),rgb+(0,)); im.putalpha(a); im.save(out)
def srt(out):
    fmt=lambda s:"%02d:%02d:%02d,000"%(s//3600,s%3600//60,s%60)
    with open(out,"w") as f:
        for i,(ref,txt) in enumerate(VERSES):
            s=60+540*i; f.write(f"{i+1}\n{fmt(s)} --> {fmt(s+25)}\n{txt}\n{ref} (KJV)\n\n")
if __name__=="__main__":
    os.makedirs(A,exist_ok=True)
    title(A+"title.png")
    for i,(r,t) in enumerate(VERSES): verse(r,t,A+f"v{i:02d}.png")
    for k in CTA: cta(k,A+f"cta_{k}.png")
    ramp((255,168,70),0.20,0.06,A+"ramp1.png")   # hour 1: afternoon gold deepens
    ramp((190,70,40),0.26,0.10,A+"ramp2.png")    # hour 2: sunset glow deepens
    ramp((18,24,58),0.34,0.16,A+"ramp3.png")     # hour 3: dusk turns blue (never black)
    srt(B+"/THANKFUL verses (English subtitles).srt")
    print("assets OK")
