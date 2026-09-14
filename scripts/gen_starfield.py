# hyperspace starfield for hero.svg -- rewrites in place

# each star flies along a ray from the vanishing point: x = R / z
import bisect
import math
import random
import re

CYCLE = 24         # seconds
CENTER = (440, 135)
STARS = 520
BUCKETS = 12       # depth phases; stars in a bucket share keyframes
LOOPS = 3          # full depth passes per cycle
PEAK = 18          # hyperspace speed, times cruise
Z_NEAR, Z_FAR = 0.04, 1.0
R_MIN, R_MAX = 20, 300
BLUR = 0.02      # streak = distance covered in this much of the cycle
DIM = 0.6          # keep it behind the content


def smoothstep(a, b, x):
    t = min(1, max(0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def speed(u):  # cruise -> ease in -> hyperspace -> ease out -> still -> cruise
    up, down, back = smoothstep(0.40, 0.55, u), smoothstep(0.62, 0.80, u), smoothstep(0.90, 1.0, u)
    return (1 + PEAK * up) * (1 - down) + back


# travelled depth over the cycle, normalized to LOOPS passes
N = 4000
ZR = Z_FAR - Z_NEAR
S = [0]
for i in range(N):
    S.append(S[-1] + speed((i + 0.5) / N))
S = [s / S[-1] * LOOPS * ZR for s in S]


def travelled(u):
    i = min(int(u * N), N - 1)
    return S[i] + (S[i + 1] - S[i]) * (u * N - i)


def when(s):  # inverse of travelled
    i = min(bisect.bisect_left(S, s), N) - 1
    i = max(i, 0)
    return (i + (s - S[i]) / (S[i + 1] - S[i] or 1)) / N


def pct(u):
    return f"{u * 100:.3f}".rstrip("0").rstrip(".")


def num(v):
    return f"{v:.3f}".rstrip("0").rstrip(".").replace("0.", ".", 1) if abs(v) < 1 else f"{v:.2f}"


def frame(u, z):
    head = 1 / z
    blur = travelled(u) - travelled(u - BLUR) if u >= BLUR else travelled(u) + S[-1] - travelled(u - BLUR + 1)
    tail = 1 / (z + blur)
    size = min(2.2, 0.9 / math.sqrt(z))
    length = max((head - tail) * R_MIN * 2, size)
    fade = (1 - smoothstep(0.8, Z_FAR, z)) * (0.55 + 0.45 * (1 - z))
    return f"{pct(u)}%{{transform:translate({head:.3f}px)scale({num(length)},{num(size)});opacity:{num(fade)}}}"


def keyframes(k):
    offset = k / BUCKETS * ZR
    depth = lambda s: Z_FAR - (offset + s) % ZR
    points = {i / 24 for i in range(25)} | {when(j * ZR / 18) for j in range(LOOPS * 18)}
    frames = [(u, depth(travelled(u))) for u in points]
    for j in range(LOOPS + 1):  # jump back to the far plane exactly at the wrap
        u = min(when(j * ZR - offset), 1)
        if 0 < u:
            frames += [(u - 1e-5, Z_NEAR), (u, Z_FAR)]
    return f"@keyframes hs{k}{{{''.join(frame(u, max(z, Z_NEAR)) for u, z in sorted(frames))}}}"


rng = random.Random(7)
stars = []
for _ in range(STARS):
    r = R_MIN + (R_MAX - R_MIN) * rng.random() ** 1.3
    k = rng.randrange(BUCKETS)
    stars.append(
        f'<g transform="rotate({rng.uniform(0, 360):.1f}) scale({r:.1f})">'
        f'<rect class="hs{k}" x="-{num(1 / (R_MIN * 2))}" y="-{num(0.5 / r)}" width="{num(1 / (R_MIN * 2))}" '
        f'height="{num(1 / r)}"/></g>')

css = "\n      ".join(
    ["/* starfield */"]
    + [keyframes(k) for k in range(BUCKETS)]
    + [".hs rect { fill: url(#hyper); opacity: 0; transform-box: view-box; transform-origin: 0 0; }"]
    + [f".hs{k} {{ animation: hs{k} {CYCLE}s linear infinite; }}" for k in range(BUCKETS)])

svg = open("hero.svg").read()

# clear old starfields (sidescroller + previous runs)
svg = re.sub(r'\s*<(linearGradient|radialGradient) id="(streak|glow|hyper)".*?</\1>', "", svg, flags=re.S)
svg = re.sub(r"\n\s*(@keyframes (warp|drift|streak|twinkle|hs)|/\* (one 30s|motion blur|starfield)|\.(warp|deep|mid|fore|streaks|hs\d*)\b).*", "", svg)
svg = re.sub(r'  (<g class="warp">|<!-- starfield -->).*?(?=  <!-- shooting star -->)', "", svg, flags=re.S)

# shooting stars only outside hyperspace
shots = [(2, 1), (20.5, 1)]
shoot = "".join(f"{pct(t / CYCLE)}%{{transform:translateX(0);opacity:0}}{pct((t + 0.1) / CYCLE)}%{{opacity:1}}"
                f"{pct((t + d) / CYCLE)}%{{transform:translateX(340px);opacity:0}}" for t, d in shots)
svg = re.sub(r"@keyframes shoot \{\n.*?\n      \}", f"@keyframes shoot {{0%{{opacity:0}}{shoot}100%{{opacity:0}}}}", svg, flags=re.S)
svg = re.sub(r"@keyframes shoot \{0%.*", f"@keyframes shoot {{0%{{opacity:0}}{shoot}100%{{opacity:0}}}}", svg)
svg = re.sub(r"animation: shoot [^;]*;", f"animation: shoot {CYCLE}s ease-out infinite;", svg)

svg = svg.replace("\n\n    <style>",'\n\n    <linearGradient id="hyper">\n'
                  '      <stop offset="0%" stop-color="#9db8ff" stop-opacity="0" />\n'
                  '      <stop offset="100%" stop-color="#e8f0ff" stop-opacity="1" />\n'
                  "    </linearGradient>\n\n    <style>", 1)
svg = svg.replace("<style>", "<style>\n      " + css, 1)
svg = svg.replace("  <!-- shooting star -->",
                  f'  <!-- starfield -->\n  <g class="hs" transform="translate({CENTER[0]} {CENTER[1]})" opacity="{DIM}">'
                  + "".join(stars) + "</g>\n\n  <!-- shooting star -->", 1)
open("hero.svg", "w").write(svg)
