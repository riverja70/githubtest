# Builds assets/snow.mp4: a seamless 20 s loop of soft falling snow, only over the window glass (gray = flake opacity).
# It is overlaid as white snow at x=90, y=0 in render.py. Usage: python3 make_snow.py
import os, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFilter
B=os.path.dirname(os.path.abspath(__file__)); A=B+"/assets/"
X0,Y0,W,H=90,0,800,720          # crop box of the window area in the 1920x1080 frame
FPS=24; P=20; N=FPS*P; HS=H+40
# window glass mask (frame coords), feathered
m=Image.new("L",(1920,1080),0); d=ImageDraw.Draw(m)
d.polygon([(222,0),(640,0),(700,40),(762,130),(762,640),(560,648),(400,690),(222,700)],fill=255)   # main pane
d.polygon([(110,0),(176,0),(176,670),(110,670)],fill=200)                                         # narrow left pane
d.polygon([(790,150),(868,130),(868,590),(790,600)],fill=255)                                     # right pane
m=m.filter(ImageFilter.GaussianBlur(6)).crop((X0,Y0,X0+W,Y0+H)); mask=np.asarray(m).astype(np.float32)/255
rng=np.random.default_rng(11)
layers=[  # count, radius range, speed multiple k (px/s = k*HS/P), opacity, blur
  (260,(0.8,1.3),1,0.55,0.0),
  (120,(1.5,2.3),2,0.75,0.4),
  (28,(3.0,4.5),3,0.55,1.6)]
flakes=[]
for cnt,(r0,r1),k,op,bl in layers:
    for _ in range(cnt):
        flakes.append(dict(x=rng.uniform(0,W),y=rng.uniform(0,HS),r=rng.uniform(r0,r1),k=k,op=op*rng.uniform(0.7,1),bl=bl,
                           amp=rng.uniform(3,14)*k,ph=rng.uniform(0,2*np.pi),m=int(rng.integers(1,3))))
p=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','gray','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
  '-c:v','libx264','-crf','12','-pix_fmt','yuv420p',A+'snow.mp4'],stdin=subprocess.PIPE)
for f in range(N):
    t=f/FPS; layer_imgs={}
    for bl in sorted(set(fl['bl'] for fl in flakes)):
        im=Image.new("L",(W,H),0); dd=ImageDraw.Draw(im)
        for fl in flakes:
            if fl['bl']!=bl: continue
            y=(fl['y']+fl['k']*HS*t/P)%HS-20
            x=(fl['x']+fl['amp']*np.sin(2*np.pi*fl['m']*t/P+fl['ph']))%W
            r=fl['r']; v=int(255*fl['op'])
            dd.ellipse((x-r,y-r,x+r,y+r),fill=v)
        if bl>0: im=im.filter(ImageFilter.GaussianBlur(bl))
        layer_imgs[bl]=np.asarray(im).astype(np.float32)
    acc=np.maximum.reduce(list(layer_imgs.values()))*mask
    p.stdin.write(np.clip(acc,0,255).astype(np.uint8).tobytes())
p.stdin.close(); p.wait(); print("ok")
