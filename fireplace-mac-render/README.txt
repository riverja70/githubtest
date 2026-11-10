CHRISTMAS FIREPLACE 3 Hour - full-quality Mac render kit (2026-11-10)
Run (in this folder):  caffeinate -dimsu python3 render.py
  - first downloads the 48 solo piano tracks (music_list.txt, ~260 MB) with curl, then renders
  - Output: "Christmas Fireplace 3 Hour (HQ).mp4", 1920x1080 24fps, H.264 CRF 19, AAC 192k 48kHz, about 3:01:20
  - writes chapters.txt (already pasted into the upload notes)
Quick check first (optional, ~2 min):  TEST=200 python3 render.py test.mp4
What is inside:
  loops/opening.mp4     0-12s: frame 1 = the exact cover, title melts away, outside cabin in falling snow, dissolves into the room
  loops/master_72s.mp4  seamless room loop: fire, candles, cocoa steam, tree lights, heavy snow in every window, gentle Bible page breath
  fire/fire.mp3         soft fire bed (level locked: ~-55 LUFS, peaks -34 dB, "the fire is perfect now")
  assets/               20 KJV verse cards (60s + every 9 min, 25s each), 3 CTA cards (180s + every 27 min). Last 20s text-free.
  covers/               cover_main.jpg (1920) and cover_main_1280.jpg (YouTube thumbnail)
  make_*.py, add_snow.py, build_loop.sh   cloud scripts that built the assets (not needed on the Mac)
Options (env): CRF=19 PRESET=slow ZOOM=0 (no slow close-ups) TEST=600 GOAL=10800
