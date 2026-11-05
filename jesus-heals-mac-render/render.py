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
      '-loop','1','-framerate','24','-t',f"{TOT:.2f}",'-i',A+'dusk.png']
for e in events: args+=['-loop','1','-framerate','24','-t',str(e[2]),'-i',e[0]]
args+=['-i',AUD]
fc=["[0:v]scale=1920:1080:flags=lanczos,setsar=1,fps=24,format=yuv420p[b0]",
    f"[1:v]format=rgba,fade=t=in:st=0:d={TOT:.2f}:alpha=1[dk]",
    "[b0][dk]overlay=0:0:eof_action=pass[b1]"]
cur="b1"
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
