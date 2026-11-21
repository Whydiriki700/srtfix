"""Parsing, repair, and timing math for .srt files."""
import re

TIMING = re.compile(
    r"^(\d{1,2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{1,2}):(\d{2}):(\d{2})[,.](\d{3})")


def to_ms(h, m, s, ms):
    return ((int(h) * 60 + int(m)) * 60 + int(s)) * 1000 + int(ms)


def format_ms(total):
    if total < 0:
        total = 0
    h, rem = divmod(total, 3600000)
    m, rem = divmod(rem, 60000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def parse_srt(text):
    """Returns (cues, skipped_blocks). A cue is {start, end, lines} in ms."""
    text = text.replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff")
    blocks = re.split(r"\n\s*\n", text.strip())
    cues = []
    skipped = 0
    for block in blocks:
        lines = [line for line in block.split("\n")]
        timing_idx = None
        for idx, line in enumerate(lines):
            if TIMING.match(line.strip()):
                timing_idx = idx
                break
        if timing_idx is None:
            if block.strip():
                skipped += 1
            continue
        match = TIMING.match(lines[timing_idx].strip())
        start = to_ms(*match.groups()[:4])
        end = to_ms(*match.groups()[4:])
        cues.append({"start": start, "end": end, "lines": lines[timing_idx + 1:]})
    return cues, skipped


def repair(cues, shift_ms=0, scale=1.0, fix_overlaps=True):
    """Applies shift and scale, sorts, drops empty cues, clamps overlaps.
    Returns (cues, report)."""
    report = {"dropped_empty": 0, "overlaps_fixed": 0, "clamped_negative": 0}
    out = []
    for cue in cues:
        text_lines = [line for line in cue["lines"] if line.strip()]
        if not text_lines:
            report["dropped_empty"] += 1
            continue
        start = int(round(cue["start"] * scale)) + shift_ms
        end = int(round(cue["end"] * scale)) + shift_ms
        if start < 0:
            report["clamped_negative"] += 1
            end -= start
            start = 0
        if end <= start:
            end = start + 1
        out.append({"start": start, "end": end, "lines": text_lines})
    out.sort(key=lambda c: c["start"])
    if fix_overlaps:
        for i in range(len(out) - 1):
            if out[i]["end"] > out[i + 1]["start"]:
                out[i]["end"] = out[i + 1]["start"]
                if out[i]["end"] <= out[i]["start"]:
                    out[i]["end"] = out[i]["start"] + 1
                report["overlaps_fixed"] += 1
    return out, report


def render_srt(cues):
    blocks = []
    for idx, cue in enumerate(cues, 1):
        blocks.append("\n".join(
            [str(idx), f"{format_ms(cue['start'])} --> {format_ms(cue['end'])}"] + cue["lines"]))
    return "\n\n".join(blocks) + "\n"
