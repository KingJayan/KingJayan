# starfield speed surge for hero.svg -- rewrites in place
import re

WIDTH = 880  # px per loop (star tiles repeat at +880)
BOOST = 4.0  # peak speed = 1+BOOST times cruise
N = 400      # slices per cycle when integrating speed
STEP = 40    # keyframes per 30s cycle

# name, surges per loop, streak length at peak (px)
LAYERS = [("fore", 1, 70), ("mid", 2, 34), ("deep", 4, 12)]


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


svg = open("hero.svg").read()
svg = re.sub(r"\s*@keyframes (drift|streak|blur)-\w+\{.*", "", svg)
svg = re.sub(r"\s*<g class=\"streaks\">.*</g>", "", svg)

kf = []
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
