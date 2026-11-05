# Builds a seamless 60s RGB gain video for the window city lights: gentle twinkle, random on/off, a few color-changing lights.
import cv2, numpy as np, subprocess, sys
img=cv2.imread(sys.argv[1]); m=cv2.imread(sys.argv[2],0)/255.; OUT=sys.argv[3]
g=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY).astype(np.float32); H,W=g.shape
top=g-cv2.GaussianBlur(g,(0,0),6); yy=np.arange(H)[:,None]
opn=cv2.morphologyEx(g,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9)))
cand=(top>18)&(g>110)&(m>0.95)&(yy>350)&(yy<600)&(cv2.GaussianBlur(g,(0,0),8)<115)
pk=cand&(g>=cv2.dilate(g,np.ones((5,5),np.uint8)))
ys,xs=np.nonzero(pk); n=len(xs); print("lights",n)
ratio=np.clip(opn[ys,xs]/np.maximum(g[ys,xs],1),0.08,1)
rng=np.random.default_rng(7)
FPS,SEC=24,60; N=FPS*SEC; t=np.arange(N)/N
kind=rng.choice(4,n,p=[0.72,0.17,0.07,0.04])   # 0 twinkle, 1 on/off, 2 slow breathe, 3 color change
def per(k,ph): return np.sin(2*np.pi*(k*t[:,None]+ph))
gain=np.ones((N,n,3),np.float32)
k1=rng.integers(3,40,n); k2=rng.integers(41,90,n); ph=rng.random((2,n))
tw=1-0.10*(0.5+0.5*per(k1,ph[0]))-0.06*(0.5+0.5*per(k2,ph[1]))
gain*=tw[...,None]
# on/off: each light has 1-3 off periods per minute with soft 0.25s edges
for i in np.nonzero(kind==1)[0]:
    s=np.ones(N,np.float32)
    for _ in range(rng.integers(1,4)):
        st=rng.integers(0,N); ln=rng.integers(FPS*3,FPS*14)
        idx=(st+np.arange(ln))%N; s[idx]=0.0
    s=cv2.GaussianBlur(np.tile(s,3)[None,:],(0,0),(FPS*0.12,0.001))[0][N:2*N] if False else s
    k=np.exp(-0.5*(np.arange(-12,13)/3.0)**2); k/=k.sum()
    s=np.convolve(np.concatenate([s[-12:],s,s[:12]]),k,'valid')
    gain[:,i,:]*=s[:,None]
for i in np.nonzero(kind==2)[0]:
    gain[:,i,:]*=(0.65+0.35*(0.5+0.5*per(rng.integers(1,4),rng.random())[:,0]))[:,None]
# colour change: multiply channels (BGR) through warm -> cool -> magenta, smooth, periodic
for i in np.nonzero(kind==3)[0]:
    k=rng.integers(1,3); p=rng.random()
    a=2*np.pi*(k*t+p)
    gain[:,i,0]*=0.55+0.45*(0.5+0.5*np.sin(a))
    gain[:,i,1]*=0.55+0.45*(0.5+0.5*np.sin(a+2.1))
    gain[:,i,2]*=0.55+0.45*(0.5+0.5*np.sin(a+4.2))
# splat: soft disc radius ~2.5px
R=5; yk,xk=np.mgrid[-R:R+1,-R:R+1]; spl=np.exp(-(xk**2+yk**2)/(2*1.8**2)).astype(np.float32)
x0,x1=max(0,xs.min()-R),min(W,xs.max()+R+1); y0,y1=max(0,ys.min()-R),min(H,ys.max()+R+1)
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
   '-c:v','libx264','-pix_fmt','yuv444p','-crf','10','-preset','medium',OUT],stdin=p if False else subprocess.PIPE)
full=np.full((H,W,3),255,np.uint8)
for f in range(N):
    acc=np.zeros((y1-y0,x1-x0,3),np.float32); wt=np.zeros((y1-y0,x1-x0,1),np.float32)
    d=(1-gain[f])*(1-ratio)[:,None]  # darken only down to the building behind the light
    for (x,y,dd) in zip(xs,ys,d):
        if dd.max()<0.01: continue
        ya,xa=y-R-y0,x-R-x0
        acc[ya:ya+2*R+1,xa:xa+2*R+1]+=spl[...,None]*dd
    fr=full.copy(); fr[y0:y1,x0:x1]=np.clip(255*(1-np.minimum(acc,0.92)),0,255).astype(np.uint8)
    p.stdin.write(fr.tobytes())
p.stdin.close(); p.wait()
