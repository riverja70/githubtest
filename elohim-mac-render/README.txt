ELOHIM HARP 3 Hour - full-quality Mac render kit (2026-11-21)
Run (in this folder):  caffeinate -dimsu python3 render.py
  - first downloads the 34 harp tracks (music_list.txt, ~185 MB) with curl, then renders
  - Cover choice: COVER=B (PRAISE HIM, default) or COVER=A (ELOHIM):  COVER=A caffeinate -dimsu python3 render.py
  - Output: "ELOHIM Harp 3 Hour (HQ).mp4", 1920x1080 24fps, H.264 CRF 19, AAC 192k 48kHz, about 3:01, ~-20 LUFS
  - writes chapters.txt (already pasted into the upload notes)
Quick check first (optional, ~2 min):  TEST=150 python3 render.py test.mp4
Inside: loops/master.mp4 (seamless 9.5s King David harp loop), loops/opening_A/B.mp4 (cover melts into the scene),
  assets/ (20 KJV verse cards every 9 min from 60s, 3 small CTA cards), covers/, music_list.txt (order + gain per track).
Options (env): CRF=19 PRESET=slow ZOOM=0 (no slow close-ups) TEST=600 GOAL=10800
