#!/usr/bin/env python3
"""Builds the page published to the player's live URL (https://claude.ai/artifact/ThXBVmarX3k8SK47Hhh8qA).

The artifact host wraps the page in its own document skeleton, so this is a fragment:
  a fixed head (title, theme colour, fonts)
  + css/style.css without its first three lines (the skeleton already sets the safe-area padding and img width)
  + the body of index.html
  + js/portraits.js and js/story_art.js
  + js/game.js
It is the same game as index.html / jills-kitchen-single-file.html; only the wrapper differs.

  python3 tools/build_artifact.py            # writes ../jills-kitchen.html (next to the project folder)
  python3 tools/build_artifact.py OUT.html   # somewhere else

Publish to the SAME live URL every release (docs/RELEASE_CHECKLIST.md): saves live with that URL.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(ROOT), 'jills-kitchen.html')
HEAD = ('<title>Jill\'s Kitchen</title>\n'
        '<meta name="theme-color" content="#1E2B2F">\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link href="https://fonts.googleapis.com/css2?family=Young+Serif&family=Figtree:wght@400;500;600;700;800&display=swap" rel="stylesheet">\n')
BODY_END = '<script src="js/portraits.js"></script>'


def read(rel):
    with open(os.path.join(ROOT, rel), encoding='utf-8') as f:
        return f.read()


def build():
    css = '\n'.join(read('css/style.css').split('\n')[3:])
    idx = read('index.html')
    assert idx.count('<body>') == 1 and idx.count(BODY_END) == 1, 'index.html layout changed: check the body slice'
    body = idx[idx.index('<body>') + len('<body>'):idx.index(BODY_END)]
    art = read('js/portraits.js') + '\n' + read('js/story_art.js')
    js = read('js/game.js')
    out = HEAD + '<style>\n' + css + '\n</style>\n' + body + '<script>\n' + art + '\n</script>\n<script>\n' + js + '\n</script>\n'
    for need in ('id="lightbox"', 'id="regcard"', 'id="tkMore"', 'id="storyNote"', 'id="roomTabs"'):
        assert out.count(need) == 1, f'{need} should appear once in the page'
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(out)
    print(f'{OUT}: {len(out) // 1024} KB, {out.count("<script>")} scripts')


if __name__ == '__main__':
    build()
