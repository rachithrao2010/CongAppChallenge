import json
from pathlib import Path

DATA = Path(__file__).parent / 'data'
OCCUPATIONS = json.loads((DATA / 'occupations.json').read_text(encoding='utf-8'))
MILITARY = json.loads((DATA / 'military.json').read_text(encoding='utf-8'))
CERTS = json.loads((DATA / 'certs.json').read_text(encoding='utf-8'))

PREPARATION = {
    1: 'Little or no preparation needed',
    2: 'Some preparation needed',
    3: 'Medium preparation needed',
    4: 'Considerable preparation needed',
    5: 'Extensive preparation needed',
}
GRADES = {'E': 'Enlisted', 'O': 'Officer', 'W': 'Warrant Officer'}

LEVELS = ['Entry', 'Intermediate', 'Advanced']
for name, certs in CERTS.items():
    for cert in certs:
        cert['industry'] = name


def certs_for(code):
    # Exact job matches beat job groups, and a cert's first listed codes are the jobs it's mainly for
    found = []
    for certs in CERTS.values():
        for cert in certs:
            hits = [(i, p) for i, p in enumerate(cert['codes']) if code.startswith(p)]
            if hits:
                i, p = min(hits, key=lambda h: -len(h[1]))
                tier = 0 if len(p) >= 7 else 1 if len(p) > 3 else 2
                found.append(((tier, i, LEVELS.index(cert['level'])), cert))
    found.sort(key=lambda f: f[0])
    return [cert for _, cert in found]


def search(branch, query, limit=10):
    query = query.strip().lower()
    if not query:
        return []

    exact, starts, contains = [], [], []
    for i, (code, title, grade, _) in enumerate(MILITARY.get(branch, [])):
        item = {'id': i, 'code': code, 'title': title, 'grade': GRADES.get(grade, '')}
        lowered = code.lower()
        if lowered == query:
            exact.append(item)
        elif lowered.startswith(query):
            starts.append(item)
        elif all(word in f'{lowered} {title.lower()}' for word in query.split()):
            contains.append(item)
    return (exact + starts + contains)[:limit]


def is_lead(code):
    title = OCCUPATIONS[code]['title']
    return any(word in title for word in ('Supervisors', 'Managers', 'Directors'))


# Supervisor and manager jobs, keyed by the jobs O*NET lists as related to them
LEADS = {}
for lead in filter(is_lead, OCCUPATIONS):
    for c in OCCUPATIONS[lead]['related']:
        LEADS.setdefault(c, []).append(lead)


def usable(code):
    occ = OCCUPATIONS[code]
    return not code.startswith('55-') and 'All Other' not in occ['title'] and occ['zone'] != 1


def match(branch, index, led_people, limit=8):
    code, _, grade, links = MILITARY[branch][index]
    leader = led_people or grade in ('O', 'W')

    picks = {}
    for link in filter(usable, links):
        picks.setdefault(link, f'Listed for {code} in the military crosswalk')
    # Hand-mapped paths for military-only jobs go before O*NET's looser "related" lists
    for link in sorted(links, key=lambda c: not c.startswith('55-')):
        parent = OCCUPATIONS[link]['title']
        reason = f'A common civilian path from {parent}' if link.startswith('55-') else f'Related to {parent}'
        related = list(filter(usable, OCCUPATIONS[link]['related']))
        if leader and not link.startswith('55-'):
            related.sort(key=lambda c: -(OCCUPATIONS[c]['zone'] or 0))
        for c in related:
            picks.setdefault(c, reason)

    if leader:
        leads = {}
        for c in [c for c in list(picks)[:limit] if not is_lead(c)]:
            for lead in filter(usable, LEADS.get(c, [])):
                leads.setdefault(lead, f'A leadership role related to {OCCUPATIONS[c]["title"]}')
        leads = {c: r for c, r in leads.items() if c not in picks}
        picks = dict(list(picks.items())[:2]) | dict(list(leads.items())[:3]) | dict(list(picks.items())[2:])

    return [
        {
            'code': c,
            'title': OCCUPATIONS[c]['title'],
            'description': OCCUPATIONS[c]['description'],
            'preparation': PREPARATION.get(OCCUPATIONS[c]['zone'], ''),
            'certs': bool(certs_for(c)),
            'reason': reason,
            'url': f'https://www.onetonline.org/link/summary/{c}',
        }
        for c, reason in list(picks.items())[:limit]
    ]
