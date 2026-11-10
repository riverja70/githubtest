#!/bin/bash
# Builds a 72s seamless master loop: Kling room loop (9s seamless) + masked Bible ping-pong (8s), 1920x1080 24fps.
# usage: build_loop.sh loop.mp4 bible.mp4 bible_mask.png out.mp4
set -e
L="$1"; B="$2"; M="$3"; OUT="$4"
ffmpeg -loglevel error -y -i "$L" -i "$B" -loop 1 -i "$M" -filter_complex "
[0:v]split=3[l1][l2][l3];
[l1]trim=1:9,setpts=PTS-STARTPTS[mid];
[l2]trim=9:10,setpts=PTS-STARTPTS[tail];
[l3]trim=0:1,setpts=PTS-STARTPTS[head];
[tail][head]xfade=transition=fade:duration=1:offset=0[seam];
[seam][mid]concat=n=2:v=1[room9];
[room9]loop=loop=7:size=216,trim=duration=72,setpts=PTS-STARTPTS,format=yuv444p[room];
[1:v]trim=end_frame=96,setpts=PTS-STARTPTS,split[bf][bf2];
[bf2]reverse[br];
[bf][br]concat=n=2:v=1[bp8];
[bp8]loop=loop=8:size=192,trim=duration=72,setpts=PTS-STARTPTS,format=yuv444p[bib];
[2:v]format=gray,trim=duration=72[mask];
[bib][mask]alphamerge[bibm];
[room][bibm]overlay=0:0:format=auto,scale=1942:1080:flags=lanczos,crop=1920:1080,format=yuv420p[v]" \
 -map "[v]" -r 24 -c:v libx264 -preset slow -crf 14 -t 72 "$OUT"
