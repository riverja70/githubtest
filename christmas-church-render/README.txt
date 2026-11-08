GREAT JOY - snowy village church, 10-minute Christmas soaking worship (concept 3 of the Christmas 10-min series)
Needs python3 (Pillow, numpy) + ffmpeg.
  python3 make_overlays.py still_4k.png   # cover, title, 6 KJV verse cards, CTA cards
  python3 make_snow.py                    # full-frame falling snow loop (assets/snow.mp4)
  python3 make_smoke.py                   # rising chimney smoke loop (assets/smoke.mp4)
  caffeinate -dimsu python3 render.py     # -> "Great Joy Village Church 10 Min (HQ).mp4"
  DUR=20 ZOOM=0 PRESET=veryfast python3 render.py preview.mp4   # quick preview
