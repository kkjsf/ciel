"""Construit normales/ a partir des fiches climatologiques Meteo-France (Licence Ouverte Etalab).

Les fiches (.data) sont sur un S3 sans CORS : l'app ne peut pas les lire directement, d'ou ce
precalcul. Usage :
    python -I tools/build_normales.py <dossier de telechargement> <dossier ciel>
Sortie : <ciel>/normales/index.json (position et altitude des stations avec normales de
temperature) et <ciel>/normales/<2 premiers chiffres de l'indicatif>.json (normales et records).
Les fiches deja telechargees ne sont pas reprises : vider le dossier pour rafraichir les records.
"""
import json
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BASE = 'https://meteofrance.s3.sbg.io.cloud.ovh.net/data/synchro_ftp/REF_STATION/'
LIST = BASE + 'liste_fiches_clim.geojson'


def fetch(url, dest):
    if dest.exists() and dest.stat().st_size > 0:
        return
    for k in range(3):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                dest.write_bytes(r.read())
            return
        except Exception as e:
            if k == 2:
                print('echec', url, e)
            time.sleep(1 + k)


def values(line):
    cells = [c.strip() for c in line.split(';')[1:14]]
    out = []
    for c in cells:
        if c in ('', '-'):
            out.append(None)
        elif c == '.':
            out.append(0.0)
        else:
            try:
                out.append(float(c))
            except ValueError:
                out.append(None)
    return out


def dms(s):
    m = re.match(r"(\d+)°(\d+)'(\d+)\"([NSEW])", s.strip())
    if not m:
        return None
    v = int(m[1]) + int(m[2]) / 60 + int(m[3]) / 3600
    return round(-v if m[4] in 'SW' else v, 4)


def parse(text):
    lines = [l.rstrip() for l in text.splitlines()]
    head = next((l for l in lines if 'Indicatif' in l), None)
    if not head:
        return None
    m = re.match(r'\s*(.+?)\s+\((\w+)\)\s+Indicatif : (\w+), alt : (-?\d+)m, lat : ([^,]+), lon : ([^;]+);', head)
    if not m:
        return None
    st = {'n': m[1].strip(), 'num': m[3], 'alt': int(m[4]), 'lat': dms(m[5]), 'lon': dms(m[6])}
    period_all = re.search(r'Statistiques\s+(\d{4})-(\d{4})', '\n'.join(lines[:5]))
    default = f'{period_all[1]}-{period_all[2]}' if period_all else None

    def block(title):
        """Valeurs du bloc, periode propre au bloc, et ligne de dates des records s'il y en a."""
        for i, l in enumerate(lines):
            if l.startswith(title):
                period, j = default, i + 1
                while j < len(lines) and not lines[j].lstrip().startswith(';'):
                    p = re.search(r'p.riode (?:du \d\d-\d\d-)?(\d{4})(?:-| au \d\d-\d\d-)(\d{4})', lines[j])
                    if p:
                        period = f'{p[1]}-{p[2]}'
                    j += 1
                if j >= len(lines):
                    return None
                vals = values(lines[j])
                dates = None
                if j + 1 < len(lines) and lines[j + 1].startswith('Date'):
                    dates = [c.strip() for c in lines[j + 1].split(';')[1:13]]
                return vals, period, dates
        return None

    tx, tn = block('Température maximale (Moyenne'), block('Température minimale (Moyenne')
    if not tx or not tn or any(v is None for v in tx[0][:12] + tn[0][:12]):
        return None
    st['p'] = tx[1]
    st['tx'] = tx[0][:12]
    st['tn'] = tn[0][:12]
    rr = block('Précipitations : Hauteur moyenne mensuelle')
    if rr and all(v is not None for v in rr[0][:12]):
        st['rr'] = rr[0][:12]
    for key, title in (('hx', 'La température la plus élevée'), ('lx', 'La température la plus basse')):
        b = block(title)
        if b and b[2]:
            st[key] = b[0][:12]
            # "15-1955" -> jour et annee du record ; le mois est la colonne
            st[key + 'd'] = b[2]
            st['rp'] = b[1]
    return st


def main(dl, out):
    dl, out = Path(dl), Path(out) / 'normales'
    dl.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    fetch(LIST, dl / 'liste.geojson')
    feats = json.loads((dl / 'liste.geojson').read_text(encoding='utf-8'))['features']
    nums = [f['properties']['num'] for f in feats]
    with ThreadPoolExecutor(6) as ex:
        list(ex.map(lambda n: fetch(f'{BASE}FICHECLIM_{n}.data', dl / f'{n}.data'), nums))
    edited = None
    shards, index = {}, []
    for n in nums:
        f = dl / f'{n}.data'
        if not f.exists():
            continue
        text = f.read_text(encoding='utf-8', errors='replace')
        e = re.search(r'Edit. le : (\d\d/\d\d/\d{4})', text)
        if e:
            edited = e[1]
        st = parse(text)
        if not st or st['lat'] is None:
            continue
        index.append([st['num'], st['lat'], st['lon'], st['alt'], 1 if st['p'] == '1991-2020' else 0])
        shards.setdefault(st['num'][:2], {})[st.pop('num')] = st
    for k, v in shards.items():
        (out / f'{k}.json').write_text(json.dumps(v, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    (out / 'index.json').write_text(json.dumps({'edition': edited, 'stations': index}, separators=(',', ':')), encoding='utf-8')
    print(len(index), 'stations avec normales de temperature,', len(shards), 'fichiers, edition', edited)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
