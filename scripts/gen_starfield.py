# starfield speed surge for hero.svg -- rewrites in place
import random
import re

WIDTH = 880  # px per loop (star tiles repeat at +880)
BOOST = 4.0  # peak speed = 1+BOOST times cruise
N = 400      # slices per cycle when integrating speed
STEP = 40    # keyframes per 30s cycle
WARP = 0.03  # extra scale at peak, toward the vanishing point
VANISH = (660, 135)

# name, surges per loop, streak length at peak (px)
LAYERS = [("fore", 1, 70), ("mid", 2, 34), ("deep", 4, 12)]

# star colors
PALETTE = ["#ffffff"] * 14 + ["#dbe7ff"] * 3 + ["#fff1dc"] * 2 + ["#ffcf9e"]

# extra star clumps
BAND = [("deep", 110, (0.3, 0.7), (0.12, 0.3)), ("mid", 22, (0.7, 1.1), (0.3, 0.45))]

# a few bright stars
BRIGHT = [(212, 34, "#dbe7ff"), (455, 228, "#ffffff"), (812, 150, "#ffe2bf")]


def smoothstep(a, b, x):
    t = min(1, max(0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def surge(u):  # 0 at cruise, 1 at full speed
    return smoothstep(0.35, 0.62, u) * (1 - smoothstep(0.68, 0.95, u))


# dx covered at each phase of one cycle, 0..1
dist = [0]
for i in range(N):
    dist.append(dist[-1] + 1 + BOOST * surge(i / N))
dist = [d / dist[-1] for d in dist]


def pct(u):
    return f"{u * 100:.3f}".rstrip("0").rstrip(".")


def color(cx, cy):  # same color for both tile copies
    return PALETTE[(int(float(cx)) % WIDTH * 7919 + int(float(cy)) * 104729) % len(PALETTE)]


svg = open("hero.svg").read()

# clear previous output
svg = re.sub(r"\s*@keyframes (drift|streak|blur|warp)\w*-?\w*\{.*", "", svg)
svg = re.sub(r"\s*<g class=\"streaks\">.*</g>", "", svg)
svg = re.sub(r"<(circle|rect) class=\"gen[^>]*/>", "", svg)
svg = re.sub(r'(opacity="[\d.]+") fill="#\w+"', r"\1", svg)

# no twinkle: that's atmosphere, not space
svg = re.sub(r' class="tw2?"', "", svg)
svg = re.sub(r"\s*\.tw2? +\{ animation: twinkle.*", "", svg)

# doppler-tinted streaks: blue at the star, red at the tail
svg = re.sub(
    r'<linearGradient id="streak">.*?</linearGradient>',
    '<linearGradient id="streak">\n      <stop offset="0%" stop-color="#cfe0ff" stop-opacity="0.85" />\n'
    '      <stop offset="45%" stop-color="#ffffff" stop-opacity="0.45" />\n'
    '      <stop offset="100%" stop-color="#ff8f7a" stop-opacity="0" />\n    </linearGradient>',
    svg, flags=re.S)
if 'id="glow"' not in svg:
    svg = svg.replace('    <style>', '    <radialGradient id="glow">\n      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.35" />\n'
                      '      <stop offset="100%" stop-color="#ffffff" stop-opacity="0" />\n    </radialGradient>\n\n    <style>', 1)

# gentle zoom toward the vanishing point during the surge
if 'class="warp"' not in svg:
    svg = svg.replace("  <!-- stars bg -->", '  <g class="warp">\n  <!-- stars bg -->', 1)
    svg = svg.replace("  <!-- shooting star -->", "  </g>\n\n  <!-- shooting star -->", 1)
    svg = svg.replace("      .deep { animation", f"      .warp {{ transform-box: view-box; transform-origin: {VANISH[0]}px {VANISH[1]}px; "
                      "animation: warp 30s linear infinite; }\n      .deep { animation", 1)

# generated stars, both tile copies
rng = random.Random(7)
extra = {"fore": [], "mid": [], "deep": []}
for name, count, (r0, r1), (o0, o1) in BAND:
    for _ in range(count):
        t = rng.random()
        x = t * WIDTH
        y = 250 - t * 230 + rng.gauss(0, 28)
        if 0 < y < 270:
            extra[name].append((round(x), round(y), round(rng.uniform(r0, r1), 1), round(rng.uniform(o0, o1), 2)))
for x, y, c in BRIGHT:
    for dx in (0, WIDTH):
        extra["fore"].append(
            f'<circle class="gen" cx="{x + dx}" cy="{y}" r="7" fill="url(#glow)"/>'
            f'<rect class="gen" x="{x + dx - 7}" y="{y - 0.25}" width="14" height="0.5" fill="{c}" fill-opacity="0.18"/>'
            f'<rect class="gen" x="{x + dx - 0.25}" y="{y - 5}" width="0.5" height="10" fill="{c}" fill-opacity="0.18"/>'
            f'<circle class="gen" cx="{x + dx}" cy="{y}" r="2" opacity="0.95"/>')


def add_colors(m):
    return f'{m[0][:-2]} fill="{color(m[1], m[2])}"/>'


kf = []
warp = []
for i in range(STEP + 1):
    warp.append(f"{pct(i / STEP)}%{{transform:scale({1 + WARP * surge(i / STEP):.4f})}}")
kf.append(f"@keyframes warp{{{''.join(warp)}}}")

for name, n, length in LAYERS:
    drift, streak = [], []
    for i in range(n * STEP + 1):
        u = i / (n * STEP)
        k = min(int(u * n), n - 1)
        f = u * n - k
        s = surge(f)
        x = -(k + dist[round(f * N)]) / n * WIDTH
        drift.append(f"{pct(u)}%{{transform:translateX({x:.2f}px)}}")
        streak.append(f"{pct(u)}%{{transform:scaleX({max(s * length, 0.01):.2f});opacity:{s:.3f}}}")
    kf.append(f"@keyframes drift-{name}{{{''.join(drift)}}}")
    kf.append(f"@keyframes streak-{name}{{{''.join(streak)}}}")

    # band stars go right after the group tag
    head = re.search(rf'<g class="{name}"[^>]*>', svg)
    gen = "".join(e if isinstance(e, str) else
                  f'<circle class="gen" cx="{e[0] + dx}" cy="{e[1]}" r="{e[2]}" opacity="{e[3]}"/>'
                  for e in extra[name] for dx in ((0,) if isinstance(e, str) else (0, WIDTH)))
    svg = svg[:head.end()] + gen + svg[head.end():]

    group = re.search(rf'<g class="{name}"[^>]*>(.*?)</g>', svg, re.S)
    body = re.sub(r'<circle (?:class="gen" )?cx="([\d.]+)" cy="([\d.]+)" r="[\d.]+" opacity="[\d.]+"/>', add_colors, group[1])
    svg = svg[:group.start(1)] + body + svg[group.end(1):]

    # one streak per star: 1px wide rect starting at the star, scaled out behind it
    group = re.search(rf'<g class="{name}"[^>]*>(.*?)</g>', svg, re.S)
    rects = "".join(
        f'<rect x="{cx}" y="{float(cy) - float(r):g}" width="1" height="{2 * float(r):g}" fill-opacity="{op}"/>'
        for cx, cy, r, op in re.findall(r'cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)" opacity="([\d.]+)"', group[1])
    )
    end = group.end() - len("</g>")
    svg = svg[:end] + f'  <g class="streaks">{rects}</g>\n  ' + svg[end:]

svg = svg.replace("<style>", "<style>\n      " + "\n      ".join(kf), 1)
open("hero.svg", "w").write(svg)
