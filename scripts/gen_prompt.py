import random, sys
from xml.sax.saxutils import escape

CMDS = [
    "adb connect 192.168.43.1:5555",
    "cd flagon && ./gradlew build",
    "bun --smol dev",
    'git commit -am "it works now"',
]
X0, CW = 40, 9            # first char x, monospace advance at 15px
START_PAUSE, HOLD, GAP = 1.2, 1.8, 0.7
ERASE = 0.035
rnd = random.Random(7)

events = []               # (time, cursor_col)
chars = []                # (col, ch, t_on, t_off)
t = START_PAUSE
events.append((0, 0))
for cmd in CMDS:
    ons = []
    for i, ch in enumerate(cmd):
        t += rnd.uniform(0.05, 0.13) + (0.15 if ch == " " and rnd.random() < 0.4 else 0)
        ons.append(t); events.append((t, i + 1))
    t += HOLD
    offs = [0] * len(cmd)
    for i in range(len(cmd) - 1, -1, -1):
        t += ERASE; offs[i] = t; events.append((t, i))
    for i, ch in enumerate(cmd):
        if ch != " ":
            chars.append((i, ch, ons[i], offs[i]))
    t += GAP
T = t
p = lambda s: f"{s / T * 100:.3f}%"

css = [f".c{{opacity:0;animation:{T:.2f}s steps(1,end) infinite}}",
       ".cur{animation:blink 1.1s steps(1,end) infinite}",
       "@keyframes blink{0%,55%{opacity:1}55.01%,100%{opacity:0}}"]
body = []
for n, (col, ch, on, off) in enumerate(chars):
    css.append(f"@keyframes k{n}{{0%{{opacity:0}}{p(on)}{{opacity:1}}{p(off)}{{opacity:0}}100%{{opacity:0}}}}")
    body.append(f'<text class="c" style="animation-name:k{n}" x="{X0 + col * CW}" y="20">{escape(ch, {chr(34): "&quot;"})}</text>')
frames = "".join(f"{p(tt)}{{transform:translateX({c * CW}px)}}" for tt, c in events)
css.append(f"@keyframes mv{{{frames}100%{{transform:translateX(0px)}}}}")
css.append(f".mv{{animation:mv {T:.2f}s steps(1,end) infinite}}")

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="880" height="34" viewBox="0 0 880 34">
  <style>
    {chr(10).join("    " + c for c in css).strip()}
  </style>
  <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="15">
    <text x="0" y="20"><tspan fill="#22c55e">&gt;</tspan><tspan fill="#52525b" dx="8">~/</tspan></text>
    <g fill="#d4d4d8">
      {(chr(10) + "      ").join(body)}
    </g>
  </g>
  <g class="mv"><rect class="cur" x="{X0}" y="8" width="8" height="16" fill="#a1a1aa" /></g>
</svg>
'''
open(sys.argv[1], "w").write(svg)
print(f"cycle {T:.2f}s, {len(chars)} glyphs")
