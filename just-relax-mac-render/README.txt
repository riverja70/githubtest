JUST RELAX WITH JESUS VOL. 2 (3 Hour) - 4K Mac render kit (2026-11-22)
Run in this folder with the render venv (numpy + Pillow needed only if loops/koi_master.mp4 is missing):
  caffeinate -dimsu "../Still Waters Render/.venv/bin/python" render.py
  - downloads the 54 piano + flute tracks (music_list.txt, ~180 MB) with curl, mixes audio, then renders
  - Output: "Just Relax With Jesus Vol 2 (4K).mp4", 3840x2160 24fps, H.264 CRF 19, AAC 192k 48kHz, about 3:00
  - Opening: Cover A over the live scene, title fades 1.0-3.5s; Brian reads Matthew 11:28-29 + prayer from 3s
  - koi swim slowly under the water (loops/koi_master.mp4, 237.5s seamless; koi.py rebuilds it if deleted)
  - 20 KJV verse cards every 9 min from 1:00, 3 small CTA cards, last 20s text-free, soft waterfall bed (WATER=-16 dB)
  - writes chapters.txt
Quick check first (~2 min):  TEST=90 RES=1080 python3 render.py test.mp4
Options (env): RES=1080 (HD copy) CRF=19 PRESET=slow TEST=600 GOAL=10800 WATER=-16
