#!/usr/bin/env python3
import argparse
import datetime as dt
import glob
import pathlib
import re
import shutil
import sys

MARKER_START = "/* OPENCLAW_TELEGRAM_STATUS_FOOTER_START */"
MARKER_END = "/* OPENCLAW_TELEGRAM_STATUS_FOOTER_END */"

SNIPPET = f"""
{MARKER_START}
const __ocShouldAppendStatusFooter =
  activeSessionEntry?.chatType !== \"group\" &&
  activeSessionEntry?.chatType !== \"channel\" &&
  (activeSessionEntry?.lastChannel === \"telegram\" || activeSessionEntry?.channel === \"telegram\");

if (__ocShouldAppendStatusFooter) {{
  const __ocTotalTokens = resolveFreshSessionTotalTokens(activeSessionEntry);

  const __ocStatusFooter = [
    `🧠 Model: ${{providerUsed && modelUsed ? `${{providerUsed}}/${{modelUsed}}` : modelUsed || \"unknown\"}}`,
    `📊 Context: ${{formatTokens(
      typeof __ocTotalTokens === \"number\" && Number.isFinite(__ocTotalTokens) && __ocTotalTokens > 0
        ? __ocTotalTokens
        : null,
      contextTokensUsed ?? activeSessionEntry?.contextTokens ?? null
    )}}`
  ].join(\" \" );

  finalPayloads = appendUsageLine(finalPayloads, __ocStatusFooter);
}}
{MARKER_END}
""".strip("\n")

PATTERN = re.compile(
    r"(if\s*\(\s*responseUsageLine\s*\)\s*finalPayloads\s*=\s*appendUsageLine\(\s*finalPayloads\s*,\s*responseUsageLine\s*\);)",
    flags=re.M,
)


def patch_file(path: pathlib.Path, dry_run: bool) -> bool:
    content = path.read_text(encoding="utf-8")

    if MARKER_START in content:
        print(f"[skip] already patched: {path}")
        return False

    m = PATTERN.search(content)
    if not m:
        print(f"[skip] needle not found: {path}")
        return False

    replacement = m.group(1) + "\n\n" + SNIPPET
    new_content = content[: m.start()] + replacement + content[m.end() :]

    if dry_run:
        print(f"[dry-run] would patch: {path}")
        return True

    ts = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = path.with_suffix(path.suffix + f".bak.telegram-footer.{ts}")
    shutil.copy2(path, backup)
    path.write_text(new_content, encoding="utf-8")
    print(f"[ok] patched: {path}")
    print(f"[ok] backup : {backup}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Patch OpenClaw reply dist files to append Telegram status footer.")
    parser.add_argument("--dist", default="/usr/lib/node_modules/openclaw/dist", help="OpenClaw dist directory")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, do not write")
    args = parser.parse_args()

    files = sorted(glob.glob(str(pathlib.Path(args.dist) / "reply-*.js")))
    if not files:
        print("[err] no reply-*.js found", file=sys.stderr)
        return 2

    changed = 0
    for fp in files:
        if patch_file(pathlib.Path(fp), dry_run=args.dry_run):
            changed += 1

    if changed == 0:
        print("[done] no files changed")
    else:
        print(f"[done] changed files: {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
