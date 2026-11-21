"""CLI: python -m srtfix in.srt [--shift MS] [--fps-from F --fps-to F] [--no-fix-overlaps] [-o out.srt]"""
import argparse
import sys

from .core import parse_srt, render_srt, repair


def main(argv=None):
    parser = argparse.ArgumentParser(prog="srtfix", description="Repair and retime .srt subtitles.")
    parser.add_argument("file", help="Input .srt file")
    parser.add_argument("--shift", type=int, default=0,
                        help="Shift all timings by this many milliseconds (may be negative)")
    parser.add_argument("--fps-from", type=float, help="Source frame rate for retiming")
    parser.add_argument("--fps-to", type=float, help="Target frame rate for retiming")
    parser.add_argument("--no-fix-overlaps", action="store_true", help="Leave overlapping cues as they are")
    parser.add_argument("-o", "--output", help="Output path (default: stdout)")
    args = parser.parse_args(argv)

    if bool(args.fps_from) != bool(args.fps_to):
        print("--fps-from and --fps-to must be given together", file=sys.stderr)
        return 2
    scale = (args.fps_from / args.fps_to) if args.fps_from else 1.0

    with open(args.file, encoding="utf-8-sig") as handle:
        text = handle.read()
    cues, skipped = parse_srt(text)
    if not cues:
        print("No cues parsed. Is this an .srt file?", file=sys.stderr)
        return 1
    fixed, report = repair(cues, shift_ms=args.shift, scale=scale,
                           fix_overlaps=not args.no_fix_overlaps)
    output = render_srt(fixed)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(output)
    else:
        sys.stdout.write(output)
    print(f"cues: {len(cues)} in, {len(fixed)} out; skipped blocks: {skipped}; "
          f"overlaps fixed: {report['overlaps_fixed']}; empty dropped: {report['dropped_empty']}",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
