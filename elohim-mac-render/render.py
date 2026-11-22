# ELOHIM harp 3 Hour - full-quality render for Jose's Mac (needs only ffmpeg + python3, no extra packages)
# Usage: caffeinate -dimsu python3 render.py      -> "ELOHIM Harp 3 Hour (HQ).mp4"
# Timeline: loops/opening_<COVER>.mp4 (0-8s: exact cover -> title melts away -> scene comes alive -> into the loop),
#   then the seamless King David harp loop (loops/master.mp4), a gentle slow close-up and back about every 9 min,
#   20 KJV verses every 540s from 60s (25s each), small CTA cards at 180s + every 1620s, last 20s text-free.
# Audio: music_list.txt in order (6 ElevenLabs + 28 Suno harp tracks), then repeats from the top until 3h,
#   5s crossfades, per-track linear gain to about -20 LUFS (ElevenLabs tracks also get slow leveling for swells),
#   gentle compressor, final limiter, 48kHz AAC 192k. Writes chapters.txt.
# Second half: slow 12s dissolve (at a track change near the middle) into the palace hall loop (loops/hall.mp4).
# Opening minute (Winning Long-Video Formula): if assets/intro_voice.mp3 exists, Adam reads one KJV verse + a short prayer
#   from 3s while the music dips 10 dB, then the music comes back up.
# Options (env): COVER=C (default; or A, B)  SWITCH=<sec>  RES=2160 (4K default; 1080 = HD) CRF=19 PRESET=medium ZOOM=0 (no close-ups) TEST=600 (first N seconds) GOAL=10800
import os, sys, glob, subprocess
B=os.path.dirname(os.path.abspath(__file__)); A=B+"/assets/"
CRF=os.environ.get("CRF","19"); PRESET=os.environ.get("PRESET","medium"); COVER=os.environ.get("COVER","C")
RES=int(os.environ.get("RES","2160")); VH=RES; VW=RES*16//9   # 4K by default (RES=1080 for a quick HD copy)
OUT=sys.argv[1] if len(sys.argv)>1 else B+"/ELOHIM Harp 3 Hour (HQ).mp4"
XF=5.0; GOAL=float(os.environ.get("GOAL",3*3600))
os.makedirs(B+"/music",exist_ok=True)
ROWS=[]
for line in open(B+"/music_list.txt"):
    if not line.strip(): continue
    k,name,url,ss,gain,mode=line.rstrip("\n").split("|"); fn=B+f"/music/{k} {name}.mp3"
    if not os.path.exists(fn):
        print("downloading",k,name); subprocess.run(["curl","-fsSL","--retry","3","-o",fn+".part",url],check=True); os.rename(fn+".part",fn)
    ROWS.append((fn,name,float(ss),float(gain),mode))
dur=lambda f: float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]))
import re
def tail_end(f):
    # cut trailing silence (some tracks end with 2-5s of dead air) so crossfades never dip
    d=dur(f); r=subprocess.run(['ffmpeg','-nostats','-i',f,'-af','silencedetect=n=-50dB:d=0.5','-f','null','-'],capture_output=True,text=True).stderr
    st=[float(x) for x in re.findall(r'silence_start: ([0-9.]+)',r)]; en=[float(x) for x in re.findall(r'silence_end: ([0-9.]+)',r)]
    if st and (len(en)<len(st) or en[-1]>=d-0.1): return min(d,st[-1]+0.4)
    return d
TE={r[0]:tail_end(r[0]) for r in ROWS}
D={r[0]:TE[r[0]]-r[2] for r in ROWS}
order=[]; tot=0
while tot<GOAL:
    r=ROWS[len(order)%len(ROWS)]; order.append(r); tot=sum(D[x[0]] for x in order)-XF*(len(order)-1)
TOT=tot; print("%d tracks, total %.1f s (%.2f h)"%(len(order),TOT,TOT/3600))
with open(B+"/chapters.txt","w") as f:
    s=0
    for r in order:
        f.write("%d:%02d:%02d %s\n"%(s//3600,s%3600//60,s%60,r[1])); s+=D[r[0]]-XF
print(open(B+"/chapters.txt").read()); sys.stdout.flush()
TEST=float(os.environ.get("TEST","0")); LEN=min(TOT,TEST) if TEST else TOT
# 1) audio (TEST renders only the first tracks it needs)
if TEST:
    keep=[]; acc=0
    for r in order:
        keep.append(r); acc+=D[r[0]]-XF
        if acc>LEN+10: break
    order=keep; TOT=min(TOT,sum(D[x[0]] for x in order)-XF*(len(order)-1))
AUD=B+f"/audio_192k_{len(order)}{'_test' if TEST else ''}.m4a"
if not os.path.exists(AUD):
    args=['ffmpeg','-y','-v','error','-stats']
    for r in order: args+=(['-ss',str(r[2])] if r[2] else [])+['-i',r[0]]
    n=len(order); fc=[]
    for k,r in enumerate(order):
        lev="dynaudnorm=f=3000:g=31:m=3:p=0.5:t=0.001," if r[4]=="dyn" else ""
        fc.append(f"[{k}:a]atrim=end={D[r[0]]:.3f},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,adeclick,{lev}acompressor=threshold=0.125:ratio=2.5:attack=300:release=2500:knee=6,volume={r[3]}dB,afade=t=in:d=1[a{k}]")
    prev="a0"
    for k in range(1,n): fc.append(f"[{prev}][a{k}]acrossfade=d={XF}:c1=tri:c2=tri[x{k}]"); prev=f"x{k}"
    fc.append(f"[{prev}]volume=2.5dB,alimiter=limit=0.7:attack=5:release=200:level=false,afade=t=out:st={TOT-6:.2f}:d=6,aresample=48000[aout]")
    args+=['-filter_complex',';'.join(fc),'-map','[aout]','-t',f"{TOT:.2f}",'-c:a','aac','-b:a','192k','-ar','48000',AUD+".tmp.m4a"]
    subprocess.run(args,check=True); os.rename(AUD+".tmp.m4a",AUD)
# 1b) opening voice (KJV verse + short prayer) over the first minute, music ducked under it
IV=A+"intro_voice.mp3"
if os.path.exists(IV):
    vd=dur(IV); VS=3.0; e=VS+vd+1.0
    g=f"if(lt(t,{VS-1.5}),1,if(lt(t,{VS}),1-0.68*(t-{VS-1.5})/1.5,if(lt(t,{e}),0.32,if(lt(t,{e+3}),0.32+0.68*(t-{e})/3,1))))"
    AUDV=AUD.replace(".m4a","_voice.m4a")
    if not os.path.exists(AUDV):
        subprocess.run(['ffmpeg','-y','-v','error','-stats','-i',AUD,'-i',IV,'-filter_complex',
            f"[0:a]volume='{g}':eval=frame[m];[1:a]aresample=48000,aformat=channel_layouts=stereo,loudnorm=I=-17:TP=-2:LRA=7,aresample=48000,adelay={int(VS*1000)}|{int(VS*1000)}[v];[m][v]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89:level=false[a]",
            '-map','[a]','-c:a','aac','-b:a','192k','-ar','48000',AUDV+".tmp.m4a"],check=True); os.rename(AUDV+".tmp.m4a",AUDV)
    AUD=AUDV; print("opening voice %.1fs from %.0fs"%(vd,VS))
# 2) video
# palace hall switch: the track change nearest the middle that is clear of verse cards and close-ups
starts=[]; s0=0
for r in order: starts.append(s0); s0+=D[r[0]]-XF
def busy(t): return any(abs(t-(60+540*i+12))<30 or (330+540*i-20<t<330+540*i+66) for i in range(21))
cands=[t+XF/2 for t in starts[1:] if not busy(t+XF/2)] or [TOT/2]
SW=min(cands,key=lambda t:abs(t-TOT/2)) if not TEST else min(TEST*0.5,TOT/2)
SW=float(os.environ.get("SWITCH",SW)); DIS=12.0; print("palace hall dissolve at %d:%02d:%02d"%(SW//3600,SW%3600//60,SW%60))
args=['ffmpeg','-y','-v','error','-stats','-stream_loop','-1','-i',B+'/loops/master.mp4','-i',B+f'/loops/opening_{COVER}.mp4','-stream_loop','-1','-i',B+'/loops/hall.mp4']
events=[(A+f"v{i:02d}.png",60+540*i,25,2,2) for i in range(20)]
kinds=["sub","share","amen"]; events+=[(A+f"cta_{kinds[k%3]}.png",180+1620*k,8,1,1.5) for k in range(7)]
events=[e for e in events if e[1]+e[2]<=TOT-20]
for e in events: args+=['-loop','1','-framerate','24','-t',str(e[2]),'-i',e[0]]
AI=3+len(events); args+=['-i',AUD]
fc=[f"[0:v]fps=24,scale={VW}:{VH}:flags=lanczos,setsar=1,format=yuv420p[t0]",f"[2:v]fps=24,scale={VW}:{VH}:flags=lanczos,setsar=1,format=yuva420p,fade=t=in:st={SW-DIS/2:.2f}:d={DIS}:alpha=1[hall]",
    f"[t0][hall]overlay=0:0:enable='gte(t,{SW-DIS/2:.2f})'[base]",f"[1:v]fps=24,scale={VW}:{VH}:flags=lanczos,setsar=1,format=yuv420p[op]","[base][op]overlay=0:0:eof_action=pass[b0]"]
cur="b0"
if os.environ.get('ZOOM','1')!='0':
    T="(in/24)"
    def sm(a,b):
        u=f"clip(({T}-{a})/{b-a},0,1)"; return f"({u}*{u}*(3-2*{u}))"
    targets=[(0.56,0.58),(0.22,0.45),(0.36,0.62),(0.62,0.40)]   # terrace: hands on strings, waterfall, sea and beach, harp and crown
    targets2=[(0.72,0.56),(0.20,0.62),(0.66,0.48),(0.62,0.74)]  # palace hall: David at the harp, fireplace, waterfall arch, pool and candles
    zt=["0"]; fx=["0"]; fy=["0"]
    for i in range(20):
        s=330+540*i
        if s+46>TOT-30: continue
        if s-60<SW<s+60: continue
        tx,ty=(targets2 if s>SW else targets)[i%4]; env=f"({sm(s,s+14)}-{sm(s+32,s+46)})"
        zt.append(f"0.12*{env}"); fx.append(f"{tx-0.5}*{env}"); fy.append(f"{ty-0.5}*{env}")
    Z="(1+"+"+".join(zt)+")"; FX="(0.5+"+"+".join(fx)+")"; FY="(0.5+"+"+".join(fy)+")"
    Lf=f"((W-W/{Z})*{FX})"; Tp=f"((H-H/{Z})*{FY})"; R=f"({Lf}+W/{Z})"; Bt=f"({Tp}+H/{Z})"
    fc.append(f"[{cur}]perspective=x0='{Lf}':y0='{Tp}':x1='{R}':y1='{Tp}':x2='{Lf}':y2='{Bt}':x3='{R}':y3='{Bt}':interpolation=cubic:sense=source:eval=frame[bz]"); cur="bz"
for j,(fn,st,du,fi,fo) in enumerate(events):
    fades=(f"fade=t=in:st=0:d={fi}:alpha=1," if fi>0 else "")+f"fade=t=out:st={du-fo}:d={fo}:alpha=1"
    fc.append(f"[{j+3}:v]scale={VW}:{VH},setsar=1,format=rgba,{fades},setpts=PTS+{st}/TB[o{j}]")
    fc.append(f"[{cur}][o{j}]overlay=0:0:eof_action=pass[c{j}]"); cur=f"c{j}"
fc.append(f"[{cur}]format=yuv420p[vout]")
args+=['-filter_complex',';'.join(fc),'-map','[vout]','-map',f'{AI}:a','-t',f"{LEN:.2f}",
       '-c:v','libx264','-preset',PRESET,'-tune','film','-crf',CRF,'-g','48','-bf','2','-pix_fmt','yuv420p',
       '-profile:v','high','-level','5.1','-c:a','copy','-movflags','+faststart',OUT]
subprocess.run(args,check=True)
print("DONE",OUT,os.path.getsize(OUT)//1_000_000,"MB")
