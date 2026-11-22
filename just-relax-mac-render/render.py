# Just Relax With Jesus Vol. 2 (3 Hour) - full-quality 4K render for Jose's Mac
# Run with the render venv (needs numpy + Pillow for the koi step):
#   caffeinate -dimsu "../Still Waters Render/.venv/bin/python" render.py     -> "Just Relax With Jesus Vol 2 (4K).mp4"
# Timeline: frame 1 = Cover A (text + left shade over the live scene), title fades 1.0-3.5s (hover hook),
#   then the seamless forest-pool loop with slow koi under the water (loops/koi_master.mp4, 237.5s, built once by koi.py),
#   Brian reads Matthew 11:28-29 + a short prayer from 3s (music dips 10 dB), 20 KJV verses every 540s from 60s (25s each),
#   small CTA cards at 180s + every 1620s, last 20s text-free (end screen). Camera never moves.
# Audio: music_list.txt in order (54 Suno piano + flute tracks), repeats from the top if short of GOAL, 5s crossfades,
#   per-track gain to about -20 LUFS, gentle compressor, limiter; soft waterfall bed far under the music; 48kHz AAC 192k.
# Options (env): RES=2160 (4K default; 1080 = HD) CRF=19 PRESET=medium TEST=150 (first N seconds) GOAL=10800 KOIRES=1080 WATER=-16
import os, sys, re, subprocess
B=os.path.dirname(os.path.abspath(__file__)); A=B+"/assets/"
CRF=os.environ.get("CRF","19"); PRESET=os.environ.get("PRESET","medium")
RES=int(os.environ.get("RES","2160")); VH=RES; VW=RES*16//9
OUT=sys.argv[1] if len(sys.argv)>1 else B+"/Just Relax With Jesus Vol 2 (4K).mp4"
XF=5.0; GOAL=float(os.environ.get("GOAL",3*3600)); WATER=float(os.environ.get("WATER","-16"))
dur=lambda f: float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]))
# 0) koi loop (once): slow koi + shadows over the 9.5s loop, seamless every 237.5s (= 25 loops)
KOI=B+"/loops/koi_master.mp4"
if not os.path.exists(KOI):
    print("building koi loop (one time, a few minutes)..."); sys.stdout.flush()
    subprocess.run([sys.executable,B+"/koi.py",B+"/loops/master.mp4",KOI+".part.mp4",os.environ.get("KOIRES","1080"),"237.5","237.5"],check=True)
    os.rename(KOI+".part.mp4",KOI)
# 1) music
os.makedirs(B+"/music",exist_ok=True); ROWS=[]
for line in open(B+"/music_list.txt"):
    if not line.strip(): continue
    k,name,url,ss,gain=line.rstrip("\n").split("|")[:5]; fn=B+f"/music/{k} {name}.mp3"
    if not os.path.exists(fn):
        print("downloading",k,name); subprocess.run(["curl","-fsSL","--retry","3","-o",fn+".part",url],check=True); os.rename(fn+".part",fn)
    ROWS.append((fn,name,float(ss),float(gain)))
def tail_end(f):
    d=dur(f); r=subprocess.run(['ffmpeg','-nostats','-i',f,'-af','silencedetect=n=-50dB:d=0.5','-f','null','-'],capture_output=True,text=True).stderr
    st=[float(x) for x in re.findall(r'silence_start: ([0-9.]+)',r)]; en=[float(x) for x in re.findall(r'silence_end: ([0-9.]+)',r)]
    if st and (len(en)<len(st) or en[-1]>=d-0.1): return min(d,st[-1]+0.4)
    return d
D={r[0]:tail_end(r[0])-r[2] for r in ROWS}
order=[]; tot=0
while tot<GOAL:
    r=ROWS[len(order)%len(ROWS)]; order.append(r); tot=sum(D[x[0]] for x in order)-XF*(len(order)-1)
TOT=tot; print("%d tracks, total %.1f s (%.2f h)"%(len(order),TOT,TOT/3600))
with open(B+"/chapters.txt","w") as f:
    s=0
    for r in order: f.write("%d:%02d:%02d %s\n"%(s//3600,s%3600//60,s%60,r[1])); s+=D[r[0]]-XF
print(open(B+"/chapters.txt").read()); sys.stdout.flush()
TEST=float(os.environ.get("TEST","0")); LEN=min(TOT,TEST) if TEST else TOT
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
        fc.append(f"[{k}:a]atrim=end={D[r[0]]:.3f},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,adeclick,acompressor=threshold=0.125:ratio=2.5:attack=300:release=2500:knee=6,volume={r[3]}dB,afade=t=in:d=1[a{k}]")
    prev="a0"
    for k in range(1,n): fc.append(f"[{prev}][a{k}]acrossfade=d={XF}:c1=tri:c2=tri[x{k}]"); prev=f"x{k}"
    fc.append(f"[{prev}]volume=2.5dB,alimiter=limit=0.7:attack=5:release=200:level=false,afade=t=out:st={TOT-6:.2f}:d=6,aresample=48000[aout]")
    args+=['-filter_complex',';'.join(fc),'-map','[aout]','-t',f"{TOT:.2f}",'-c:a','aac','-b:a','192k','-ar','48000',AUD+".tmp.m4a"]
    subprocess.run(args,check=True); os.rename(AUD+".tmp.m4a",AUD)
# 1b) opening voice + soft waterfall bed
IV=A+"intro_voice.mp3"; WB=A+"water_loop.mp3"
AUDV=AUD.replace(".m4a","_final.m4a")
if not os.path.exists(AUDV):
    vd=dur(IV); VS=3.0; e=VS+vd+1.0
    g=f"if(lt(t,{VS-1.5}),1,if(lt(t,{VS}),1-0.68*(t-{VS-1.5})/1.5,if(lt(t,{e}),0.32,if(lt(t,{e+3}),0.32+0.68*(t-{e})/3,1))))"
    inp=['-i',AUD,'-i',IV]; fc=f"[0:a]volume='{g}':eval=frame[m];[1:a]aresample=48000,aformat=channel_layouts=stereo,loudnorm=I=-17:TP=-2:LRA=7,aresample=48000,adelay={int(VS*1000)}|{int(VS*1000)}[v];"
    if os.path.exists(WB):
        inp+=['-stream_loop','-1','-i',WB]
        fc+=f"[2:a]aresample=48000,aformat=channel_layouts=stereo,lowpass=f=6000,volume={WATER}dB,afade=t=in:d=2,afade=t=out:st={TOT-6:.2f}:d=6[w];[m][v][w]amix=inputs=3:normalize=0:duration=first"
    else: fc+="[m][v]amix=inputs=2:normalize=0:duration=first"
    fc+=",alimiter=limit=0.89:level=false[a]"
    subprocess.run(['ffmpeg','-y','-v','error','-stats']+inp+['-filter_complex',fc,'-map','[a]','-t',f"{TOT:.2f}",'-c:a','aac','-b:a','192k','-ar','48000',AUDV+".tmp.m4a"],check=True)
    os.rename(AUDV+".tmp.m4a",AUDV)
AUD=AUDV
# 2) video
args=['ffmpeg','-y','-v','error','-stats','-stream_loop','-1','-i',KOI,'-loop','1','-framerate','24','-t','4','-i',A+'cover_layer_A.png']
events=[(A+f"v{i:02d}.png",60+540*i,25,2,2) for i in range(20)]
kinds=["sub","share","amen"]; events+=[(A+f"cta_{kinds[k%3]}.png",180+1620*k,8,1,1.5) for k in range(7)]
events=[e for e in events if e[1]+e[2]<=TOT-20]
for e in events: args+=['-loop','1','-framerate','24','-t',str(e[2]),'-i',e[0]]
AI=2+len(events); args+=['-i',AUD]
fc=[f"[0:v]fps=24,scale={VW}:{VH}:flags=lanczos,setsar=1,format=yuv420p[b0]",
    f"[1:v]scale={VW}:{VH},setsar=1,format=rgba,fade=t=out:st=1.0:d=2.5:alpha=1[cv]","[b0][cv]overlay=0:0:eof_action=pass[c]"]
cur="c"
for j,(fn,st,du,fi,fo) in enumerate(events):
    fades=(f"fade=t=in:st=0:d={fi}:alpha=1," if fi>0 else "")+f"fade=t=out:st={du-fo}:d={fo}:alpha=1"
    fc.append(f"[{j+2}:v]scale={VW}:{VH},setsar=1,format=rgba,{fades},setpts=PTS+{st}/TB[o{j}]")
    fc.append(f"[{cur}][o{j}]overlay=0:0:eof_action=pass[c{j}]"); cur=f"c{j}"
fc.append(f"[{cur}]format=yuv420p[vout]")
args+=['-filter_complex',';'.join(fc),'-map','[vout]','-map',f'{AI}:a','-t',f"{LEN:.2f}",
       '-c:v','libx264','-preset',PRESET,'-tune','film','-crf',CRF,'-g','48','-bf','2','-pix_fmt','yuv420p',
       '-profile:v','high','-level','5.1','-c:a','copy','-movflags','+faststart',OUT]
subprocess.run(args,check=True)
print("DONE",OUT,os.path.getsize(OUT)//1_000_000,"MB")
