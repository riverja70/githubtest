# CHRISTMAS FIREPLACE 3 Hour - full-quality render for Jose's Mac (needs only ffmpeg + python3, no extra packages)
# Usage: caffeinate -dimsu python3 render.py      -> "Christmas Fireplace 3 Hour (HQ).mp4"
# Timeline: opening.mp4 (0-12s: exact cover -> outside cabin in the snow -> dissolves into the room, music from frame 1)
#   then the room loop (loops/master_72s.mp4: fire, candles, snow, steam, tree lights, gentle Bible page breath),
#   a gentle close-up drift and back about every 9 min, 20 KJV verses every 540s from 60s (25s each),
#   CTA cards at 180s + every 1620s, last 20s text-free (end screen).
# Audio: music/ in name order (all first takes, then all second takes, then again) with 5s crossfades + soft fire bed
#   (fire/fire.mp3, level locked by Jose 2026-11-10: about -55 LUFS, peaks -34 dB), 48kHz AAC 192k.
# Options (env): CRF=19 PRESET=slow ZOOM=0 (no camera moments) TEST=600 (first N seconds only) GOAL=10800
import os, sys, glob, subprocess
B=os.path.dirname(os.path.abspath(__file__)); A=B+"/assets/"
CRF=os.environ.get("CRF","19"); PRESET=os.environ.get("PRESET","slow")
OUT=sys.argv[1] if len(sys.argv)>1 else B+"/Christmas Fireplace 3 Hour (HQ).mp4"
XF=5.0; GOAL=float(os.environ.get("GOAL",3*3600))
# 0) download the music once (PromptEdit public links in music_list.txt)
os.makedirs(B+"/music",exist_ok=True)
for line in open(B+"/music_list.txt"):
    if not line.strip(): continue
    k,name,url=line.rstrip("\n").split("|"); fn=B+f"/music/{k} {name}.mp3"
    if not os.path.exists(fn):
        print("downloading",k,name); subprocess.run(["curl","-fsSL","--retry","3","-o",fn+".part",url],check=True); os.rename(fn+".part",fn)
tracks=sorted(glob.glob(B+"/music/*.mp3"), key=lambda f:(os.path.basename(f)[2], os.path.basename(f)[:2]))  # 01a..24a, 01b..24b
dur=lambda f: float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]))
D={t:dur(t) for t in tracks}
order=[]; tot=0
while tot<GOAL:
    t=tracks[len(order)%len(tracks)]; order.append(t); tot=sum(D[x] for x in order)-XF*(len(order)-1)
TOT=tot; print("%d tracks, total %.1f s (%.2f h)"%(len(order),TOT,TOT/3600))
with open(B+"/chapters.txt","w") as f:
    s=0
    for t in order:
        f.write("%d:%02d:%02d %s\n"%(s//3600,s%3600//60,s%60,os.path.basename(t)[4:-4])); s+=D[t]-XF
print(open(B+"/chapters.txt").read()); sys.stdout.flush()
TEST=float(os.environ.get("TEST","0")); LEN=min(TOT,TEST) if TEST else TOT
# 1) audio: music chain + fire bed
AUD=B+f"/audio_192k_{len(order)}.m4a"
if not os.path.exists(AUD):
    args=['ffmpeg','-y','-v','error','-stats']
    for t in order: args+=['-i',t]
    args+=['-stream_loop','-1','-i',B+'/fire/fire.mp3']
    n=len(order)
    fc=[f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,adeclick,acompressor=threshold=0.125:ratio=2.5:attack=300:release=2500:knee=6[a{k}]" for k in range(n)]
    prev="a0"
    for k in range(1,n): fc.append(f"[{prev}][a{k}]acrossfade=d={XF}:c1=tri:c2=tri[x{k}]"); prev=f"x{k}"
    fc.append(f"[{prev}]volume=-2dB[mus]")
    fc.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,volume=24dB,lowpass=f=5000,alimiter=limit=0.0625:attack=0.5:release=80:level=false,volume=-11dB,atrim=duration={TOT:.2f}[fire]")
    fc.append(f"[mus][fire]amix=inputs=2:normalize=0:duration=first,afade=t=out:st={TOT-6:.2f}:d=6,aresample=48000[aout]")
    args+=['-filter_complex',';'.join(fc),'-map','[aout]','-t',f"{TOT:.2f}",'-c:a','aac','-b:a','192k','-ar','48000',AUD+".tmp.m4a"]
    subprocess.run(args,check=True); os.rename(AUD+".tmp.m4a",AUD)
# 2) video
args=['ffmpeg','-y','-v','error','-stats','-stream_loop','-1','-i',B+'/loops/master_72s.mp4','-i',B+'/loops/opening.mp4']
events=[(A+f"v{i:02d}.png",60+540*i,25,2,2) for i in range(20)]
kinds=["sub","share","amen"]; events+=[(A+f"cta_{kinds[k%3]}.png",180+1620*k,8,1,1.5) for k in range(7)]
events=[e for e in events if e[1]+e[2]<=TOT-20]
for e in events: args+=['-loop','1','-framerate','24','-t',str(e[2]),'-i',e[0]]
AI=2+len(events); args+=['-i',AUD]
fc=["[0:v]fps=24,setsar=1,format=yuv420p[base]","[1:v]fps=24,setsar=1,format=yuv420p[op]","[base][op]overlay=0:0:eof_action=pass[b0]"]
cur="b0"
if os.environ.get('ZOOM','1')!='0':
    T="(in/24)"
    def sm(a,b):
        u=f"clip(({T}-{a})/{b-a},0,1)"; return f"({u}*{u}*(3-2*{u}))"
    targets=[(0.42,0.72),(0.80,0.45),(0.27,0.24),(0.50,0.33)]   # Bible, fire + poinsettias, snowy window, tree
    zt=["0"]; fx=["0"]; fy=["0"]
    for i in range(20):
        s=330+540*i
        if s+46>TOT-30: continue
        tx,ty=targets[i%4]; env=f"({sm(s,s+14)}-{sm(s+32,s+46)})"
        zt.append(f"0.18*{env}"); fx.append(f"{tx-0.5}*{env}"); fy.append(f"{ty-0.5}*{env}")
    Z="(1+"+"+".join(zt)+")"; FX="(0.5+"+"+".join(fx)+")"; FY="(0.5+"+"+".join(fy)+")"
    Lf=f"((W-W/{Z})*{FX})"; Tp=f"((H-H/{Z})*{FY})"; R=f"({Lf}+W/{Z})"; Bt=f"({Tp}+H/{Z})"
    fc.append(f"[{cur}]perspective=x0='{Lf}':y0='{Tp}':x1='{R}':y1='{Tp}':x2='{Lf}':y2='{Bt}':x3='{R}':y3='{Bt}':interpolation=cubic:sense=source:eval=frame[bz]"); cur="bz"
for j,(fn,st,du,fi,fo) in enumerate(events):
    fades=(f"fade=t=in:st=0:d={fi}:alpha=1," if fi>0 else "")+f"fade=t=out:st={du-fo}:d={fo}:alpha=1"
    fc.append(f"[{j+2}:v]scale=1920:1080,setsar=1,format=rgba,{fades},setpts=PTS+{st}/TB[o{j}]")
    fc.append(f"[{cur}][o{j}]overlay=0:0:eof_action=pass[c{j}]"); cur=f"c{j}"
fc.append(f"[{cur}]format=yuv420p[vout]")
args+=['-filter_complex',';'.join(fc),'-map','[vout]','-map',f'{AI}:a','-t',f"{LEN:.2f}",
       '-c:v','libx264','-preset',PRESET,'-tune','film','-crf',CRF,'-g','48','-bf','2','-pix_fmt','yuv420p',
       '-profile:v','high','-c:a','copy','-movflags','+faststart',OUT]
subprocess.run(args,check=True)
print("DONE",OUT,os.path.getsize(OUT)//1_000_000,"MB")
