# Koi overlay: soft colored koi + shadows swimming randomly in the pool, seamless period T.
# Usage: python3 koi.py <base_loop.mp4|still.png> <out.mp4> [height=1080] [seconds=20] [period=120]
# Output is the base (looped) with koi composited; seamless every <period> seconds.
import sys, math, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFilter
src, out = sys.argv[1], sys.argv[2]
H = int(sys.argv[3]) if len(sys.argv) > 3 else 1080
SECS = float(sys.argv[4]) if len(sys.argv) > 4 else 20
T = float(sys.argv[5]) if len(sys.argv) > 5 else 237.5
W = H * 16 // 9; FPS = 24; S = W / 1280.0
rng = np.random.default_rng(7)

# open-water polygon (1280-wide coords), fish stay inside
POLY = [(190,445),(380,405),(600,398),(850,398),(868,450),(872,520),(760,548),(560,556),(360,552),(240,525),(175,480)]
def inside(x, y):
    c = False; n = len(POLY)
    for i in range(n):
        x1,y1 = POLY[i]; x2,y2 = POLY[(i+1)%n]
        if (y1 > y) != (y2 > y) and x < (x2-x1)*(y-y1)/(y2-y1)+x1: c = not c
    return c
def margin_ok(x, y, m=14):
    return all(inside(x+dx, y+dy) for dx,dy in [(0,0),(m,0),(-m,0),(0,m*.6),(0,-m*.6)])

# periodic random paths
def make_path():
    while True:
        cx, cy = rng.uniform(300,760), rng.uniform(440,520)
        ks = [1,2,3]
        ax = [rng.uniform(70,150)/k**1.5 for k in ks]; ay = [rng.uniform(10,30)/k**1.5 for k in ks]
        px = rng.uniform(0,2*math.pi,3); py = rng.uniform(0,2*math.pi,3)
        def f(t, cx=cx, cy=cy, ax=ax, ay=ay, px=px, py=py):
            w = 2*math.pi*t/T
            return (cx + sum(a*math.sin(k*w+p) for a,k,p in zip(ax,ks,px)),
                    cy + sum(a*math.sin(k*w+p) for a,k,p in zip(ay,ks,py)))
        if all(margin_ok(*f(t)) for t in np.linspace(0, T, 400)): return f

PAL = [((245,240,232),(232,96,30)), ((236,120,36),(250,236,220)), ((240,226,206),(205,40,32)),
       ((232,170,60),(240,232,215)), ((250,248,240),(30,30,30))]

def fish_sprite(base, patch, phase, L=200):
    """koi pointing +x, length L (supersampled), tail bend by phase."""
    img = Image.new("RGBA", (int(L*1.5), int(L*0.7)), (0,0,0,0))
    cxo, cyo = int(L*0.25), img.height//2
    N = 40; top=[]; bot=[]
    for i in range(N+1):
        s = i/N                     # 0 head .. 1 tail base
        x = cxo + L*(1-s)*0.85
        y = cyo + 0.06*L*math.sin(2*math.pi*0.7*s - phase)*s**2.0
        w = 0.13*L*math.sin(math.pi*min(1,(s*0.92+0.06)))**0.8*(1-0.55*s)
        top.append((x, y-w)); bot.append((x, y+w))
    body = top + bot[::-1]
    mask = Image.new("L", img.size, 0); md = ImageDraw.Draw(mask); md.polygon(body, fill=255)
    # tail fan
    tx, ty = top[-1][0], (top[-1][1]+bot[-1][1])/2
    sw = 0.09*L*math.sin(-phase+0.7*2*math.pi)
    tail = [(tx+4,ty-3),(tx-0.22*L, ty-0.13*L+sw*0.4),(tx-0.16*L, ty+sw*0.5),(tx-0.22*L, ty+0.13*L+sw*0.4),(tx+4,ty+3)]
    fins = Image.new("L", img.size, 0); fd = ImageDraw.Draw(fins); fd.polygon(tail, fill=170)
    hx = top[int(N*0.25)]
    fd.polygon([(hx[0],hx[1]+2),(hx[0]-0.12*L,hx[1]-0.09*L),(hx[0]-0.05*L,hx[1]+4)], fill=120)
    hb = bot[int(N*0.25)]
    fd.polygon([(hb[0],hb[1]-2),(hb[0]-0.12*L,hb[1]+0.09*L),(hb[0]-0.05*L,hb[1]-4)], fill=120)
    col = Image.new("RGBA", img.size, base+(255,))
    pd = ImageDraw.Draw(col)
    r2 = np.random.default_rng(hash(base+patch) % 999)
    for _ in range(3):
        s = r2.uniform(0.05, 0.75); x = cxo + L*(1-s)*0.85
        pd.ellipse((x-0.12*L, cyo-0.09*L, x+0.08*L, cyo+0.07*L), fill=patch+(255,))
    a = Image.fromarray(np.maximum(np.array(mask), np.array(fins)).astype(np.uint8))
    col.putalpha(a)
    return col.filter(ImageFilter.GaussianBlur(L*0.028))

PHASES = 48
fish = []
for i in range(5):
    base, patch = PAL[i % len(PAL)]
    spr = [fish_sprite(base, patch, 2*math.pi*k/PHASES) for k in range(PHASES)]
    fish.append(dict(path=make_path(), spr=spr, size=rng.uniform(0.85,1.15), wig=round(rng.uniform(0.30,0.45)*237.5), off=rng.uniform(0,T)))

WATER = np.array([62,72,52], np.float32)
def koi_layer(t):
    lay = Image.new("RGBA", (W, H), (0,0,0,0)); sh = Image.new("RGBA", (W, H), (0,0,0,0))
    for f in fish:
        tt = (t + f["off"]) % T
        x, y = f["path"](tt); x2, y2 = f["path"]((tt+0.6) % T)
        ang = math.degrees(math.atan2(-(y2-y), x2-x))
        
        ph = int(tt/T*f["wig"]*PHASES) % PHASES
        depth = (y-398)/(556-398)            # 0 far .. 1 near
        Lpx = (34 + 28*depth) * f["size"] * S   # fish length in output px
        spr = f["spr"][ph]
        k = Lpx/200
        s = spr.resize((max(2,int(spr.width*k)), max(2,int(spr.height*k))), Image.LANCZOS)
        s = s.rotate(ang, resample=Image.BICUBIC, expand=True)
        arr = np.array(s).astype(np.float32)
        arr[...,:3] = arr[...,:3]*0.58 + WATER*0.42      # seen through water
        arr[...,3] *= 0.42 + 0.16*depth
        s2 = Image.fromarray(arr.clip(0,255).astype(np.uint8))
        X, Y = int(x*S - s2.width/2), int(y*S - s2.height/2)
        shadow = Image.new("RGBA", s2.size, (8,12,6,0)); shadow.putalpha(Image.fromarray((arr[...,3]*0.55).astype(np.uint8)))
        sh.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(3*S)), (X+int(5*S), Y+int(9*S)))
        lay.alpha_composite(s2, (X, Y))
    sh.alpha_composite(lay)
    return sh

# soft water mask so koi fade at the edges
wm = Image.new("L", (W, H), 0); ImageDraw.Draw(wm).polygon([(x*S, y*S) for x,y in POLY], fill=255)
wm = np.array(wm.filter(ImageFilter.GaussianBlur(10*S))).astype(np.float32)/255

is_img = src.lower().endswith((".png",".jpg",".jpeg"))
if is_img:
    base_still = np.array(Image.open(src).convert("RGB").resize((W,H), Image.LANCZOS)).astype(np.float32)
    reader = None
else:
    reader = subprocess.Popen(["ffmpeg","-v","error","-stream_loop","-1","-i",src,"-vf",f"scale={W}:{H}:flags=lanczos,fps={FPS}",
                               "-f","rawvideo","-pix_fmt","rgb24","-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
                        "-c:v","libx264","-preset","medium","-crf","16","-pix_fmt","yuv420p",out], stdin=subprocess.PIPE)
yy = np.arange(H)[:,None].astype(np.float32)
for n in range(int(SECS*FPS)):
    t = n/FPS
    if is_img: frame = base_still
    else: frame = np.frombuffer(reader.stdout.read(W*H*3), np.uint8).reshape(H,W,3).astype(np.float32)
    k = np.array(koi_layer(t)).astype(np.float32)
    # gentle refraction wobble on the koi layer
    dx = (np.sin(yy/(7*S) + t*2.1)*1.2*S).astype(np.int32)
    k = np.take_along_axis(k, (np.clip(np.arange(W)[None,:]+dx,0,W-1))[...,None].repeat(4,2), axis=1)
    a = (k[...,3:4]/255)*wm[...,None]
    frame = frame*(1-a) + k[...,:3]*a
    enc.stdin.write(frame.clip(0,255).astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait()
if reader: reader.kill()
