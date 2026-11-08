EMMANUEL - Christmas cafe soaking worship, 1 hour (2026-11-08). Full-quality render kit for Jose's Mac.

Run (in Terminal, from this folder), keeping the Mac awake:
  caffeinate -dimsu python3 render.py
Output: "Emmanuel Christmas Cafe 1 Hour (HQ).mp4"  1920x1080 24fps, H.264 CRF 18, AAC 192k 48kHz, about 1.2-1.6 GB, 1:04:07.
Needs only python3 + ffmpeg (no extra packages). About 30-60 min on a Mac Studio.

What's inside:
  loop.mp4            Kling 3.0 10s loop (fire, candles, snow, twinkling lights), start = end frame
  fire_crackle.mp3    soft fire crackle (looped under the music, pops tamed by a limiter)
  music/              11 carols, piano + sax / piano + flute, 5s crossfades (chapters.txt)
  assets/title.png    hover hook: frame 1 = exact cover, title fades out 1.5-4 s
  assets/lights_*     random lights going off/on near the window and on the tree
  assets/v00-v09.png  10 KJV nativity verses (every 6 min from 1:00), cta_*.png small cards at 10, 30, 50 min
  make_overlays.py / make_lights.py rebuild the assets (cloud side, need Pillow + numpy)
Options: DUR=90 (short test), CRF=16 (higher quality), ZOOM=0 (no camera moments), FIRE_DB=-2 (crackle level; Jose wants it as low as possible).
Upload notes, title, description, tags and subtitles: "Upload notes.txt", "Emmanuel verses (English subtitles).srt".
