#!/usr/bin/env python3
import argparse
import glob
import pathlib
import shutil
import sys

MARKER_START = "/* OPENCLAW_TELEGRAM_STATUS_FOOTER_START */"


def revert_file(path: pathlib.Path, dry_run: bool) -> bool:
    content = path.read_text(encoding="utf-8")
    if MARKER_START not in content:
        print(f"[skip] not patched: {path}")
        return False

    backups = sorted(glob.glob(str(path) + ".bak.telegram-footer.*"))
    if not backups:
        print(f"[err] backup not found: {path}")
        return False

    latest = pathlib.Path(backups[-1])
    if dry_run:
        print(f"[dry-run] would restore {path} <- {latest}")
        return True

    shutil.copy2(latest, path)
    print(f"[ok] restored: {path} <- {latest}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Restore OpenClaw reply dist files from latest telegram-footer backups.")
    parser.add_argument("--dist", default="/usr/lib/node_modules/openclaw/dist", help="OpenClaw dist directory")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, do not write")
    args = parser.parse_args()

    files = sorted(pathlib.Path(args.dist).glob("reply-*.js"))
    if not files:
        print("[err] no reply-*.js found", file=sys.stderr)
        return 2

    changed = 0
    for f in files:
        if revert_file(f, args.dry_run):
            changed += 1

    if changed == 0:
        print("[done] no files restored")
    else:
        print(f"[done] restored files: {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
