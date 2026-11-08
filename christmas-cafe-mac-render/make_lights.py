# Random "lights going off and on" effect (free, done in the render).
# Builds assets/lights_off.png (the still with the small warm bulbs near the window and on the tree removed)
# and assets/lights_alpha.mp4 (90s loop, gray = how much of the "off" plate shows; groups of bulbs fade off for 1.5-5s).
# Usage: python3 make_lights.py assets/still_1080.png
import sys, os, subprocess, numpy as np
from PIL import Image, ImageFilter
B=os.path.dirname(os.path.abspath(__file__)); A=B+"/assets/"
W,H=1920,1080
src=Image.open(sys.argv[1]).convert("RGB").resize((W,H),Image.LANCZOS)
im=np.asarray(src).astype(np.float32)/255
lum=im.max(axis=2)
L8=Image.fromarray((lum*255).astype(np.uint8))
opened=np.asarray(L8.filter(ImageFilter.MinFilter(9)).filter(ImageFilter.MaxFilter(9))).astype(np.float32)/255
tophat=lum-opened
m=((tophat>0.15)&(lum>0.55)&((im[:,:,0]-im[:,:,2])>0.12)).astype(np.float32)
zone=np.zeros((H,W),np.float32)
zone[0:700,0:1000]=1     # window: street, string lights, garland
zone[0:840,1630:1920]=1  # Christmas tree
zone[560:1080,0:300]=0   # lanterns on the window seat stay lit
zone[600:800,1560:1700]=0  # lantern by the fireplace stays lit
zone[360:640,330:510]=0    # street Christmas tree outside stays lit (Jose saw blur when it dimmed)
zone[0:840,1630:1920]=0    # cafe tree: twinkle comes from the Kling loop, keep it sharp
m*=zone
mk=Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(2.5))
mask=np.asarray(mk).astype(np.float32)/255
# "off" plate: each channel with bright specks removed (grey-scale opening), softly blurred
chans=[Image.fromarray((im[:,:,c]*255).astype(np.uint8)).filter(ImageFilter.MinFilter(9)).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(2)) for c in range(3)]
off=np.stack([np.asarray(c) for c in chans],2).astype(np.float32)/255
off=im*(1-mask[...,None])+np.minimum(off,im)*mask[...,None]
Image.fromarray((off*255).astype(np.uint8)).save(A+"lights_off.png")
# alpha video at half size (scaled up in the render)
w,h=960,540; FPS=12; DUR=90; N=FPS*DUR
mh=np.asarray(mk.resize((w,h),Image.BILINEAR)).astype(np.float32)/255
rng=np.random.default_rng(7); CS=20; gy,gx=(h+CS-1)//CS,(w+CS-1)//CS
sched=np.zeros((gy,gx,N),np.float32); t=np.arange(N)/FPS
for y in range(gy):
    for x in range(gx):
        s=rng.uniform(0,DUR)
        while s<DUR-1:
            d=rng.uniform(1.5,5.0); f=0.35
            sched[y,x]=np.maximum(sched[y,x],np.clip(np.minimum((t-s)/f,(s+d-t)/f),0,1))
            s+=d+rng.uniform(8,35)
p=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','gray','-s',f'{w}x{h}','-r',str(FPS),'-i','-',
  '-c:v','libx264','-crf','14','-pix_fmt','yuv420p',A+'lights_alpha.mp4'],stdin=subprocess.PIPE)
for k in range(N):
    g=np.kron(sched[:,:,k],np.ones((CS,CS),np.float32))[:h,:w]
    p.stdin.write((np.clip(mh*g,0,1)*255).astype(np.uint8).tobytes())
p.stdin.close(); p.wait(); print("ok")
