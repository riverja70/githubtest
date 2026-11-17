# Builds loops/opening.mp4 (12s): frame 1 = the exact cover (hover hook); title and grade melt into the live loop 1-3s.
import subprocess
subprocess.run(["ffmpeg","-loglevel","error","-y","-i","loops/snow_full.mp4","-loop","1","-framerate","24","-t","12","-i","covers/cover_main.jpg",
 "-filter_complex","[1:v]scale=1920:1080,format=rgba,fade=t=out:st=1:d=2:alpha=1[c];[0:v][c]overlay=0:0:shortest=1,format=yuv420p[v]",
 "-map","[v]","-t","12","-r","24","-c:v","libx264","-preset","slow","-crf","14","loops/opening.mp4"],check=True)
