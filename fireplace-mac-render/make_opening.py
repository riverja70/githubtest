# Builds loops/opening.mp4 (12s, 1920x1080 24fps): frame 1 = exact cover; title melts away 1-3s; slow push-in on the
# snowy cabin with falling snow; dissolves into the room 8-11s; frames 11-12s = room loop itself (invisible handoff).
import subprocess, numpy as np
from PIL import Image
W,H,FPS,N=1920,1080,24,288
cov=np.asarray(Image.open("covers/cover_main.jpg").convert("RGB")).astype(np.float32)
clean=Image.open("covers/outB_clean_3840.png").convert("RGB")
room=subprocess.run(["ffmpeg","-nostdin","-loglevel","error","-i","loops/master_72s.mp4","-t","12","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
room=np.frombuffer(room,np.uint8).reshape(-1,H,W,3)
sm=lambda u: (lambda c: c*c*(3-2*c))(min(1,max(0,u)))
rng=np.random.default_rng(3); M=500
x0=rng.uniform(0,W,M); y0=rng.uniform(0,H,M); vy=rng.uniform(1.2,3.5,M); sz=rng.choice([1.0,1.8,3.0],M,p=[.5,.35,.15]); al=rng.uniform(.35,.8,M)
amp=rng.uniform(5,20,M); ph=rng.uniform(0,6.28,M)
yy,xx=np.mgrid[-10:11,-10:11]
enc=subprocess.Popen(["ffmpeg","-nostdin","-loglevel","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","slow","-crf","14","-pix_fmt","yuv420p","loops/opening.mp4"],stdin=subprocess.PIPE)
cx,cy=0.55,0.62
for i in range(N):
    t=i/FPS
    z=1+0.12*sm((t-3)/9)
    cw,ch=3840/z,2160/z; L=(3840-cw)*cx; T=(2160-ch)*cy
    ext=np.asarray(clean.resize((W,H),Image.LANCZOS,box=(L,T,L+cw,T+ch))).astype(np.float32)
    snow=np.zeros((H+40,W+40),np.float32); a_s=sm((t-0.5)/1.5)
    if a_s>0:
        ys=(y0+vy*i)%H; xs=(x0+amp*np.sin(i/40+ph))%W
        for k in range(M):
            r=sz[k]; R=int(r*2.5)+1; kk=np.exp(-(xx[10-R:10+R+1,10-R:10+R+1]**2+yy[10-R:10+R+1,10-R:10+R+1]**2)/(2*r*r))
            X=int(xs[k])+20; Y=int(ys[k])+20; snow[Y-R:Y+R+1,X-R:X+R+1]+=al[k]*kk
        a=np.clip(snow[20:20+H,20:20+W],0,1)[...,None]*a_s
        ext=ext*(1-a)+np.array([235,240,250],np.float32)*a
    w=sm((t-1)/2)
    fr=cov*(1-w)+ext*w
    rmix=sm((t-8)/3)
    fr=fr*(1-rmix)+room[i].astype(np.float32)*rmix
    enc.stdin.write(fr.clip(0,255).astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait()
