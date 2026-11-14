#!/usr/bin/env python3
"""Render README.md as a GitHub profile page preview (desktop + mobile).

Usage:
    python3 preview.py            # writes preview.html next to this file
    python3 preview.py --out /path/to/preview.html

Handy before pushing a profile README: GitHub itself needs the README inside a
repo named <username>/<username>, so the preview shows the same layout locally.
"""

import html
import re
import sys

CSS = """
:root { --bg:#0d1117; --panel:#161b22; --border:#30363d; --text:#c9d1d9; --muted:#8b949e; --link:#58a6ff; }
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--text);
  font: 14px/1.6 -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; }
a { color: var(--link); text-decoration: none; }
a:hover { text-decoration: underline; }
body.light { --bg:#ffffff; --panel:#f6f8fa; --border:#d0d7de; --text:#1f2328; --muted:#57606a; --link:#0969da; }
body.light .name, body.light .markdown h1, body.light .markdown h2 { color:#1f2328; }
body.light .markdown pre { background:#f6f8fa; }
.wrap { max-width: 1280px; margin: 0 auto; padding: 24px; }
.head { border-bottom: 1px solid var(--border); padding-bottom: 16px; margin-bottom: 24px;
  display:flex; align-items:center; gap:12px; color:var(--muted); font-size:13px; }
.head .dot { width:10px; height:10px; border-radius:50%; background:#3fb950; }
.cols { display:flex; gap:24px; align-items:flex-start; }
.side { width: 296px; flex: 0 0 296px; }
.avatar { width: 296px; height: 296px; border-radius: 6px; border: 1px solid var(--border); }
.name { font-size: 20px; font-weight: 600; margin: 12px 0 2px; color:#f0f6fc; }
.login { color: var(--muted); margin-bottom: 12px; }
.bio { margin: 12px 0; }
.stat { color: var(--muted); margin: 6px 0; font-size: 13px; }
.stat strong { color: var(--text); font-weight: 600; }
.side ul { list-style:none; margin:10px 0; padding:0; border-top:1px solid var(--border); }
.side li { padding: 8px 0; border-bottom: 1px solid var(--border); font-size: 13px; color: var(--muted); }
.main { flex: 1 1 auto; min-width: 0; }
.card { border: 1px solid var(--border); border-radius: 6px; background: var(--panel); }
.card .top { padding: 12px 16px; border-bottom: 1px solid var(--border); color: var(--muted); font-size: 13px;
  display:flex; justify-content:space-between; gap:12px; }
.markdown { padding: 24px 32px; }
.markdown h1 { font-size: 26px; margin: 0 0 12px; padding-bottom: 8px; border-bottom: 1px solid var(--border); color:#f0f6fc; }
.markdown h2 { font-size: 20px; margin: 24px 0 10px; padding-bottom: 6px; border-bottom: 1px solid var(--border); color:#f0f6fc; }
.markdown p { margin: 0 0 12px; }
.markdown ul { margin: 0 0 12px; padding-left: 22px; }
.markdown li { margin: 4px 0; }
.markdown pre { background:#0a0c10; border:1px solid var(--border); border-radius:6px;
  padding:12px 14px; overflow-x:auto; margin:0 0 12px; font-size:13px; line-height:1.5; }
.markdown code { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
.markdown img { vertical-align: middle; }
.badges a { margin-right: 4px; }
.note { color: var(--muted); font-size: 12px; margin-top: 18px; }
@media (max-width: 760px) {
  .wrap { padding: 14px; }
  .cols { flex-direction: column; gap: 16px; }
  .side { width: 100%; }
  .avatar { width: 120px; height: 120px; }
  .markdown { padding: 16px; }
  .markdown h1 { font-size: 22px; }
}
"""

MD = """<div class=\"head\"><span class=\"dot\"></span> github.com/chozzz &rarr; profile preview (not pushed)</div>"""


def to_html(md_text):
    out = []
    lines = md_text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line:
            i += 1
            continue
        if line.startswith('```'):
            code = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                code.append(html.escape(lines[i].rstrip()))
                i += 1
            i += 1
            out.append('<pre><code>' + '\n'.join(code) + '</code></pre>')
            continue
        if line.startswith('## '):
            out.append('<h2>' + inline(line[3:]) + '</h2>')
        elif line.startswith('# '):
            out.append('<h1>' + inline(line[2:]) + '</h1>')
        elif line.startswith('- '):
            items = []
            while i < len(lines) and lines[i].startswith('- '):
                items.append('<li>' + inline(lines[i][2:]) + '</li>')
                i += 1
            out.append('<ul>' + ''.join(items) + '</ul>')
            continue
        elif line.startswith('<a href='):
            row = []
            while i < len(lines) and lines[i].startswith('<a href='):
                row.append(lines[i].rstrip())
                i += 1
            out.append('<p class="badges">' + ''.join(row) + '</p>')
            continue
        else:
            out.append('<p>' + inline(line) + '</p>')
        i += 1
    return '\n'.join(out)


LINK = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')


def inline(text):
    # Escape first, then apply markdown on the escaped text so HTML tags survive.
    text = html.escape(text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    parts = []
    pos = 0
    for m in LINK.finditer(text):
        start = m.start()
        end = m.end()
        parts.append(text[pos:start])
        parts.append('<a href="' + m.group(2) + '">' + m.group(1) + '</a>')
        pos = end
    parts.append(text[pos:])
    return ''.join(parts)


def main():
    here = '/home/choz/dev/github-profile'
    src = here + '/README.md'
    if '--in' in sys.argv:
        pos = sys.argv.index('--in')
        src = sys.argv[pos + 1]
    out = here + '/preview.html'
    if '--out' in sys.argv:
        pos = sys.argv.index('--out')
        out = sys.argv[pos + 1]
    readme = open(src).read()
    body = to_html(readme)
    side = """
    <div class="side">
      <img class="avatar" src="https://avatars.githubusercontent.com/u/5223310?v=4" alt="avatar">
      <div class="name">Vadi Taslim</div>
      <div class="login">chozzz</div>
      <p class="bio">Self-hosted agents that do real work. Agent OS on my own hardware, and production software for businesses.</p>
      <div class="stat"><strong>15</strong> followers &middot; <strong>4</strong> following</div>
      <div class="stat">Sydney, Australia</div>
      <div class="stat">hireable</div>
      <ul>
        <li>vargos-labs</li>
        <li>vaditaslim.com</li>
        <li>x.com/vaditaslim</li>
      </ul>
    </div>
    """
    card = """
    <div class="main">
      <div class="card">
        <div class="top"><span>chozzz / README</span><span>README.md</span></div>
        <div class="markdown">""" + MD + body + """</div>
      </div>
      <p class="note">Badges load from shields.io, so the preview needs internet. GitHub renders the same markdown inside the chozzz/chozzz repo.</p>
    </div>
    """
    light = '--light' in sys.argv
    doc = '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>chozzz profile preview</title><style>' + CSS + '</style></head><body' + (' class="light"' if light else '') + '><div class="wrap"><div class="cols">' + side + card + '</div></div></body></html>'
    open(out, 'w').write(doc)
    print('wrote', out)


if __name__ == '__main__':
    main()
