# Topology & Geometry Course Concepts Research

This repo is a source-backed companion for Tadashi Tokieda's AIMS South Africa course, **Topology & Geometry**.

Playlist: https://www.youtube.com/playlist?list=PLTBqohhFNBE_09L0i-lf3fYXF5woAbrzJ

## Goal

Build a deep, plain-language treatment of the course across lectures, themes, subthemes, concepts, and method families. The writing starts from first principles: what problem the idea solves, what detail matters, why the mathematical principle is important, and how the ideas connect. It avoids assuming prior knowledge of mathematics, machine learning, benchmark language, causal inference, optimization, or systems language.

## Current Source State

- 35 playlist videos discovered.
- 15 lecture groups recovered from titles.
- 34 English auto-caption files recovered.
- 1 video currently reports no captions through `yt-dlp`: `nx1XOlezuvk`.
- Raw captions live in `raw-material/youtube/captions/`.
- Cleaned transcripts live in `raw-material/youtube/transcripts/`.

## Commands

```bash
python3 scripts/build_course.py
python3 scripts/validate_all.py
python3 -m http.server 8790 --directory site
```

Then open:

```text
http://127.0.0.1:8790/
```

## Important Caveat

This is the first transcript-backed build. It has the structure needed for a robotics-level companion, but the lecture-by-lecture narrative should still be expanded by hand from the recovered transcripts. Do not treat auto-captions as exact mathematical text; they can mishear names, symbols, and short technical words.
