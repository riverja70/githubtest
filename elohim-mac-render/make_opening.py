# Builds loops/opening_<COVER>.mp4 (8s, 24fps, RES=2160 -> 3840x2160 by default) for the hover hook:
# frame 1 = exact cover; title melts away 1-3s while the Veo clip (same 4K still) comes alive with a slow push-in;
# dissolves into the seamless harp loop 5.5-8s (frames at 8s = loop itself, invisible handoff). Streams frames (low RAM).
import subprocess, sys, os, numpy as np
from PIL import Image
RES=int(os.environ.get("RES","2160")); H=RES; W=RES*16//9; FPS,N=24,192
def reader(path):
    p=subprocess.Popen(["ffmpeg","-nostdin","-loglevel","error","-i",path,"-vf",f"scale={W}:{H}:flags=lanczos,fps=24","-frames:v",str(N),"-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
    last=None
    while True:
        b=p.stdout.read(W*H*3)
        if len(b)<W*H*3: break
        last=np.frombuffer(b,np.uint8).reshape(H,W,3); yield last
    while True: yield last
sm=lambda u:(lambda c:c*c*(3-2*c))(min(1,max(0,u)))
for tag in (sys.argv[1] if len(sys.argv)>1 else "C"):
    cov=np.asarray(Image.open(f"covers/cover_{tag}.jpg").convert("RGB").resize((W,H),Image.LANCZOS)).astype(np.float32)
    veo=reader("loops/veo_open.mp4"); loop=reader("loops/master.mp4")
    enc=subprocess.Popen(["ffmpeg","-nostdin","-loglevel","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","slow","-crf","14","-pix_fmt","yuv420p",f"loops/opening_{tag}.mp4"],stdin=subprocess.PIPE)
    for i in range(N):
        t=i/FPS; v=next(veo).astype(np.float32); l=next(loop)
        w=sm((t-1)/2); fr=cov*(1-w)+v*w
        r=sm((t-5.5)/2.5); fr=fr*(1-r)+l.astype(np.float32)*r
        enc.stdin.write(fr.clip(0,255).astype(np.uint8).tobytes())
    enc.stdin.close(); enc.wait()
print("opening OK", W, H)
