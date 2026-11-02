"""Icone de Ciel : un soleil dont les 51 rayons, de longueurs differentes, figurent les 51 scenarios ECMWF.

Ecrit icons/icon.svg (source, aussi favicon) puis rend les PNG avec Chrome headless et PIL :
icon-192.png, icon-512.png et icon-maskable-512.png (fond plein bord a bord, dessin reduit a 80 %
pour rester dans la zone sure des icones adaptatives Android).
Usage : python tools/build_icons.py   (depuis le dossier ciel)
"""
import math
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
ICONS = Path(__file__).resolve().parent.parent / 'icons'


def rays():
    out = []
    for k in range(51):
        a = k / 51 * 2 * math.pi - math.pi / 2
        n = .5 + .26 * math.sin(3 * a + 1) + .16 * math.sin(7 * a + 2.3) + .08 * math.sin(13 * a + .4)
        r0, r1 = 100, 100 + 34 + 72 * n
        c = '#ff8a5c' if n > .62 else '#ffb04a' if n > .45 else '#ffd166'
        out.append(f'<line x1="{256 + r0 * math.cos(a):.1f}" y1="{256 + r0 * math.sin(a):.1f}" '
                   f'x2="{256 + r1 * math.cos(a):.1f}" y2="{256 + r1 * math.sin(a):.1f}" stroke="{c}"/>')
    return '\n    '.join(out)


def svg(maskable):
    bg = '<rect width="512" height="512" fill="url(#bg)"/>' if maskable else '<rect width="512" height="512" rx="112" fill="url(#bg)"/>'
    scale = ' transform="translate(256 256) scale(.8) translate(-256 -256)"' if maskable else ''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0c1d45"/><stop offset="1" stop-color="#1d5aa6"/></linearGradient>
    <radialGradient id="sun" cx=".38" cy=".34" r=".8"><stop offset="0" stop-color="#ffe7a3"/><stop offset="1" stop-color="#ffaa2b"/></radialGradient>
  </defs>
  {bg}
  <g{scale}>
   <g stroke-width="7.5" stroke-linecap="round">
    {rays()}
   </g>
   <circle cx="256" cy="256" r="76" fill="url(#sun)"/>
  </g>
</svg>
'''


def render(svg_text, out, sizes):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / 'i.svg').write_text(svg_text, encoding='utf-8')
        (tmp / 'i.html').write_text('<html><body style="margin:0;background:transparent">'
                                    '<img src="i.svg" style="display:block;width:1024px;height:1024px"></body></html>', encoding='utf-8')
        subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--default-background-color=00000000',
                        '--window-size=1024,1024', f'--screenshot={tmp / "big.png"}', (tmp / 'i.html').as_uri()],
                       check=True, capture_output=True, timeout=60)
        big = Image.open(tmp / 'big.png').convert('RGBA')
        for size, name in sizes:
            big.resize((size, size), Image.LANCZOS).save(ICONS / name, optimize=True)
            print(name, size)


if __name__ == '__main__':
    (ICONS / 'icon.svg').write_text(svg(False), encoding='utf-8')
    render(svg(False), ICONS, [(192, 'icon-192.png'), (512, 'icon-512.png')])
    render(svg(True), ICONS, [(512, 'icon-maskable-512.png')])
