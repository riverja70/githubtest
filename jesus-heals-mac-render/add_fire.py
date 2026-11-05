# Adds a soft looping fireplace crackle under the music of the HQ render. Video stream is copied (no re-encode).
# Usage: python3 add_fire.py "<path to JesusHeals 3 Hour (HQ).mp4>"   [env FIRE_LUFS, default -40 = about 18 dB under the music]
import os, sys, re, subprocess, urllib.request
B=os.path.dirname(os.path.abspath(__file__))
SRC=sys.argv[1]; OUT=SRC.replace("(HQ).mp4","(HQ fire).mp4")
URL="https://storage.contentcreatortemplates.com/storage/v1/object/public/test/01a1ab7a-b2cf-7234-adcd-c21d256ae3c3.mp3"
FIRE=B+"/fireplace_crackle.mp3"
if not os.path.exists(FIRE): urllib.request.urlretrieve(URL,FIRE)
TARGET=float(os.environ.get("FIRE_LUFS","-40"))
r=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',FIRE,'-af','ebur128','-f','null','-'],capture_output=True,text=True).stderr
I=float(re.findall(r"I:\s+(-?[\d.]+) LUFS",r)[-1]); gain=TARGET-I
dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',SRC]))
print(f"crackle {I:.1f} LUFS -> gain {gain:+.1f} dB, video {dur:.1f}s"); sys.stdout.flush()
fc=(f"[1:a]aresample=48000,aformat=channel_layouts=stereo,volume={gain:.2f}dB,"
    f"afade=t=in:st=0:d=8,afade=t=out:st={dur-6:.2f}:d=6[f];"
    f"[0:a][f]amix=inputs=2:duration=first:normalize=0,aresample=48000[a]")
subprocess.run(['ffmpeg','-y','-v','error','-stats','-i',SRC,'-stream_loop','-1','-i',FIRE,'-filter_complex',fc,
  '-map','0:v','-map','[a]','-t',f"{dur:.3f}",'-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',OUT],check=True)
# 2-minute listening check clip (from 1:00:00)
subprocess.run(['ffmpeg','-y','-v','error','-ss','3600','-i',OUT,'-t','120','-c','copy',OUT.replace(".mp4"," check 2min.mp4")],check=True)
print("DONE",OUT,os.path.getsize(OUT)//1_000_000,"MB")
