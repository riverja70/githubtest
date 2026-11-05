# Jesus Heals NYC 3 Hour - full-quality render for Jose's Mac (only needs ffmpeg + python3, no extra packages)
# Usage: python3 render.py            -> "JesusHeals 3 Hour (HQ).mp4" (CRF 18, AAC 192k, 48kHz)
# Same timeline as the approved 443MB cloud version: loop + slow dusk + title + 20 KJV verses + 7 CTA cards + 31 crossfaded tracks.
import os, sys, glob, subprocess
B=os.path.dirname(os.path.abspath(__file__)); A=B+"/assets/"
CRF=os.environ.get("CRF","18"); PRESET=os.environ.get("PRESET","slow")
OUT=sys.argv[1] if len(sys.argv)>1 else B+"/JesusHeals 3 Hour (HQ).mp4"
XF=5.0
tracks=sorted(glob.glob(B+"/music/*.mp3")); assert len(tracks)==10, tracks
order=tracks*3+[tracks[0]]
dur=lambda f: float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]))
TOT=sum(dur(t) for t in order)-XF*(len(order)-1)
print("total %.1f s (%.2f h)"%(TOT,TOT/3600)); sys.stdout.flush()
# 1) audio
AUD=B+"/audio_192k.m4a"
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
# 2) video + mux
events=[(A+"title.png",0,9,0,2)]
events+=[(A+f"v{i:02d}.png",60+540*i,25,2,2) for i in range(20)]
kinds=["sub","share","amen"]
events+=[(A+f"cta_{kinds[k%3]}.png",180+1620*k,8,1,1.5) for k in range(7)]
args=['ffmpeg','-y','-v','error','-stats','-stream_loop','-1','-i',B+'/'+os.environ.get('LOOP','loop_v3.mp4'),
      '-loop','1','-framerate','24','-t',f"{TOT:.2f}",'-i',A+os.environ.get('DUSK','dusk.png')]
for e in events: args+=['-loop','1','-framerate','24','-t',str(e[2]),'-i',e[0]]
args+=['-i',AUD]
PLATE=os.environ.get('PLATE')  # optional sharp city plate (RGB, loop size), masked into the windows
GAIN=os.environ.get('GAIN','1')!='0'  # animate city lights (twinkle / on-off / colour) with assets/citylights_gain.mp4
pre=[]
if PLATE:
    P0=len(events)+3
    args+=['-loop','1','-framerate','24','-i',PLATE,'-loop','1','-framerate','24','-i',A+'window_plate_mask.png']
    if GAIN:
        args+=['-stream_loop','-1','-i',A+'citylights_gain.mp4']
        pre+=[f"[{P0}:v]format=gbrp[pa]",f"[{P0+2}:v]format=gbrp[ga]","[pa][ga]blend=all_mode=multiply,format=rgba[pm]"]
    else:
        pre+=[f"[{P0}:v]format=rgba[pm]"]
    pre+=[f"[{P0+1}:v]format=gray[mk]","[pm][mk]alphamerge[pl]","[0:v][pl]overlay=0:0[lp]"]
SRCV='lp' if PLATE else '0:v'
fc=pre+[f"[{SRCV}]scale=1920:1080:flags=lanczos,setsar=1,fps=24,format=yuv420p[b0]",
    f"[1:v]format=rgba,fade=t=in:st=0:d={TOT:.2f}:alpha=1[dk]",
    "[b0][dk]overlay=0:0:eof_action=pass[b1]"]
cur="b1"
# --- gentle camera moments (ZOOM=1): slow pull-back over the first 40s, then every 9 min a slow drift into a close-up and back
if os.environ.get('ZOOM','1')!='0':
    ZOFF=float(os.environ.get('ZOFF','0'))
    T="(in/24)"
    def sm(a,b):  # smoothstep 0->1 between a and b
        u=f"clip(({T}-{a})/{b-a},0,1)"; return f"({u}*{u}*(3-2*{u}))"
    targets=[(0.47,0.80),(0.55,0.32),(0.10,0.62),(0.80,0.66)]  # Bible+candle, city/Empire State, fireplace, lantern+tea
    zt=["0.12*(1-"+sm(0,40)+")"]; fx=["0"]; fy=["0"]
    for i in range(20):
        s=330+540*i-ZOFF; tx,ty=targets[i%4]
        if s<0 or s+46>TOT-30: continue
        env=f"({sm(s,s+14)}-{sm(s+32,s+46)})"
        zt.append(f"0.20*{env}"); fx.append(f"{tx-0.5}*{env}"); fy.append(f"{ty-0.5}*{env}")
    Z="(1+"+"+".join(zt)+")"; FX="(0.5+"+"+".join(fx)+")"; FY="(0.5+"+"+".join(fy)+")"
    L=f"((W-W/{Z})*{FX})"; Tp=f"((H-H/{Z})*{FY})"; R=f"({L}+W/{Z})"; Bt=f"({Tp}+H/{Z})"
    fc.append(f"[b1]perspective=x0='{L}':y0='{Tp}':x1='{R}':y1='{Tp}':x2='{L}':y2='{Bt}':x3='{R}':y3='{Bt}':interpolation=cubic:sense=source:eval=frame[bz]")
    cur="bz"
for j,(fn,st,du,fi,fo) in enumerate(events):
    fades=(f"fade=t=in:st=0:d={fi}:alpha=1," if fi>0 else "")+f"fade=t=out:st={du-fo}:d={fo}:alpha=1"
    fc.append(f"[{j+2}:v]format=rgba,{fades},setpts=PTS+{st}/TB[o{j}]")
    fc.append(f"[{cur}][o{j}]overlay=0:0:eof_action=pass[c{j}]"); cur=f"c{j}"
fc.append(f"[{cur}]format=yuv420p[vout]")
args+=['-filter_complex',';'.join(fc),'-map','[vout]','-map',f'{len(events)+2}:a','-t',f"{TOT:.2f}",
       '-c:v','libx264','-preset',PRESET,'-tune','film','-crf',CRF,'-g','48','-bf','2','-pix_fmt','yuv420p',
       '-profile:v','high','-c:a','copy','-movflags','+faststart',OUT]
subprocess.run(args,check=True)
print("DONE",OUT,os.path.getsize(OUT)//1_000_000,"MB")
