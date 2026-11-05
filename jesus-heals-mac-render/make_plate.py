# Builds sky_plate.png (sharp city view at loop size; render.py applies the window mask) from the 4K sharp-skyline still. ffmpeg + stdlib only.
# Usage: python3 make_plate.py <url or local path of the 4K still>
import os, sys, subprocess, urllib.request
B=os.path.dirname(os.path.abspath(__file__)); src=sys.argv[1]
if src.startswith("http"):
    req=urllib.request.Request(src,headers={"User-Agent":"Mozilla/5.0"})
    open(B+"/sky_4k.png","wb").write(urllib.request.urlopen(req).read()); src=B+"/sky_4k.png"
subprocess.run(['ffmpeg','-y','-v','error','-i',src,'-vf','scale=1928:1072:flags=lanczos','-frames:v','1',B+'/sky_plate.png'],check=True)
print("plate ready:",B+"/sky_plate.png")
