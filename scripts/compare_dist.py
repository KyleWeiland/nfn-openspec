"""Compare two builds of the Astro site.

The regression check for renderer changes (Astro upgrades, template edits): it
answers "did the pages change, and how?" for a 19k-page build that nobody can
eyeball. Pass two existing dist/ directories, or two git refs to build first.

    python compare_dist.py site/dist-before site/dist-after
    python compare_dist.py --build main HEAD
    python compare_dist.py --build main HEAD --sample 500 --strict

What it reports, in order:

  1. Paths: files only in one build (missing or new pages, renamed assets).
  2. Assets: size of every file under _assets/ with the content hash in its
     name normalised, plus totals per extension, so a jump in shipped JS is
     visible.
  3. Visible text: the rendered text of every common HTML page, after stripping
     tags, scripts and styles. Any difference here is a content regression.
  4. Markup: the tag skeleton of every common HTML page (tag names and
     attribute names, values dropped). Differences are grouped by their diff
     signature, so a template change that touches 18,000 article pages shows as
     one group with a sample, not 18,000 lines.
  5. Inline code: the set of distinct inline <script> and <style> bodies across
     the whole build, so a new runtime script or a changed scoped style stands
     out once rather than per page.

Normalised before comparing: hashed asset filenames, Astro's scoped-style
hashes (data-astro-cid-*, astro-* classes), and relative timestamps such as
"3h ago", which depend on build time.

Exit status: 1 when the path sets differ or any visible text differs; with
--strict, also when any markup or inline code differs. 0 otherwise.
"""

import argparse
import difflib
import hashlib
import html
import random
import re
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# --- normalisation ---------------------------------------------------------

ASSET_HASH = re.compile(r"(/_assets/[^\"'\s()]*?\.)[A-Za-z0-9_-]{6,12}(\.(?:css|js|mjs))")
ASSET_FILE_HASH = re.compile(r"\.[A-Za-z0-9_-]{6,12}(\.(?:css|js|mjs))$")
ASTRO_CID = re.compile(r"(data-astro-cid-)[a-z0-9]{6,10}")
ASTRO_CLASS = re.compile(r"\bastro-[a-z0-9]{6,10}\b")
REL_TIME = re.compile(r"\b(?:\d+[mhd] ago|just now)\b")
SCRIPT_BLOCK = re.compile(r"<script\b[^>]*>(.*?)</script>", re.S | re.I)
STYLE_BLOCK = re.compile(r"<style\b[^>]*>(.*?)</style>", re.S | re.I)
TAG = re.compile(r"<(/?)([a-zA-Z][a-zA-Z0-9-]*)([^>]*)>")
ATTR = re.compile(r"([a-zA-Z_:][-a-zA-Z0-9_:.]*)(?:\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s\"'>]+))?")
WS = re.compile(r"\s+")

# Attribute values that are structural rather than per-page: kept in the skeleton.
KEEP_VALUES = {"rel", "type", "name", "property", "http-equiv", "charset", "lang", "as"}


def normalise(text):
    text = ASSET_HASH.sub(r"\1HASH\2", text)
    text = ASTRO_CID.sub(r"\1HASH", text)
    text = ASTRO_CLASS.sub("astro-HASH", text)
    text = REL_TIME.sub("REL_TIME", text)
    return text


def visible_text(norm):
    body = SCRIPT_BLOCK.sub(" ", norm)
    body = STYLE_BLOCK.sub(" ", body)
    body = TAG.sub(" ", body)
    return WS.sub(" ", html.unescape(body)).strip()


def skeleton(norm):
    """One line per tag: name plus attribute names, with a few structural values."""
    lines = []
    for closing, name, attrs in TAG.findall(norm):
        if closing:
            lines.append(f"</{name.lower()}>")
            continue
        parts = []
        for m in ATTR.finditer(attrs):
            attr = m.group(1).lower()
            full = m.group(0)
            if attr in KEEP_VALUES and "=" in full:
                value = full.split("=", 1)[1].strip().strip("\"'")
                parts.append(f"{attr}={value}")
            else:
                parts.append(attr)
        parts.sort()
        lines.append(f"<{name.lower()} {' '.join(parts)}>".replace(" >", ">"))
    return lines


def line_diff(a, b):
    """-/+ lines between two line lists. autojunk is off because a page repeats the
    same tags dozens of times, which difflib's heuristic would otherwise treat as noise
    and misalign into one huge block."""
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal":
            continue
        out.extend("-" + l for l in a[i1:i2])
        out.extend("+" + l for l in b[j1:j2])
    return out


def signature(diff):
    """Group key for a diff: the set of distinct changed lines, so pages that differ in
    the same way but a different number of times (20 articles vs 3) land together."""
    return hashlib.sha1("\n".join(sorted(set(diff))).encode()).hexdigest()[:10]


def inline_code(norm):
    scripts = {WS.sub(" ", s).strip() for s in SCRIPT_BLOCK.findall(norm) if s.strip()}
    styles = {WS.sub(" ", s).strip() for s in STYLE_BLOCK.findall(norm) if s.strip()}
    return scripts, styles


# --- build -----------------------------------------------------------------

def build_ref(ref, keep):
    """Build the site at a git ref in a temporary worktree; return its dist/ path."""
    tmp = Path(tempfile.mkdtemp(prefix=f"nfn-dist-{re.sub(r'[^A-Za-z0-9]+', '-', ref)}-"))
    print(f"building {ref} in {tmp}", flush=True)
    subprocess.run(["git", "worktree", "add", "--detach", str(tmp), ref], cwd=REPO_ROOT, check=True)
    site = tmp / "site"
    try:
        subprocess.run("npm ci --no-audit --no-fund", cwd=site, shell=True, check=True)
        subprocess.run("npm run build", cwd=site, shell=True, check=True)
    except subprocess.CalledProcessError:
        subprocess.run(["git", "worktree", "remove", "--force", str(tmp)], cwd=REPO_ROOT)
        raise
    dist = site / "dist"
    if keep:
        print(f"keeping worktree {tmp}", flush=True)
        return dist, None
    return dist, tmp


def remove_worktree(tmp):
    if tmp is None:
        return
    subprocess.run(["git", "worktree", "remove", "--force", str(tmp)], cwd=REPO_ROOT)
    shutil.rmtree(tmp, ignore_errors=True)


# --- comparison ------------------------------------------------------------

def long_path(p):
    """Windows refuses paths over 260 characters unless they carry the \\\\?\\ prefix.
    Article slugs are up to 100 bytes, so a dist/ under a deep directory needs it."""
    p = Path(p).resolve()
    if sys.platform == "win32" and not str(p).startswith("\\\\?\\"):
        return Path("\\\\?\\" + str(p))
    return p


def list_files(dist):
    return {p.relative_to(dist).as_posix(): p for p in dist.rglob("*") if p.is_file()}


def asset_key(rel):
    return ASSET_FILE_HASH.sub(r".HASH\1", rel)


def fmt_bytes(n):
    return f"{n:,} B"


def compare(dist_a, dist_b, sample, strict, show):
    files_a, files_b = list_files(dist_a), list_files(dist_b)
    problems = []
    strict_problems = []

    # 1. paths
    only_a = sorted(set(files_a) - set(files_b))
    only_b = sorted(set(files_b) - set(files_a))
    common = sorted(set(files_a) & set(files_b))
    html_common = [p for p in common if p.endswith(".html")]
    print("== Paths ==")
    print(f"before: {len(files_a):,} files ({sum(1 for p in files_a if p.endswith('.html')):,} html)")
    print(f"after:  {len(files_b):,} files ({sum(1 for p in files_b if p.endswith('.html')):,} html)")
    assets_only_a = [p for p in only_a if p.startswith("_assets/")]
    assets_only_b = [p for p in only_b if p.startswith("_assets/")]
    pages_only_a = [p for p in only_a if p not in assets_only_a]
    pages_only_b = [p for p in only_b if p not in assets_only_b]
    for label, items in (("only in before", pages_only_a), ("only in after", pages_only_b)):
        if items:
            print(f"{label}: {len(items):,}")
            for p in items[:show]:
                print(f"  {p}")
            if len(items) > show:
                print(f"  ... {len(items) - show:,} more")
    if pages_only_a or pages_only_b:
        problems.append("page paths differ")
    elif not only_a and not only_b:
        print("identical path set")

    # 2. assets
    print("\n== Assets (_assets/, hashes normalised) ==")
    sizes_a = {asset_key(p): files_a[p].stat().st_size for p in files_a if p.startswith("_assets/")}
    sizes_b = {asset_key(p): files_b[p].stat().st_size for p in files_b if p.startswith("_assets/")}
    for key in sorted(set(sizes_a) | set(sizes_b)):
        a, b = sizes_a.get(key), sizes_b.get(key)
        if a == b:
            print(f"  {key}: {fmt_bytes(a)}")
        elif a is None:
            print(f"  {key}: new, {fmt_bytes(b)}")
        elif b is None:
            print(f"  {key}: removed, was {fmt_bytes(a)}")
        else:
            print(f"  {key}: {fmt_bytes(a)} -> {fmt_bytes(b)}")
    totals = defaultdict(lambda: [0, 0])
    for key, n in sizes_a.items():
        totals[key.rsplit(".", 1)[-1]][0] += n
    for key, n in sizes_b.items():
        totals[key.rsplit(".", 1)[-1]][1] += n
    for ext, (a, b) in sorted(totals.items()):
        print(f"  total .{ext}: {fmt_bytes(a)} -> {fmt_bytes(b)}")
    if set(sizes_a) != set(sizes_b):
        strict_problems.append("asset set differs")

    # 3-5. html content
    chosen = html_common
    if sample and sample < len(html_common):
        chosen = sorted(random.Random(0).sample(html_common, sample))
    print(f"\n== HTML pages compared: {len(chosen):,} of {len(html_common):,} common ==")

    text_groups = defaultdict(list)
    text_samples = {}
    markup_groups = defaultdict(list)
    markup_samples = {}
    scripts_a, scripts_b, styles_a, styles_b = set(), set(), set(), set()

    for rel in chosen:
        raw_a = files_a[rel].read_text(encoding="utf-8", errors="replace")
        raw_b = files_b[rel].read_text(encoding="utf-8", errors="replace")
        if raw_a == raw_b:
            sa, ya = inline_code(normalise(raw_a))
            scripts_a |= sa
            scripts_b |= sa
            styles_a |= ya
            styles_b |= ya
            continue
        na, nb = normalise(raw_a), normalise(raw_b)
        sa, ya = inline_code(na)
        sb, yb = inline_code(nb)
        scripts_a |= sa
        scripts_b |= sb
        styles_a |= ya
        styles_b |= yb
        if na == nb:
            continue
        ta, tb = visible_text(na), visible_text(nb)
        if ta != tb:
            diff = line_diff(ta.split(" "), tb.split(" "))
            sig = signature(diff)
            text_groups[sig].append(rel)
            text_samples.setdefault(sig, (rel, diff))
        ka, kb = skeleton(na), skeleton(nb)
        if ka != kb:
            diff = line_diff(ka, kb)
            sig = signature(diff)
            markup_groups[sig].append(rel)
            markup_samples.setdefault(sig, (rel, diff))

    def print_groups(groups, samples):
        total = sum(len(v) for v in groups.values())
        print(f"{total:,} page(s) differ, in {len(groups)} distinct way(s)")
        for sig, pages in sorted(groups.items(), key=lambda kv: -len(kv[1])):
            rel, diff = samples[sig]
            print(f"\n  [{sig}] {len(pages):,} page(s), e.g. {rel}")
            for line in diff[:show]:
                print(f"    {line}")
            if len(diff) > show:
                print(f"    ... {len(diff) - show} more diff line(s)")

    print("\n== Visible text ==")
    if text_groups:
        problems.append("visible text differs")
        print_groups(text_groups, text_samples)
    else:
        print("identical on every compared page")

    print("\n== Markup (tag skeleton) ==")
    if markup_groups:
        strict_problems.append("markup differs")
        print_groups(markup_groups, markup_samples)
    else:
        print("identical on every compared page")

    print("\n== Inline code (distinct bodies across compared pages) ==")
    for label, a, b in (("script", scripts_a, scripts_b), ("style", styles_a, styles_b)):
        gone, new = sorted(a - b), sorted(b - a)
        print(f"{label}: {len(a)} before, {len(b)} after, {len(gone)} removed, {len(new)} added")
        if gone or new:
            strict_problems.append(f"inline {label} differs")
        for item in gone[:3]:
            print(f"  - {item[:160]}{'...' if len(item) > 160 else ''}")
        for item in new[:3]:
            print(f"  + {item[:160]}{'...' if len(item) > 160 else ''}")

    print("\n== Result ==")
    if problems:
        print("FAIL: " + "; ".join(problems))
        return 1
    if strict and strict_problems:
        print("FAIL (strict): " + "; ".join(strict_problems))
        return 1
    if strict_problems:
        print("OK with differences: " + "; ".join(strict_problems) + " (use --strict to fail on these)")
    else:
        print("OK: builds are equivalent")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Compare two builds of the Astro site.")
    parser.add_argument("a", help="dist directory, or a git ref with --build")
    parser.add_argument("b", help="dist directory, or a git ref with --build")
    parser.add_argument("--build", action="store_true", help="treat A and B as git refs and build each in a temporary worktree")
    parser.add_argument("--keep", action="store_true", help="with --build, keep the worktrees for inspection")
    parser.add_argument("--sample", type=int, default=0, help="compare only N randomly chosen HTML pages (seeded); paths and assets are always compared in full")
    parser.add_argument("--strict", action="store_true", help="also fail on markup, asset or inline-code differences")
    parser.add_argument("--show", type=int, default=12, help="max examples per section")
    args = parser.parse_args()

    cleanup = []
    try:
        if args.build:
            dist_a, tmp_a = build_ref(args.a, args.keep)
            cleanup.append(tmp_a)
            dist_b, tmp_b = build_ref(args.b, args.keep)
            cleanup.append(tmp_b)
        else:
            dist_a, dist_b = Path(args.a), Path(args.b)
        dist_a, dist_b = long_path(dist_a), long_path(dist_b)
        for d in (dist_a, dist_b):
            if not d.is_dir():
                sys.exit(f"not a directory: {d}")
        print(f"before: {dist_a}\nafter:  {dist_b}\n")
        code = compare(dist_a, dist_b, args.sample, args.strict, args.show)
    finally:
        for tmp in cleanup:
            remove_worktree(tmp)
    sys.exit(code)


if __name__ == "__main__":
    main()
