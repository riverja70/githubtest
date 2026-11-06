THANKFUL 3 Hour - full-quality Mac render kit (2026-11-06). Same technique as Jesus Heals FINAL v4.
Run:  python3 render.py      (needs ffmpeg; about 1-3 hours on a Mac Studio; keep the Mac awake: caffeinate -dimsu python3 render.py)
Output: "THANKFUL 3 Hour (HQ).mp4", 1920x1080 24fps, H.264 CRF 18, AAC 192k 48kHz, 3:00:21, about 5-6 GB. Upload directly in YouTube Studio.
Also writes chapters.txt (paste into the description).

What is inside:
  loops/hour1-3.mp4   Veo 3.1 loops (8s, start = end frame): bench afternoon, oak at sunset, chapel path at dusk
  music/              9 Suno songs, played in order 4 times (+ Every Good Gift at the end), 5s crossfades, adeclick + gentle compressor, -4dB
  assets/             title card (0-9s), 20 KJV verse cards (every 540s from 60s), 3 CTA cards (180s + every 1620s), ramp1-3 (light ramp per hour)
  covers/             main pop cover + B and C for Test & Compare (make_covers.py)
  make_assets.py      rebuilds assets/ + the verses .srt (cloud only, needs Pillow + fonts)
Timeline: scene 1 -> 30s crossfade at 1:00:07 -> scene 2 -> 30s crossfade at 2:00:14 -> scene 3. Opening pull-back (40s), then a slow
close-up drift and back every 9 min (skipped near the scene crossfades). Last 20s has no text (end screen).
Options: CRF=18 PRESET=slow RAMP=0 ZOOM=0 XD=30 TEST=600 (first N seconds only) GOAL=1500 (short full-structure test).
