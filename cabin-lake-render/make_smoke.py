# Builds assets/smoke.mp4: a seamless 20 s loop of soft chimney smoke rising from the cabin chimney (gray = smoke opacity).
# Overlaid as pale blue-gray smoke under the snow layer in render.py. Usage: python3 make_smoke.py
import os, subprocess, numpy as np
B=os.path.dirname(os.path.abspath(__file__)); A=B+"/assets/"
W,H,FPS,P=1920,1080,24,20; N=FPS*P
CHIMNEYS=[(1404,252,1.25)]   # chimney top x, y (1080p frame), strength
rng=np.random.default_rng(7)
parts=[]
for cx,cy,k in CHIMNEYS:
    n=int(60*k)
    for i in range(n):
        parts.append(dict(cx=cx,cy=cy,k=k,b=P*i/n+rng.uniform(0,P/n),life=rng.uniform(6.5,9.0),
                          vy=rng.uniform(17,24)*k,dx=rng.uniform(4,9),ph=rng.uniform(0,2*np.pi),
                          wob=rng.uniform(3,7),r0=rng.uniform(4,7),r1=rng.uniform(26,42)*k,op=rng.uniform(0.30,0.45)))
yy,xx=np.mgrid[0:H,0:W]
p=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','gray','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
  '-c:v','libx264','-crf','14','-pix_fmt','yuv420p',A+'smoke.mp4'],stdin=subprocess.PIPE)
for f in range(N):
    t=f/FPS; acc=np.zeros((H,W),np.float32)
    for q in parts:
        age=(t-q['b'])%P
        if age>q['life']: continue
        u=age/q['life']
        y=q['cy']-q['vy']*age
        x=q['cx']+q['dx']*age+q['wob']*np.sin(1.3*age+q['ph'])*u*3
        r=q['r0']+(q['r1']-q['r0'])*u**0.8
        a=q['op']*min(1,age/0.8)*(1-u)**1.6
        x0,x1=int(max(0,x-3*r)),int(min(W,x+3*r)); y0,y1=int(max(0,y-3*r)),int(min(H,y+3*r))
        if x1<=x0 or y1<=y0: continue
        g=a*np.exp(-(((xx[y0:y1,x0:x1]-x)**2+(yy[y0:y1,x0:x1]-y)**2)/(2*r*r)))
        sub=acc[y0:y1,x0:x1]; acc[y0:y1,x0:x1]=1-(1-sub)*(1-g)
    p.stdin.write(np.clip(acc*255,0,255).astype(np.uint8).tobytes())
p.stdin.close(); p.wait(); print("ok")
