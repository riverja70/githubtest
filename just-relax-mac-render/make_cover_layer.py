# Builds assets/cover_layer_A.png: the Cover A text + left shade as a transparent 4K layer (opening = cover over the live loop).
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
B=os.path.dirname(os.path.abspath(__file__)); F=os.environ.get("FONTS","/mnt/project-files/scripts/fonts/")
k=2; W,H=1920*k,1080*k
L=Image.new("RGBA",(W,H),(0,0,0,0))
g=Image.new("L",(W,H),0); d=ImageDraw.Draw(g)
for x in range(1100*k): d.line([(x,0),(x,H)],fill=int(95*(1-x/(1100*k))**1.6))
L.paste(Image.new("RGBA",(W,H),(10,14,8,255)),(0,0),g)
def st(xy,txt,font,blur=10,alpha=170):
    sh=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(sh).text((xy[0]+4*k,xy[1]+5*k),txt,font=font,fill=(0,0,0,alpha))
    L.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur*k))); ImageDraw.Draw(L).text(xy,txt,font=font,fill="white")
serif=ImageFont.truetype(F+"PlayfairDisplay.ttf",150*k)
try: serif.set_variation_by_name("Bold")
except Exception: pass
small=ImageFont.truetype(F+"PlayfairDisplay.ttf",40*k)
try: small.set_variation_by_name("Bold")
except Exception: pass
st((110*k,120*k),"JUST RELAX",serif); st((110*k,285*k),"WITH JESUS",serif)
st((118*k,480*k),"Soaking Worship for Prayer & Rest",ImageFont.truetype(F+"GreatVibes-Regular.ttf",92*k))
d=ImageDraw.Draw(L); t="3 HOURS"; w=d.textlength(t,font=small); x,y=W-w-110*k,960*k
box=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(box).rounded_rectangle((x-28*k,y-16*k,x+w+28*k,y+62*k),10*k,fill=(0,0,0,135))
L.alpha_composite(box); ImageDraw.Draw(L).text((x,y),t,font=small,fill="white")
L.save(B+"/assets/cover_layer_A.png"); print("ok")
