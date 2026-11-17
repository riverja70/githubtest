# EMMANUEL Alpine Village 3 Hour (HQ render kit)

Run on the Mac (needs ffmpeg + python3 only):

    cd alpine-mac-render
    caffeinate -dimsu python3 render.py

Output: `Emmanuel Alpine Village 3 Hour (HQ).mp4` (about 3:01:20, 1080p24, AAC 48kHz).
The script downloads the 51 piano + guitar carols into `music/` first, then builds the audio and the video.
Quick check first: `TEST=120 python3 render.py test.mp4` renders only the first 2 minutes.

- loops/opening.mp4: frame 1 = cover, title fades over 1-3s (hover hook)
- loops/snow_full / snow_out / snow_clear / snow_in: the village loop with light snow that comes and goes (fixed random order)
- assets/: 20 KJV verse cards + 3 CTA cards; last 20s stay text-free for the end screen
