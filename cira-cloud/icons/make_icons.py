import math, subprocess
CX, CY, R, W = 512, 500, 255, 118
GAP = 42
def pt(a, r=R):
    a = math.radians(a); return CX + r*math.cos(a), CY + r*math.sin(a)
x1, y1 = pt(GAP); x2, y2 = pt(-GAP)
ARC = f"M {x1:.1f} {y1:.1f} A {R} {R} 0 1 1 {x2:.1f} {y2:.1f}"
RO = R + W/2 - 4
a1x, a1y = pt(103, RO - 30); a2x, a2y = pt(160, RO - 30); apx, apy = pt(134, RO + 92)
TAIL = f"M {a1x:.1f} {a1y:.1f} L {apx:.1f} {apy:.1f} L {a2x:.1f} {a2y:.1f} Z"
def glyph(paint, extra="", grow=0):
    return (f'<g {extra}><path d="{ARC}" fill="none" stroke="{paint}" stroke-width="{W + 2*grow}" stroke-linecap="round"/>'
            f'<path d="{TAIL}" fill="{paint}" stroke="{paint}" stroke-width="{22 + 2*grow}" stroke-linejoin="round"/></g>')
def inset_tail(d):
    P = [(a1x, a1y), (apx, apy), (a2x, a2y)]
    import math
    la = math.dist(P[1], P[2]); lb = math.dist(P[0], P[2]); lc = math.dist(P[0], P[1])
    ix = (la*P[0][0] + lb*P[1][0] + lc*P[2][0]) / (la+lb+lc); iy = (la*P[0][1] + lb*P[1][1] + lc*P[2][1]) / (la+lb+lc)
    area = abs((P[1][0]-P[0][0])*(P[2][1]-P[0][1]) - (P[2][0]-P[0][0])*(P[1][1]-P[0][1])) / 2
    r = 2*area/(la+lb+lc); k = (r - d)/r
    Q = [(ix + (x-ix)*k, iy + (y-iy)*k) for x, y in P]
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in Q) + " Z"
def outline(color, bg, t=16):
    return (glyph(color) + f'<path d="{ARC}" fill="none" stroke="{bg}" stroke-width="{W - 2*t}" stroke-linecap="round"/>'
            f'<path d="{inset_tail(t - 11)}" fill="{bg}"/>')
U = 'gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="1024" y2="1024"'
DEFS = f'''<defs>
<linearGradient id="g" {U}><stop offset="0" stop-color="#4C8DFF"/><stop offset="1" stop-color="#5B3FF0"/></linearGradient>
<linearGradient id="gg" {U}><stop offset=".15" stop-color="#62A6FF"/><stop offset=".85" stop-color="#7352FF"/></linearGradient>
<linearGradient id="hl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".18"/><stop offset=".55" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="dk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2B2E37"/><stop offset="1" stop-color="#15161B"/></linearGradient>
<filter id="sh" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="14" stdDeviation="18" flood-color="#1B1060" flood-opacity=".33"/></filter>
<filter id="ol" x="-10%" y="-10%" width="120%" height="120%"><feMorphology in="SourceAlpha" operator="erode" radius="15" result="e"/><feComposite in="SourceGraphic" in2="e" operator="out"/></filter>
<filter id="st" x="-15%" y="-15%" width="130%" height="130%">
  <feMorphology in="SourceAlpha" operator="dilate" radius="15" result="d"/>
  <feFlood flood-color="#1B2A6B"/><feComposite in2="d" operator="in" result="ring"/>
  <feOffset in="ring" dx="10" dy="14" result="shadow"/>
  <feMerge><feMergeNode in="shadow"/><feMergeNode in="ring"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
</defs>'''
sq = lambda f: f'<rect width="1024" height="1024" rx="232" fill="{f}"/>'
V = {
 "main":    sq("url(#g)") + sq("url(#hl)") + glyph("#fff", 'filter="url(#sh)"'),
 "classic": '<circle cx="512" cy="512" r="512" fill="url(#g)"/><circle cx="512" cy="512" r="512" fill="url(#hl)"/>' + glyph("#fff", 'filter="url(#sh)"'),
 "fill":    sq("#4F6BFF") + glyph("#fff"),
 "outline": sq("#1E2027") + outline("#fff", "#1E2027"),
 "black":   sq("url(#dk)") + glyph("url(#gg)"),
 "white":   sq("#F4F6FB") + glyph("url(#g)"),
 "sticker": sq("#B9CCFF") + glyph("#1B2A6B", 'transform="translate(10 14)"', 16) + glyph("#1B2A6B", "", 16) + glyph("#fff"),
}
for name, body in V.items():
    open(f"{name}.svg", "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024">{DEFS}{body}</svg>')
    for size in (256, 1024):
        subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size), f"{name}.svg", "-o", f"{name}_{size}.png"], check=True)
print("ok")
