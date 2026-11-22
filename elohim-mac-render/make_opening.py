# Builds loops/opening_A.mp4 and opening_B.mp4 (8s, 1920x1080 24fps) for the hover hook:
# frame 1 = exact cover; title melts away 1-3s while the Veo clip (same 4K still) comes alive with a slow push-in;
# dissolves into the seamless harp loop 5.5-8s (frames at 8s = loop itself, invisible handoff).
import subprocess, numpy as np
from PIL import Image
W,H,FPS,N=1920,1080,24,192
def frames(path,n):
    raw=subprocess.run(["ffmpeg","-nostdin","-loglevel","error","-i",path,"-vf","scale=1920:1080:flags=lanczos,fps=24","-frames:v",str(n),"-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
    return np.frombuffer(raw,np.uint8).reshape(-1,H,W,3)
veo=frames("loops/veo_open.mp4",N); loop=frames("loops/master.mp4",N)
sm=lambda u:(lambda c:c*c*(3-2*c))(min(1,max(0,u)))
import sys
for tag in (sys.argv[1] if len(sys.argv)>1 else "ABC"):
    cov=np.asarray(Image.open(f"covers/cover_{tag}.jpg").convert("RGB").resize((W,H))).astype(np.float32)
    enc=subprocess.Popen(["ffmpeg","-nostdin","-loglevel","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","slow","-crf","14","-pix_fmt","yuv420p",f"loops/opening_{tag}.mp4"],stdin=subprocess.PIPE)
    for i in range(N):
        t=i/FPS; v=veo[min(i,len(veo)-1)].astype(np.float32)
        w=sm((t-1)/2); fr=cov*(1-w)+v*w
        r=sm((t-5.5)/2.5); fr=fr*(1-r)+loop[i].astype(np.float32)*r
        enc.stdin.write(fr.clip(0,255).astype(np.uint8).tobytes())
    enc.stdin.close(); enc.wait()
print("opening OK")
