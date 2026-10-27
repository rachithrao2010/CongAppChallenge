"""Builds data/occupations.json and data/military.json from the O*NET downloads.

Usage: python tools/build_data.py <folder with the O*NET files>

The folder needs occupation_data.csv, related_occupations.csv and job_zones.csv from
https://www.onetcenter.org/database.html, plus milx0724.csv from the military crosswalk
at https://www.onetcenter.org/crosswalks.html.
"""
import csv
import json
import sys
from pathlib import Path

BRANCHES = {'A': 'Army', 'N': 'Navy', 'P': 'Navy', 'F': 'Air Force', 'M': 'Marine Corps', 'C': 'Coast Guard', 'H': 'Space Force'}

# The crosswalk sends combat and tactical jobs to these military-only occupations, so point them at civilian ones
MILITARY_ONLY = {
    '55-1011.00': ['53-2011.00', '53-2012.00', '53-2021.00', '53-2022.00'],
    '55-1012.00': ['53-2022.00', '53-2021.00', '11-1021.00', '49-3011.00'],
    '55-1013.00': ['11-1021.00', '33-1012.00', '11-9161.00', '13-1199.07'],
    '55-1014.00': ['11-1021.00', '11-9161.00', '13-1199.07', '13-1111.00'],
    '55-1015.00': ['11-9161.00', '11-1021.00', '13-1111.00', '33-3021.06'],
    '55-1016.00': ['11-1021.00', '33-1012.00', '11-9161.00', '13-1199.07', '11-3131.00'],
    '55-1017.00': ['11-9161.00', '13-1199.07', '33-3021.06', '11-1021.00', '33-3021.00'],
    '55-1019.00': ['11-1021.00', '11-9161.00', '13-1199.07', '13-1111.00'],
    '55-2011.00': ['53-1041.00', '53-2022.00', '49-3011.00', '53-2012.00'],
    '55-2012.00': ['33-1012.00', '33-1091.00', '47-5032.00', '11-1021.00'],
    '55-2013.00': ['33-1012.00', '33-1091.00', '11-9161.00', '11-1021.00'],
    '55-3011.00': ['53-2031.00', '53-2022.00', '49-3011.00', '53-2012.00'],
    '55-3012.00': ['53-2022.00', '49-3011.00', '47-2073.00'],
    '55-3013.00': ['53-3032.00', '49-3042.00', '47-2073.00', '33-3051.00', '33-9032.00'],
    '55-3014.00': ['47-5032.00', '53-3032.00', '49-3042.00', '33-9032.00', '47-2073.00'],
    '55-3015.00': ['43-5031.00', '15-1231.00', '53-2021.00', '15-1244.00'],
    '55-3016.00': ['33-3051.00', '33-2011.00', '33-3012.00', '33-9032.00', '33-3021.00', '33-3051.04'],
    '55-3018.00': ['33-3021.00', '33-3021.06', '33-3051.00', '11-9161.00', '13-1199.07', '29-2042.00'],
    '55-3019.00': ['33-3021.06', '33-9032.00', '33-3051.00', '43-5031.00'],
}


def read(path):
    with open(path, encoding='utf-8-sig', errors='replace', newline='') as f:
        return list(csv.DictReader(f))


def main(src):
    src = Path(src)
    out = Path(__file__).resolve().parent.parent / 'data'
    out.mkdir(exist_ok=True)

    zones = {r['O*NET-SOC Code']: int(r['Job Zone']) for r in read(src / 'job_zones.csv')}
    occupations = {
        r['O*NET-SOC Code']: {'title': r['Title'], 'description': r['Description'], 'zone': zones.get(r['O*NET-SOC Code']), 'related': []}
        for r in read(src / 'occupation_data.csv')
    }

    for r in sorted(read(src / 'related_occupations.csv'), key=lambda r: int(r['Index'])):
        code, related = r['O*NET-SOC Code'], r['Related O*NET-SOC Code']
        if code in occupations and related in occupations and len(occupations[code]['related']) < 10:
            occupations[code]['related'].append(related)

    for code, civilian in MILITARY_ONLY.items():
        missing = [c for c in civilian if c not in occupations]
        if missing:
            sys.exit(f'{code} points at codes O*NET no longer has: {missing}')
        occupations[code]['related'] = civilian

    # "All Other" occupations have no related list, so fall back to their neighbors in the same group
    for code, occ in occupations.items():
        if not occ['related']:
            group = code[:5]
            occ['related'] = [c for c in occupations if c.startswith(group) and c != code and 'All Other' not in occupations[c]['title']][:10]

    military = {}
    for r in read(src / 'milx0724.csv'):
        if r['STATUS'] != 'A' or r['SVC'] not in BRANCHES:
            continue
        codes = [r[f'ONET{i}'] for i in range(1, 5) if r[f'ONET{i}'] in occupations]
        if codes:
            military.setdefault(BRANCHES[r['SVC']], []).append([r['MOC'], r['MOC_TITLE'], r['MPC'], codes])

    (out / 'occupations.json').write_text(json.dumps(occupations, separators=(',', ':')), encoding='utf-8')
    (out / 'military.json').write_text(json.dumps(military, separators=(',', ':')), encoding='utf-8')
    print(f'{len(occupations)} occupations, {sum(len(v) for v in military.values())} military jobs')


if __name__ == '__main__':
    main(sys.argv[1])
