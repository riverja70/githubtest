# THANKFUL 3 Hour - full-quality render for Jose's Mac (only needs ffmpeg + python3, no extra packages)
# Usage: python3 render.py            -> "THANKFUL 3 Hour (HQ).mp4" (CRF 18, AAC 192k, 48kHz)
# Same technique as Jesus Heals FINAL v4, with 3 scenes (one per hour, slow 30s crossfades):
#   hour 1 bench in the afternoon, hour 2 oak at sunset, hour 3 chapel path at dusk
#   + a slow light ramp inside each hour, an opening pull-back, a gentle close-up drift about every 9 min,
#   title 0-9s, 20 KJV verses every 540s from 60s, CTA cards at 180s + every 1620s, last 20s text-free,
#   music/ played in order and repeated until 3 hours, 5s crossfades, 48kHz.
# Options (env): CRF=18 PRESET=slow  RAMP=0 (no light ramp)  ZOOM=0 (no camera moments)  XD=30 (scene crossfade s)
#                TEST=600 (render only the first N seconds)  GOAL=1200 (short full-structure test video)
import os, sys, glob, subprocess
B=os.path.dirname(os.path.abspath(__file__)); A=B+"/assets/"
CRF=os.environ.get("CRF","18"); PRESET=os.environ.get("PRESET","slow")
OUT=sys.argv[1] if len(sys.argv)>1 else B+"/THANKFUL 3 Hour (HQ).mp4"
XF=5.0; XD=float(os.environ.get("XD","30")); GOAL=float(os.environ.get("GOAL",3*3600))
tracks=sorted(glob.glob(B+"/music/*.mp3")); assert tracks, "no music"
dur=lambda f: float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]))
D={t:dur(t) for t in tracks}
order=[]; tot=0
while tot<GOAL:
    t=tracks[len(order)%len(tracks)]; order.append(t); tot=sum(D[x] for x in order)-XF*(len(order)-1)
TOT=tot
print("%d tracks, total %.1f s (%.2f h)"%(len(order),TOT,TOT/3600))
# chapters for the YouTube description
with open(B+"/chapters.txt","w") as f:
    s=0
    for t in order:
        f.write("%d:%02d:%02d %s\n"%(s//3600,s%3600//60,s%60,os.path.basename(t)[3:-4])); s+=D[t]-XF
print(open(B+"/chapters.txt").read()); sys.stdout.flush()
TEST=float(os.environ.get("TEST","0")); LEN=min(TOT,TEST) if TEST else TOT
# 1) audio
AUD=B+f"/audio_192k_{len(order)}.m4a"
if not os.path.exists(AUD):
    args=['ffmpeg','-y','-v','error','-stats']
    for t in order: args+=['-i',t]
    fc=[f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,adeclick,acompressor=threshold=0.125:ratio=2.5:attack=300:release=2500:knee=6[a{k}]" for k in range(len(order))]
    prev="a0"
    for k in range(1,len(order)):
        fc.append(f"[{prev}][a{k}]acrossfade=d={XF}:c1=tri:c2=tri[x{k}]"); prev=f"x{k}"
    fc.append(f"[{prev}]volume=-4dB,afade=t=out:st={TOT-6:.2f}:d=6,aresample=48000[aout]")
    args+=['-filter_complex',';'.join(fc),'-map','[aout]','-t',f"{TOT:.2f}",'-c:a','aac','-b:a','192k','-ar','48000',AUD+".tmp.m4a"]
    subprocess.run(args,check=True); os.rename(AUD+".tmp.m4a",AUD)
# 2) video: 3 scenes with crossfades at 1/3 and 2/3
T1,T2=TOT/3,2*TOT/3
L=[T1+XD/2, (T2-T1)+XD, TOT-T2+XD/2]     # segment lengths (each includes its crossfade overlap)
args=['ffmpeg','-y','-v','error','-stats']
for h in (1,2,3): args+=['-stream_loop','-1','-i',B+f'/loops/hour{h}.mp4']
for h in (1,2,3): args+=['-loop','1','-framerate','24','-t',f"{L[h-1]:.2f}",'-i',A+f'ramp{h}.png']
# hover hook (HOOK=1, default): frame 1 is an exact copy of the YouTube cover, which melts into the moving scene over
# 1.0-3.0s (music from frame 1). The cover carries the title, so the title card and the opening pull-back are skipped.
HOOK=os.environ.get('HOOK','1')!='0'; COVER=os.environ.get('COVER',B+"/covers/THANKFUL cover (main, pop).jpg")
events=[(COVER,0,3.0,0,2.0)] if HOOK else [(A+"title.png",0,9,1.5,2)]
events+=[(A+f"v{i:02d}.png",60+540*i,25,2,2) for i in range(20)]
kinds=["sub","share","amen"]
events+=[(A+f"cta_{kinds[k%3]}.png",180+1620*k,8,1,1.5) for k in range(7)]
events=[e for e in events if e[1]+e[2]<=TOT-20]   # last 20s text-free (end screen)
for e in events: args+=['-loop','1','-framerate','24','-t',str(e[2]),'-i',e[0]]
AI=6+len(events); args+=['-i',AUD]
RAMP=os.environ.get('RAMP','1')!='0'
fc=[]
for h in range(3):
    fc.append(f"[{h}:v]scale=1920:1080:flags=lanczos,setsar=1,fps=24,format=yuv420p,trim=duration={L[h]:.2f},setpts=PTS-STARTPTS[s{h}]")
    if RAMP:
        fc.append(f"[{h+3}:v]format=rgba,fade=t=in:st=0:d={L[h]:.2f}:alpha=1[r{h}]")
        fc.append(f"[s{h}][r{h}]overlay=0:0:eof_action=pass,format=yuv420p,trim=duration={L[h]:.2f}[g{h}]")
    else:
        fc.append(f"[s{h}]null[g{h}]")
fc.append(f"[g0][g1]xfade=transition=fade:duration={XD}:offset={T1-XD/2:.2f}[x1]")
fc.append(f"[x1][g2]xfade=transition=fade:duration={XD}:offset={T2-XD/2:.2f}[b1]")
cur="b1"
# --- Bible page ripple (optional): loops/hour{h}_page.mp4 = Kling clip with the same first/last frame as the loop.
#     Only the Bible area (soft mask assets/bible_mask_h{h}.png) is laid over the running loop, so the wheat and mist
#     always move forward. Versions rotate: forward, backward (Bible only), slow 0.75x. Plays at every 2nd camera
#     moment of that hour, starting on a loop boundary (first frame = still = invisible cut).
def page_variants(h):
    f=B+f"/loops/hour{h}_page.mp4"; m=A+f"bible_mask_h{h}.png"
    if not (os.path.exists(f) and os.path.exists(m)): return []
    rev=B+f"/loops/hour{h}_page_rev.mp4"; slow=B+f"/loops/hour{h}_page_slow.mp4"
    enc=['-c:v','libx264','-crf','14','-preset','slow','-pix_fmt','yuv420p','-an']
    if not os.path.exists(rev): subprocess.run(['ffmpeg','-y','-v','error','-i',f,'-vf','reverse']+enc+[rev],check=True)
    if not os.path.exists(slow): subprocess.run(['ffmpeg','-y','-v','error','-i',f,'-vf','setpts=PTS/0.75,minterpolate=fps=24:mi_mode=blend']+enc+[slow],check=True)
    return [f,rev,slow]
PV={h:page_variants(h) for h in (1,2,3)}
PHASE=[0,T1-XD/2,T2-XD/2]; ins=[]
for i in range(0,20,2):
    s0=330+540*i
    if s0+46>TOT-30 or any(abs(s0+23-c)<XD+40 for c in (T1,T2)): continue
    h=0 if s0<T1 else (1 if s0<T2 else 2)
    if not PV[h+1]: continue
    clip=PV[h+1][sum(1 for x in ins if x[2]==h)%3]
    t=PHASE[h]+8*round((s0+12-PHASE[h])/8)   # starts near the beginning of the close-up hold (s0+14 .. s0+32)
    ins.append((clip,t,h))
nin=AI+1
for k,(clip,t,h) in enumerate(ins):
    d=dur(clip); args+=['-i',clip,'-loop','1','-framerate','24','-t',f"{d:.3f}",'-i',A+f"bible_mask_h{h+1}.png"]
    fc.append(f"[{nin}:v]scale=1920:1080:flags=lanczos,setsar=1,fps=24,trim=duration={d:.3f},format=rgba[pc{k}]")
    fc.append(f"[{nin+1}:v]format=gray,trim=duration={d:.3f}[pm{k}]")
    fc.append(f"[pc{k}][pm{k}]alphamerge,setpts=PTS-STARTPTS+{t:.4f}/TB[pg{k}]")
    fc.append(f"[{cur}][pg{k}]overlay=0:0:eof_action=pass,format=yuv420p[pi{k}]"); cur=f"pi{k}"; nin+=2
if ins: print("Bible page ripples at", ", ".join("%d:%02d:%02d (%s)"%(t//3600,t%3600//60,t%60,os.path.basename(c)) for c,t,_ in ins))
# --- gentle camera moments: slow pull-back over the first 40s, then every 9 min a slow drift into a close-up and back
if os.environ.get('ZOOM','1')!='0':
    T="(in/24)"
    def sm(a,b):  # smoothstep 0->1 between a and b
        u=f"clip(({T}-{a})/{b-a},0,1)"; return f"({u}*{u}*(3-2*{u}))"
    targets=[[(0.29,0.63),(0.49,0.60),(0.40,0.84),(0.70,0.47)],   # hour 1: Bible, lantern, basket + pumpkins, oaks
             [(0.70,0.69),(0.55,0.50),(0.62,0.83),(0.27,0.42)],   # hour 2: lantern + Bible, river valley, basket, sun
             [(0.62,0.57),(0.16,0.40),(0.62,0.30),(0.45,0.72)]]   # hour 3: candle + Bible, chapel, oak in mist, path
    zt=["0" if HOOK else "0.12*(1-"+sm(0,40)+")"]; fx=["0"]; fy=["0"]
    for i in range(20):
        s=330+540*i
        if s+46>TOT-30 or any(abs(s+23-c)<XD+40 for c in (T1,T2)): continue   # never during a scene crossfade
        h=0 if s<T1 else (1 if s<T2 else 2); tx,ty=targets[h][i%4]
        env=f"({sm(s,s+14)}-{sm(s+32,s+46)})"
        zt.append(f"0.20*{env}"); fx.append(f"{tx-0.5}*{env}"); fy.append(f"{ty-0.5}*{env}")
    Z="(1+"+"+".join(zt)+")"; FX="(0.5+"+"+".join(fx)+")"; FY="(0.5+"+"+".join(fy)+")"
    Lf=f"((W-W/{Z})*{FX})"; Tp=f"((H-H/{Z})*{FY})"; R=f"({Lf}+W/{Z})"; Bt=f"({Tp}+H/{Z})"
    fc.append(f"[{cur}]perspective=x0='{Lf}':y0='{Tp}':x1='{R}':y1='{Tp}':x2='{Lf}':y2='{Bt}':x3='{R}':y3='{Bt}':interpolation=cubic:sense=source:eval=frame[bz]")
    cur="bz"
for j,(fn,st,du,fi,fo) in enumerate(events):
    fades=(f"fade=t=in:st=0:d={fi}:alpha=1," if fi>0 else "")+f"fade=t=out:st={du-fo}:d={fo}:alpha=1"
    fc.append(f"[{j+6}:v]scale=1920:1080,setsar=1,format=rgba,{fades},setpts=PTS+{st}/TB[o{j}]")
    fc.append(f"[{cur}][o{j}]overlay=0:0:eof_action=pass[c{j}]"); cur=f"c{j}"
fc.append(f"[{cur}]format=yuv420p[vout]")
args+=['-filter_complex',';'.join(fc),'-map','[vout]','-map',f'{AI}:a','-t',f"{LEN:.2f}",
       '-c:v','libx264','-preset',PRESET,'-tune','film','-crf',CRF,'-g','48','-bf','2','-pix_fmt','yuv420p',
       '-profile:v','high','-c:a','copy','-movflags','+faststart',OUT]
subprocess.run(args,check=True)
print("DONE",OUT,os.path.getsize(OUT)//1_000_000,"MB")
