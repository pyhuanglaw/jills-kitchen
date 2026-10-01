#!/usr/bin/env python3
"""Packages a release as zips for the player, from the tag (docs/RELEASE_CHECKLIST.md §6).

  python3 tools/make_release_zips.py TAG NAME EVIDENCE_DIR [EVIDENCE_DIR ...]
  e.g. python3 tools/make_release_zips.py v2.3-rc3 v23-rc3 docs/evidence/v23_late

Kinds, each zip under 25 MB (25,000,000 bytes) (a kind is split into numbered parts when it is larger):
  source    everything but the large art, the evidence and the saves
  art       the player's pictures (docs/vNN images and refs), assets/portraits/src, the full-size portrait cards
  evidence  this release's evidence folders only (earlier releases already shipped theirs)
  saves     tests/saves

Every file of the tag is in exactly one zip, except evidence from earlier releases (listed at the end). Then the
source zip is unzipped into a scratch folder and tools/build_single.py and tools/build_artifact.py are run there:
their output must be identical to the committed single file and to a page built from the tag.
Zips go next to the project folder: ../jills-kitchen-NAME-KIND[-N-label].zip
"""
import io, os, subprocess, sys, tarfile, tempfile, zipfile, hashlib, zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAG, NAME, EVID = sys.argv[1], sys.argv[2], [e.rstrip('/') + '/' for e in sys.argv[3:]]
OUTDIR = os.path.dirname(ROOT)
LIMIT = 24_000_000   # bytes (decimal MB): every zip stays under 25,000,000 bytes, whichever way "25 MB" is read
PREFIX = 'jills-kitchen-project/'
IMG = ('.png', '.jpg', '.jpeg', '.webp')


def kind(path):
    if path.startswith('tests/saves/'):
        return 'saves'
    if path.startswith('docs/evidence/'):
        return 'evidence' if any(path.startswith(e) for e in EVID) else None
    if path.startswith('assets/portraits/src/'):
        return 'art'
    if path.startswith('assets/portraits/') and path.count('/') == 2 and path.endswith('.png'):
        return 'art-cards'
    if path.startswith('docs/v') and path.lower().endswith(IMG):
        return 'art'
    return 'source'


def tag_files():
    data = subprocess.run(['git', 'archive', '--format=tar', TAG], cwd=ROOT, capture_output=True, check=True).stdout
    out = {}
    with tarfile.open(fileobj=io.BytesIO(data)) as t:
        for m in t.getmembers():
            if m.isfile():
                out[m.name] = t.extractfile(m).read()
    return out


def parts(items):
    """Greedy split by each file's compressed size (deflate, as the zip stores it), biggest first, into as few parts
    as fit under LIMIT; the written zips are checked against 25 MiB afterwards."""
    sized = [(len(zlib.compress(b, 9)), p, b) for p, b in items]
    bins = []
    for n, p, b in sorted(sized, key=lambda x: -x[0]):
        for bn in bins:
            if bn[0] + n <= LIMIT:
                bn[0] += n; bn[1].append((p, b)); break
        else:
            bins.append([n, [(p, b)]])
    return [bn[1] for bn in bins]


def write(zname, items):
    path = os.path.join(OUTDIR, zname)
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p, b in sorted(items):
            z.writestr(PREFIX + p, b)
    return path, os.path.getsize(path)


def main():
    files = tag_files()
    groups, skipped = {}, []
    for p, b in files.items():
        k = kind(p)
        if k is None:
            skipped.append(p); continue
        groups.setdefault(k, []).append((p, b))
    made = []
    for k in ('source', 'art', 'art-cards', 'evidence', 'saves'):
        items = groups.get(k, [])
        if not items:
            continue
        ps = parts(items)
        for i, part in enumerate(ps, 1):
            label = k if len(ps) == 1 else f'{k}-{i}'
            if k == 'art-cards':
                label = 'art-portrait-cards' if len(ps) == 1 else f'art-portrait-cards-{i}'
            made.append((label, len(part)) + write(f'jills-kitchen-{NAME}-{label}.zip', part))
    total = sum(len(v) for v in groups.values())
    print(f'{TAG}: {len(files)} files; in zips {total}; earlier evidence left out {len(skipped)}')
    for label, n, path, size in made:
        print(f'  {os.path.basename(path)}  {n} files  {size / 1048576:.1f} MiB')
        assert size < 25_000_000, f'{path} is over 25 MB'
    # the source zip rebuilds the game
    src = [m for m in made if m[0] == 'source'][0][2]
    with tempfile.TemporaryDirectory() as d:
        with zipfile.ZipFile(src) as z:
            z.extractall(d)
        proj = os.path.join(d, 'jills-kitchen-project')
        # the art zip's files are not needed to build; the portraits the game uses are js/portraits.js (source)
        r = subprocess.run([sys.executable, 'tools/build_single.py', '--check'], cwd=proj, capture_output=True, text=True)
        print('  build_single from the unzipped source:', (r.stdout or r.stderr).strip())
        assert r.returncode == 0
        a1 = os.path.join(d, 'from_zip.html'); subprocess.run([sys.executable, 'tools/build_artifact.py', a1], cwd=proj, check=True, capture_output=True)
        # the same page built from the tag itself
        tagdir = os.path.join(d, 'tag'); os.makedirs(tagdir)
        for p, b in files.items():
            if p.startswith(('tools/', 'js/', 'css/', 'index.html')):
                fp = os.path.join(tagdir, p); os.makedirs(os.path.dirname(fp), exist_ok=True); open(fp, 'wb').write(b)
        a2 = os.path.join(d, 'from_tag.html'); subprocess.run([sys.executable, 'tools/build_artifact.py', a2], cwd=tagdir, check=True, capture_output=True)
        h1 = hashlib.sha256(open(a1, 'rb').read()).hexdigest(); h2 = hashlib.sha256(open(a2, 'rb').read()).hexdigest()
        print('  build_artifact from the unzipped source == from the tag:', h1 == h2, h1[:12])
        assert h1 == h2
    if skipped:
        print('  earlier releases\' evidence, not in these zips:', len(skipped), 'files under',
              sorted({'/'.join(p.split('/')[:3]) for p in skipped}))


if __name__ == '__main__':
    main()
