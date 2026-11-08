# GREAT JOY - snowy village church Christmas soaking worship (10-minute series), full-quality render for Jose's Mac (needs only python3 + ffmpeg)
# Usage: python3 render.py                 -> "Great Joy Village Church 10 Min (HQ).mp4"  (1080p24, CRF 18, AAC 192k 48kHz)
#        DUR=90 python3 render.py out.mp4  -> short preview
# Timeline: hover hook (frame 1 = exact cover, title fades 1.5-4 s) + Kling loop (snow, chimney smoke, lanterns, twinkle) + full-frame falling-snow layer + rising chimney smoke layer
#           + slow camera moments + 6 KJV verses (Luke 2 / Psalm 95:6 / Isaiah 9:2 / John) + 3 small cards + 2 carols. Last 30 s text-free.
import os, sys, glob, subprocess
B=os.path.dirname(os.path.abspath(__file__)); A=B+"/assets/"
CRF=os.environ.get("CRF","18"); PRESET=os.environ.get("PRESET","slow")
OUT=sys.argv[1] if len(sys.argv)>1 else B+"/Great Joy Village Church 10 Min (HQ).mp4"
XF=5.0
# SHORT=1 -> 10-minute posting test: 2 carols, verses every 2 min, cover strip without "1 HOUR"
SHORT=os.environ.get("SHORT","0")=="1"
tracks=sorted(glob.glob(B+"/music/*.mp3")); SHORT=True
dur=lambda f: float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]))
FULL=sum(dur(t) for t in tracks)-XF*(len(tracks)-1)
TOT=float(os.environ.get("DUR",FULL))
print("total %.1f s (%.2f min); rendering %.1f s"%(FULL,FULL/60,TOT)); sys.stdout.flush()
# chapters for the description
t=0.0
with open(B+("/chapters_10min.txt" if SHORT else "/chapters.txt"),"w") as ch:
    for k,f in enumerate(tracks):
        name=os.path.basename(f)[3:-4]
        ch.write("%d:%02d %s\n"%(int(t)//60,int(t)%60,name)); t+=dur(f)-XF
# 1) audio: carols crossfaded + looping fire crackle underneath
AUD=B+("/audio_10min_192k.m4a" if SHORT else "/audio_192k.m4a")
if not os.path.exists(AUD):
    args=['ffmpeg','-y','-v','error','-stats']
    for f in tracks: args+=['-i',f]
    n=len(tracks)
    fc=[f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,adeclick,acompressor=threshold=0.125:ratio=2.5:attack=300:release=2500:knee=6[a{k}]" for k in range(n)]
    prev="a0"
    for k in range(1,n):
        fc.append(f"[{prev}][a{k}]acrossfade=d={XF}:c1=tri:c2=tri[x{k}]"); prev=f"x{k}"
    fc.append(f"[{prev}]volume=-4dB,afade=t=out:st={FULL-6:.2f}:d=6,alimiter=limit=0.89:attack=5:release=200:level=false,aresample=48000[aout]")
    args+=['-filter_complex',';'.join(fc),'-map','[aout]','-t',f"{FULL:.2f}",'-c:a','aac','-b:a','192k','-ar','48000',AUD+".tmp.m4a"]
    subprocess.run(args,check=True); os.rename(AUD+".tmp.m4a",AUD)
# 2) video + mux
events=[(A+("title_10min.png" if SHORT else "title.png"),0,4,0,2.5)]   # hover hook: cover title, fades out 1.5-4 s
if SHORT:
    events+=[(A+f"v{k:02d}.png",40+100*i,22,2,2) for i,k in enumerate(range(6))]  # Luke 2:11 first
    events+=[(A+f"cta_{k}.png",s,8,1,1.5) for k,s in (("amen",95),("sub",295),("share",495))]
else:
    events+=[(A+f"v{i:02d}.png",60+360*i,25,2,2) for i in range(10)]     # verses
    events+=[(A+f"cta_{k}.png",s,8,1,1.5) for k,s in (("sub",600),("share",1800),("amen",3000))]
events=[e for e in events if e[1]+e[2]<=FULL-30 and e[1]<TOT]
args=['ffmpeg','-y','-v','error','-stats','-stream_loop','-1','-i',B+'/loop.mp4','-stream_loop','-1','-i',A+'snow.mp4','-stream_loop','-1','-i',A+'smoke.mp4']
for e in events: args+=['-loop','1','-framerate','24','-t',str(e[2]),'-i',e[0]]
args+=['-i',AUD]
O=3
fc=["[0:v]scale=1920:1080:flags=lanczos,setsar=1,fps=24,format=rgba[b0]",
    "[1:v]fps=24,format=gray[sa]","color=c=white:s=1920x1080:r=24,format=rgba[sw]","[sw][sa]alphamerge[sn]",
    "[2:v]fps=24,format=gray[ma]","color=c=0xCDD4E1:s=1920x1080:r=24,format=rgba[mw]","[mw][ma]alphamerge[sm]",
    "[b0][sm]overlay=0:0:shortest=0[b0s]",   # rising chimney smoke (make_smoke.py)
    "[b0s][sn]overlay=0:0:shortest=0[b1]"]   # falling snow over the whole picture, all video long
cur="b1"
if os.environ.get('ZOOM','1')!='0':
    T="(in/24)"
    def sm(a,b):
        u=f"clip(({T}-{a})/{b-a},0,1)"; return f"({u}*{u}*(3-2*{u}))"
    targets=[(0.55,0.72),(0.57,0.22),(0.17,0.64),(0.86,0.64)]  # church door, steeple, left cottages, right cottage
    zt=["0"]; fx=["0"]; fy=["0"]
    for i in range(10):
        s=(150+200*i) if SHORT else 270+540*i; tx,ty=targets[i%4]
        if s+46>FULL-30: continue
        env=f"({sm(s,s+14)}-{sm(s+32,s+46)})"
        zt.append(f"0.20*{env}"); fx.append(f"{tx-0.5}*{env}"); fy.append(f"{ty-0.5}*{env}")
    Z="(1+"+"+".join(zt)+")"; FX="(0.5+"+"+".join(fx)+")"; FY="(0.5+"+"+".join(fy)+")"
    L=f"((W-W/{Z})*{FX})"; Tp=f"((H-H/{Z})*{FY})"; R=f"({L}+W/{Z})"; Bt=f"({Tp}+H/{Z})"
    fc.append(f"[b1]perspective=x0='{L}':y0='{Tp}':x1='{R}':y1='{Tp}':x2='{L}':y2='{Bt}':x3='{R}':y3='{Bt}':interpolation=cubic:sense=source:eval=frame[bz]")
    cur="bz"
for j,(fn,st,du,fi,fo) in enumerate(events):
    fades=(f"fade=t=in:st=0:d={fi}:alpha=1," if fi>0 else "")+f"fade=t=out:st={du-fo}:d={fo}:alpha=1"
    fc.append(f"[{j+O}:v]format=rgba,{fades},setpts=PTS+{st}/TB[o{j}]")
    fc.append(f"[{cur}][o{j}]overlay=0:0:eof_action=pass[c{j}]"); cur=f"c{j}"
fc.append(f"[{cur}]format=yuv420p[vout]")
args+=['-filter_complex',';'.join(fc),'-map','[vout]','-map',f'{len(events)+O}:a','-t',f"{TOT:.2f}",
       '-c:v','libx264','-preset',PRESET,'-tune','film','-crf',CRF,'-g','48','-bf','2','-pix_fmt','yuv420p',
       '-profile:v','high','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',OUT]
subprocess.run(args,check=True)
print("DONE",OUT,os.path.getsize(OUT)//1_000_000,"MB")
