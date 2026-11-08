# Alternate cover: zoom on the window with the Empire State Building as the hero, title low over a soft dark band.
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
B=os.path.dirname(os.path.abspath(__file__)); F=B+"/fonts/"
src=Image.open(sys.argv[1]).convert("RGB"); W0,H0=src.size
cx,cy,cw=float(sys.argv[3]),float(sys.argv[4]),float(sys.argv[5])   # crop centre (fractions) and width (fraction)
w=int(W0*cw); h=int(w*9/16); x0=int(W0*cx-w/2); y0=int(H0*cy-h/2); x0=max(0,min(W0-w,x0)); y0=max(0,min(H0-h,y0))
im=src.crop((x0,y0,x0+w,y0+h)).resize((1920,1080),Image.LANCZOS)
im=ImageEnhance.Contrast(im).enhance(1.05); W,H=im.size
def font(n,s,wt=None):
    f=ImageFont.truetype(F+n,s)
    if wt:
        try: f.set_variation_by_axes([wt])
        except Exception: pass
    return f
def spaced(d,text,f,y,fill,spc,cx=W/2):
    ws=[d.textlength(c,font=f) for c in text]; x=cx-(sum(ws)+spc*(len(text)-1))/2
    for c,wd in zip(text,ws): d.text((x,y),c,font=f,fill=fill); x+=wd+spc
mode=sys.argv[6] if len(sys.argv)>6 else "low"
ty=640 if mode=="low" else 60
band=Image.new("L",(W,H),0); ImageDraw.Draw(band).rectangle((0,ty-60,W,ty+300),fill=150)
band=band.filter(ImageFilter.GaussianBlur(80)); dark=Image.new("RGB",(W,H),(8,5,3)); im=Image.composite(dark,im,band)
txt=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(txt)
spaced(d,"EMMANUEL",font("PlayfairDisplay.ttf",138),ty,(255,255,255,255),42); spaced(d,"MATTHEW 1:23",font("PlayfairDisplay.ttf",44,800),ty+190,(250,210,120,255),16)
a=txt.split()[3].filter(ImageFilter.GaussianBlur(16)).point(lambda v:int(v*0.8)); sh=Image.new("RGBA",(W,H),(0,0,0,0)); sh.putalpha(a)
im=Image.alpha_composite(Image.alpha_composite(im.convert("RGBA"),sh),txt)
d=ImageDraw.Draw(im); sf=font("PlayfairDisplay.ttf",34); d.rectangle((0,H-70,W,H),fill=(0,0,0,255))
t=sys.argv[7] if len(sys.argv)>7 else "CHRISTMAS PIANO CAROLS  |  SCRIPTURE BY THE FIRE"
tw=d.textlength(t,font=sf); d.text(((W-tw)/2,H-58),t,font=sf,fill=(240,240,240,255))
im=im.convert("RGB"); im.save(sys.argv[2],quality=93)
