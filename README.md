# srtfix

Subtitles drift, overlap, and arrive numbered like a crime scene. srtfix
repairs .srt files and retimes them, with a plain report of what it changed.

## What it does

- Shift every cue by a number of milliseconds, forward or backward
  (timings that would go negative are clamped to zero, never lost)
- Retime between frame rates, for example subtitles written for 25 fps
  shown on a 23.976 fps cut
- Fix overlapping cues by clamping each end to the next cue's start
- Drop empty cues, sort cues by start time, and renumber cleanly
- Count blocks it could not parse instead of silently eating them

## Usage

```
python -m srtfix movie.srt --shift 500 -o movie-fixed.srt
python -m srtfix movie.srt --shift -1200 -o movie-fixed.srt
python -m srtfix movie.srt --fps-from 25 --fps-to 23.976 -o movie-fixed.srt
```

Without `-o` the fixed file goes to stdout, and the report goes to stderr:

```
cues: 812 in, 809 out; skipped blocks: 0; overlaps fixed: 14; empty dropped: 3
```

## Tests

```
python -m unittest discover -s tests
```

Zero dependencies. Python 3.9+. MIT license.
