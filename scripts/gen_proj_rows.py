from xml.sax.saxutils import escape
ROWS = [
    ("flagon", "webgl", "unmodified java in the browser"),
    ("desmos-ide", "math", "a dsl + ide that compiles to desmos expressions"),
    ("gradient", "ios", "offline-first grades viewer for home access center"),
    ("sortd", "daemon", "sorts your files by custom path rules, runs in the background"),
    ("OUTPOST", "game", "singleplayer 3D fps in an infinite procedural world"),
]
FONT = 'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="13"'
CW = 7.8  # monospace advance at 13px
W = 1012  # 880 * 1.15: matches the scale of the width="115%" headers on github
X_NAME, X_TAG, X_DESC = 17, 17 + 12 * CW, 17 + 20 * CW
for i, (name, tag, desc) in enumerate(ROWS):
    sel = i == 0
    bg = (f'<defs><linearGradient id="hl" x1="0" x2="1"><stop offset="0" stop-color="#1c2130" />'
          '<stop offset=".8" stop-color="#1c2130" stop-opacity="0" /></linearGradient></defs>\n'
          f'  <rect x="0" y="1" width="{W}" height="20" fill="url(#hl)" />\n'
          '  <rect x="0" y="3" width="3" height="16" fill="#22c55e" />\n  ') if sel else ''
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="22" viewBox="0 0 {W} 22">
  {bg}<g {FONT}>
    <text x="{X_NAME}" y="15" fill="{'#fafafa' if sel else '#d4d4d8'}" font-weight="700">{escape(name)}</text>
    <text x="{X_TAG}" y="15" fill="#52525b">{escape(tag)}</text>
    <text x="{X_DESC}" y="15" fill="{'#d4d4d8' if sel else '#a1a1aa'}">{escape(desc)}</text>
  </g>
</svg>
'''
    open(f"assets/p-{name.lower()}.svg", "w").write(svg)
open("assets/p-info.svg", "w").write(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="20" viewBox="0 0 {W} 20">
  <text x="{X_NAME}" y="13" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="12" fill="#52525b">{len(ROWS)}/{len(ROWS)}</text>
</svg>
''')
