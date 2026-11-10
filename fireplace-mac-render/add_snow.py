# Adds seamless falling snow (72s period) behind the window glass of the master loop.
# usage: python3 add_snow.py master_loop_72s.mp4 out.mp4 [density]
import sys, subprocess, numpy as np
src, out = sys.argv[1], sys.argv[2]; N = int(sys.argv[3]) if len(sys.argv) > 3 else 900
W, H, F, FPS = 1920, 1080, 1728, 24
X0, Y0, BW, BH = 140, 0, 1080, 520   # snow box covering all windows
rng = np.random.default_rng(7)
# window glass mask: rectangles AND bluish pixels (excludes wood frames, wreath, tree-light reflections)
f0 = subprocess.run(["ffmpeg","-nostdin","-loglevel","error","-i",src,"-frames:v","1","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
img = np.frombuffer(f0,np.uint8).reshape(H,W,3).astype(float)
rect = np.zeros((H,W),bool)
for x1,y1,x2,y2 in [(158,18,325,418),(360,52,618,420),(643,103,780,458),(1098,138,1202,492)]: rect[y1:y2,x1:x2]=True
r,g,b = img[...,0],img[...,1],img[...,2]
blue = np.clip((b - r - 4)/14, 0, 1)
mask = (rect*blue)
from PIL import Image, ImageFilter
mask = np.asarray(Image.fromarray((mask*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))).astype(float)/255
mbox = mask[Y0:Y0+BH, X0:X0+BW]
# flakes
x0 = rng.uniform(0,BW,N); y0 = rng.uniform(0,BH,N)
k = rng.integers(3,9,N)                     # whole wraps per 72s -> seamless
vy = k*BH/(F)                               # px per frame
size = rng.choice([0,1,2],N,p=[0.5,0.35,0.15])
amp = rng.uniform(4,16,N); m = rng.integers(1,5,N); ph = rng.uniform(0,2*np.pi,N)
alpha = rng.uniform(0.35,0.85,N)*np.array([0.7,0.9,1.0])[size]
def kern(s):
    rr=[1.0,1.6,2.4][s]; R=int(np.ceil(rr*2.5)); yy,xx=np.mgrid[-R:R+1,-R:R+1]; return R,np.exp(-(xx**2+yy**2)/(2*rr*rr))
K=[kern(s) for s in range(3)]
dec = subprocess.Popen(["ffmpeg","-nostdin","-loglevel","error","-i",src,"-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg","-nostdin","-loglevel","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","slow","-crf","14","-pix_fmt","yuv420p",out],stdin=subprocess.PIPE)
pad=8
for t in range(F):
    fr = np.frombuffer(dec.stdout.read(W*H*3),np.uint8).reshape(H,W,3).astype(np.float32)
    layer = np.zeros((BH+2*pad,BW+2*pad),np.float32)
    ys = (y0 + vy*t) % BH; xs = (x0 + amp*np.sin(2*np.pi*m*t/F + ph)) % BW
    for i in range(N):
        R,kk = K[size[i]]; cx=int(xs[i])+pad; cy=int(ys[i])+pad
        layer[cy-R:cy+R+1, cx-R:cx+R+1] += alpha[i]*kk
    a = np.clip(layer[pad:pad+BH,pad:pad+BW],0,1)*mbox
    box = fr[Y0:Y0+BH,X0:X0+BW]
    snow = np.array([232,238,250],np.float32)
    fr[Y0:Y0+BH,X0:X0+BW] = box*(1-a[...,None]) + snow*a[...,None]
    enc.stdin.write(fr.clip(0,255).astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait(); dec.wait()
