import re
from datetime import date

SECTION = re.compile(
    r'^(professional |military |work )?(summary|profile|objective|experience|history|employment|'
    r'skills|education|training|qualifications|certifications|awards)\b',
    re.IGNORECASE,
)
REFERENCES = re.compile(r'^references\b', re.IGNORECASE | re.MULTILINE)

CONTACT = [
    re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+'),
    re.compile(r'(https?://|www\.)\S+|linkedin\.com/\S+', re.IGNORECASE),
    re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
    re.compile(r'(\+?1[\s.-]?)?\(?\b\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b'),
    re.compile(
        r'\b\d{1,6}\s+([A-Z][a-z]+\s){1,3}(St|Street|Ave|Avenue|Rd|Road|Blvd|Dr|Drive|Ln|Lane|Ct|Court|Way|Pl|Place)\b\.?'
    ),
]

MONTHS = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
MONTH = (r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?|'
         r'Sept?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?')
YEAR = r'(?:19[5-9]\d|20[0-4]\d)'
FULL_DATE = (rf'(?:\d{{1,2}}\s?{MONTH}\s?(?:\d{{4}}|\d{{2}})|{MONTH}\s+(?:\d{{1,2}},?\s+)?{YEAR}|'
             rf'\d{{1,2}}/\d{{1,2}}/\d{{2,4}}|\d{{1,2}}/{YEAR})')
ONE_DATE = rf'(?:{FULL_DATE}|{YEAR})'
RANGE = re.compile(
    rf'\b(?P<start>{ONE_DATE})\s*(?:-|–|—|to|through|until)\s*(?P<end>{ONE_DATE}|present|current|now|today)\b',
    re.IGNORECASE,
)
SINGLE_DATE = re.compile(rf'\b{FULL_DATE}\b', re.IGNORECASE)
# Leaves amounts like "2000 flight hours" or "$2010" alone
BARE_YEAR = re.compile(
    rf'(?<![$\d,.])\b{YEAR}\b(?!\+|,\d|\s*(?:hours|hrs|miles|mi|lbs|pounds|people|personnel|soldiers|sailors|'
    rf'marines|airmen|troops|vehicles|items|meters|feet|ft|gallons|tons|patients|flight))',
    re.IGNORECASE,
)

STATE_ABBR = ('AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|'
              'NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY|DC')
REGIONS = ('Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|Florida|Georgia|Hawaii|'
           'Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|'
           'Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|New Hampshire|New Jersey|New Mexico|'
           'New York|North Carolina|North Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|Rhode Island|'
           'South Carolina|South Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|West Virginia|'
           'Wisconsin|Wyoming|Puerto Rico|Guam|Okinawa|Afghanistan|Iraq|Kuwait|Syria|Qatar|Bahrain|'
           'United Arab Emirates|UAE|Saudi Arabia|Jordan|Djibouti|Somalia|Africa|Middle East|Germany|Italy|'
           'Spain|United Kingdom|England|Belgium|Poland|Romania|Turkey|Kosovo|Bosnia|Japan|South Korea|'
           'Korea|Philippines|Honduras|Diego Garcia|Europe|Asia|Pacific')
CAPS = r"[A-Z][\w'-]+"
CITY_STATE = re.compile(rf'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+){{0,2}},\s*(?:{STATE_ABBR}|{REGIONS})\b')
IN_STATE = rf'(?:,\s*(?:{STATE_ABBR}|{REGIONS})\b)?'
PLACES = [
    re.compile(r'\bUSN?S\s+[A-Z][\w.]*(?:\s+[A-Z][\w.]*){0,2}(?:\s*\([A-Z]{2,4}[- ]?\d+\))?'),
    re.compile(rf'\b(?:Fort|Ft\.|Camp|Joint Base|Naval (?:Air )?Station|Naval Base|NAS|'
               rf'Marine Corps (?:Base|Air Station)|MCAS|MCB)\s+{CAPS}(?:\s+{CAPS})?{IN_STATE}'),
    re.compile(rf'\b{CAPS}(?:\s+{CAPS})?\s+(?:Air Force Base|AFB|Air Base|Army Airfield|Naval Base|'
               rf'Space Force Base|SFB){IN_STATE}'),
    re.compile(r'\b(?:JBLM|JBSA|JBER|JBPHH|JBAB|JBMDL|JBLE|JBCC)\b'),
    CITY_STATE,
    re.compile(rf'\b(?:{REGIONS})\b'),
]

SCHOOL = re.compile(
    rf'\b(?:{CAPS}\s+){{1,5}}(?:University|College|Institute|High School)\b(?:\s+of\s+{CAPS}(?:\s+{CAPS})?)?'
    rf'|\bUniversity of\s+{CAPS}(?:\s+{CAPS})?'
)
OPERATION = re.compile(rf'\bOperation\s+{CAPS}(?:\s+{CAPS})?(?:\s+(?:and|&)\s+{CAPS}(?:\s+{CAPS})?)?')
UNIT = re.compile(
    r'\b(?P<v>\d+(?:st|nd|rd|th)|\d+-\d+)\s+(?:[A-Z][\w-]*\s+){0,3}'
    r'(?:Battalion|Brigade|Regiment|Division|Squadron|Company|Platoon|Group|Wing|Fleet|Corps|Infantry|'
    r'Cavalry|Armor|Artillery|Airborne|Ranger|Aviation|Engineers?|Marines|MEU|MEF|BN|BDE|SQN|CAV|IN|ID|AD)\b'
)

RANKS = ('PVT|PV2|PFC|SPC|CPL|SGT|SSG|SFC|MSG|1SG|SGM|CSM|WO1|CW[2-5]|2LT|1LT|CPT|MAJ|LTC|COL|BG|MG|LTG|GEN|'
         'SN|PO[1-3]|CPO|SCPO|MCPO|ENS|LTJG|LT|LCDR|CDR|CAPT|ADM|LCpl|Cpl|Sgt|SSgt|GySgt|MSgt|1stSgt|MGySgt|'
         'SgtMaj|Capt|Maj|LtCol|Col|Amn|A1C|SrA|TSgt|SMSgt|CMSgt|Private|Specialist|Corporal|Sergeant|'
         'Captain|Lieutenant|Major|Colonel|General|Commander|Admiral|Ensign|Chief|Seaman|Airman|Mr|Mrs|Ms|Dr')
NAME_WORD = r"(?:[A-Z][a-z]+(?:[-'][A-Z][a-z]+)?|[A-Z]\.)"
RANKED_NAME = re.compile(rf'\b(?:{RANKS})\.?\s+(?P<v>{NAME_WORD}(?:\s+{NAME_WORD}){{0,2}})')
NOT_NAMES = {
    'First', 'Class', 'Major', 'Master', 'Staff', 'Senior', 'Technical', 'Gunnery', 'Petty', 'Warrant', 'Command',
    'Squad', 'Team', 'Platoon', 'Section', 'Company', 'Battalion', 'Brigade', 'Division', 'Unit', 'Leader',
    'Officer', 'Commander', 'Chief', 'Instructor', 'Recruiter', 'Drill', 'Operations', 'Supply', 'Logistics',
    'Medical', 'Maintenance', 'Infantry', 'Engineer', 'Army', 'Navy', 'Marine', 'Marines', 'Air', 'Force',
    'Corps', 'Guard', 'Reserve', 'Sergeant', 'Lieutenant', 'Colonel', 'General', 'Captain', 'Specialist',
    'Private', 'Corporal', 'Seaman', 'Airman', 'Admiral', 'Ensign', 'Promoted', 'Served', 'Retired',
    'Selected', 'Select', 'Board', 'Course', 'School', 'Academy', 'Leadership', 'Advisor', 'Manager',
    'In', 'At', 'With', 'The', 'And', 'Of', 'For', 'To', 'As', 'On',
}


def is_contact(line):
    return any(p.search(line) for p in CONTACT)


def split_header(text):
    lines = text.splitlines()
    for i, line in enumerate(lines[:10]):
        if SECTION.match(line.strip()):
            return '\n'.join(lines[:i]).strip(), '\n'.join(lines[i:]).strip()

    # No section headings, so take the name line and any contact lines under it
    end = 0
    for i, line in enumerate(lines[:10]):
        stripped = line.strip()
        first = not '\n'.join(lines[:i]).strip()
        if not stripped or is_contact(stripped) or (first and len(stripped.split()) <= 4):
            end = i + 1
        else:
            break
    return '\n'.join(lines[:end]).strip(), '\n'.join(lines[end:]).strip()


def split_references(text):
    match = REFERENCES.search(text)
    if not match:
        return text, ''
    return text[:match.start()].strip(), text[match.start():].strip()


def parse_date(text):
    text = text.lower()
    if text in ('present', 'current', 'now', 'today'):
        return date.today().year, date.today().month

    year = re.search(r'(19|20)\d{2}', text)
    if year:
        year = int(year.group(0))
    else:
        year = int(re.findall(r'\d{2}', text)[-1])
        year += 1900 if year > 50 else 2000

    month = next((i + 1 for i, name in enumerate(MONTHS) if name in text), None)
    if month is None and '/' in text:
        month = int(text.split('/')[0])
    return year, month


def length(start, end):
    (sy, sm), (ey, em) = parse_date(start), parse_date(end)
    if sm is None or em is None:
        years, months = ey - sy, 0
    else:
        years, months = divmod((ey * 12 + em) - (sy * 12 + sm), 12)

    parts = []
    if years:
        parts.append(f'{years} year' + ('s' if years > 1 else ''))
    if months:
        parts.append(f'{months} month' + ('s' if months > 1 else ''))
    return ' '.join(parts) or 'under a month'


def header_places(header):
    return [m.group(0).split(',')[0] for m in CITY_STATE.finditer(header)]


def scrub(text, names=(), places=()):
    hidden = {}

    def hide(kind, note=None):
        def replace(match):
            group = next((g for g in ('v', 'p') if match.groupdict().get(g)), None)
            value = match.group(group) if group else match.group(0)
            if kind == 'NAME':
                words = value.split()
                while words and words[-1] in NOT_NAMES:
                    words.pop()
                if not words or words[0] in NOT_NAMES:
                    return match.group(0)
                value = ' '.join(words)

            key = str(len(hidden) + 1)
            hidden[key] = value
            label = f'[{kind} {key}: {note(match)}]' if note else f'[{kind} {key}]'
            start = (match.start(group) if group else match.start()) - match.start()
            whole = match.group(0)
            return whole[:start] + label + whole[start + len(value):]
        return replace

    for pattern in CONTACT:
        text = pattern.sub(hide('CONTACT'), text)
    for name in names:
        text = re.sub(rf'\b{re.escape(name)}\b', hide('NAME'), text)
    for place in places:
        text = re.sub(rf'\b{re.escape(place)}\b', hide('PLACE'), text)
    text = RANGE.sub(hide('DATES', lambda m: length(m.group('start'), m.group('end'))), text)
    text = SINGLE_DATE.sub(hide('DATE'), text)
    text = BARE_YEAR.sub(hide('DATE'), text)
    text = SCHOOL.sub(hide('SCHOOL'), text)
    text = OPERATION.sub(hide('OPERATION'), text)
    for pattern in PLACES:
        text = pattern.sub(hide('PLACE'), text)
    text = UNIT.sub(hide('UNIT'), text)
    text = RANKED_NAME.sub(hide('NAME'), text)
    return text, hidden


def restore(text, hidden):
    return re.sub(r'\[[A-Z]+ (\d+)[^\]]*\]', lambda m: hidden.get(m.group(1), m.group(0)), text)
