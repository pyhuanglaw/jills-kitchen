#!/usr/bin/env python3
"""Builds jills-kitchen-single-file.html from index.html + css/style.css + js/game.js.

The single file is exactly index.html with the stylesheet and the script inlined, so it
behaves the same as the multi-file version and can be opened directly (it keeps the
doctype, charset and mobile viewport tags from index.html).

  python3 tools/build_single.py          # write the single file
  python3 tools/build_single.py --check  # exit 1 if the single file is out of date
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'jills-kitchen-single-file.html')
CSS_TAG = '<link rel="stylesheet" href="css/style.css">'
JS_TAG = '<script src="js/game.js"></script>'


def read(rel):
    with open(os.path.join(ROOT, rel), encoding='utf-8') as f:
        return f.read()


def build():
    html, css, js = read('index.html'), read('css/style.css'), read('js/game.js')
    assert html.count(CSS_TAG) == 1, 'index.html must link css/style.css exactly once'
    assert html.count(JS_TAG) == 1, 'index.html must load js/game.js exactly once'
    assert '</style' not in css.lower(), 'style.css contains </style>, cannot inline'
    assert '</script' not in js.lower(), 'game.js contains </script>, cannot inline'
    return html.replace(CSS_TAG, '<style>\n' + css + '</style>').replace(JS_TAG, '<script>\n' + js + '</script>')


def main():
    out = build()
    cur = open(OUT, encoding='utf-8').read() if os.path.exists(OUT) else None
    if '--check' in sys.argv:
        if cur != out:
            print('jills-kitchen-single-file.html is OUT OF DATE — run: python3 tools/build_single.py')
            sys.exit(1)
        print('jills-kitchen-single-file.html is up to date')
        return
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write(out)
    print('wrote', os.path.relpath(OUT, ROOT), f'({len(out.encode("utf-8")) // 1024} KB)')


if __name__ == '__main__':
    main()
