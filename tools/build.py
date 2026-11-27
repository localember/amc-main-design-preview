#!/usr/bin/env python3
"""Build the AMC main-site design preview (GitHub Pages, noindex, forms off)."""
from __future__ import annotations

import base64
import html
import json
import re
import shutil
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COVE = Path("/Users/johnowens/tmp/amc-build/amc-copperascove-design-preview")
CATALOG = Path("/Users/johnowens/localember/tools/bd-generator/catalog")
LIVE = Path("/tmp/amc-live")
ORIG_HOME = ROOT / "index.html"

HUB_PHONE = "2544106888"
HUB_DISPLAY = "(254) 410-6888"
CITY = "Central Texas"
STATE = "TX"
TOWNS = (
    "Waco, Temple, Killeen, Copperas Cove, Georgetown, Round Rock, Taylor, "
    "Jarrell, Hewitt and surrounding Central Texas communities"
)
LEAVE = {
    "georgetown", "jarrell", "killeen", "north-waco", "round-rock",
    "taylor", "waco", "west-georgetown",
}

LOCATIONS = [
    {"name": "Copperas Cove", "short": "CC", "line1": "1856 Patriot Circle", "city": "Copperas Cove, TX 76522",
     "phone": "2542067131", "display": "(254) 206-7131",
     "preview": "https://localember.github.io/amc-copperascove-design-preview/",
     "lat": 31.1138549, "lng": -97.874032},
    {"name": "Georgetown", "short": "GT", "line1": "101 Cooperative Way #235", "city": "Georgetown, TX 78626",
     "phone": "5126300060", "display": "(512) 630-0060",
     "preview": "https://localember.github.io/amc-georgetown-design-preview/",
     "lat": 30.6120309, "lng": -97.6828412},
    {"name": "Hewitt", "short": "HE", "line1": "518 North Hewitt Drive", "city": "Hewitt, TX 76643",
     "phone": "2542350793", "display": "(254) 235-0793",
     "preview": "https://localember.github.io/amc-hewitt-design-preview/",
     "lat": 31.4716473, "lng": -97.2009552},
    {"name": "Jarrell", "short": "JA", "line1": "539 Town Center Blvd", "city": "Jarrell, TX 76537",
     "phone": "5128838048", "display": "(512) 883-8048",
     "preview": "https://localember.github.io/amc-jarrell-design-preview/",
     "lat": 30.816035, "lng": -97.6138554},
    {"name": "Killeen", "short": "KI", "line1": "900 W Central Texas Expy", "city": "Killeen, TX 76541",
     "phone": "2546344010", "display": "(254) 634-4010",
     "preview": "https://localember.github.io/amc-killeen-design-preview/",
     "lat": 31.107639, "lng": -97.746782},
    {"name": "North Waco", "short": "NW", "line1": "1139 N Loop 340", "city": "Waco, TX 76705",
     "phone": "2547998343", "display": "(254) 799-8343",
     "preview": "https://localember.github.io/amc-northwaco-design-preview/",
     "lat": 31.6034191, "lng": -97.101674},
    {"name": "Round Rock", "short": "RR", "line1": "2201 Double Creek Dr, Suite 4001", "city": "Round Rock, TX 78664",
     "phone": "5129957699", "display": "(512) 995-7699",
     "preview": "https://localember.github.io/amc-roundrock-design-preview/",
     "lat": 30.4928045, "lng": -97.6449899},
    {"name": "Taylor", "short": "TA", "line1": "816 N Main St", "city": "Taylor, TX 76574",
     "phone": "5123525285", "display": "(512) 352-5285",
     "preview": "https://localember.github.io/amc-taylor-design-preview/",
     "lat": 30.57463, "lng": -97.4100026},
    {"name": "Temple", "short": "TE", "line1": "61 N Kegley Rd", "city": "Temple, TX 76502",
     "phone": "2548992225", "display": "(254) 899-2225",
     "preview": "https://localember.github.io/amc-temple-design-preview/",
     "lat": 31.1139681, "lng": -97.3995615},
    {"name": "Waco", "short": "WA", "line1": "5000 W Waco Dr", "city": "Waco, TX 76710",
     "phone": "2545371064", "display": "(254) 537-1064",
     "preview": "https://localember.github.io/amc-waco-design-preview/",
     "lat": 31.5196923, "lng": -97.1795971},
    {"name": "West Georgetown", "short": "WG", "line1": "4887 Williams Dr #103", "city": "Georgetown, TX 78633",
     "phone": "5123167930", "display": "(512) 316-7930",
     "preview": "https://localember.github.io/amc-westgeorgetown-design-preview/",
     "lat": 30.6964798, "lng": -97.7336548},
]

STOCK = {
    "chiropractic-necessary": ("chiropractic.webp", "Chiropractor's hands applying a specific adjustment to a patient's mid-back on a treatment table."),
    "chiropractic-care-kids": ("pediatric.webp", "Clinician using a gentle two-handed hold on an infant lying on a treatment table during pediatric chiropractic care."),
    "pregnancy": ("pregnancy-chiropractic.webp", "Pregnant woman sitting on a sofa with her hands resting on her belly."),
    "kinesio-taping": ("kinesiology-taping.webp", "Clinician applying strips of kinesiology tape across a patient's shoulder."),
    "management-of-pain": ("neck-pain.webp", "Man at a desk holding the back of his neck while looking at a computer."),
    "sports-injury": ("sports-injury.webp", "Tennis player holding her elbow in discomfort on a clay court."),
    "pain-management": ("types-of-care.webp", "Chiropractor talking with a patient seated on a treatment table during a consultation."),
    "wellness-care": ("wellness.webp", "Family stretching together outdoors by a lake."),
    "acupuncture": ("acupuncture.webp", "Fine acupuncture needles prepared for a session."),
    "acupuncture-lp": ("acupuncture.webp", "Fine acupuncture needles prepared for a session."),
    "decompression": ("decompression.webp", "Patient lying on a spinal decompression table during care."),
    "weight-loss": ("weight-loss.webp", "Clinician reviewing a nutrition and weight-loss plan with a patient."),
    "corrective-therapy": ("physical-rehabilitation.webp", "Clinician guiding a patient's shoulder and arm through a mobility exercise during corrective therapy."),
    "back-pain": ("back-pain.webp", "Woman at a desk holding her lower back while working at a computer."),
    "low-back-pain": ("back-pain.webp", "Woman at a desk holding her lower back while working at a computer."),
    "neck-pain": ("neck-pain.webp", "Man at a desk holding the back of his neck while looking at a computer."),
    "sciatica": ("sciatica.webp", "Woman standing at a desk, leaning forward and holding her lower back."),
    "headaches-migraines": ("headaches.webp", "Woman sitting on a sofa holding both temples with her eyes closed."),
    "scoliosis": ("scoliosis.webp", "Clinician examining a patient's back, with a spine illustration overlaid on the torso."),
    "car-accident": ("auto-accident.webp", "Driver in a car holding the side of her neck in discomfort."),
    "disc-injury": ("disc-injury.webp", "Man in a maroon shirt standing beside a sofa, holding his lower back with both hands."),
    "whiplash": ("whiplash.webp", "Man kneeling between two cars after a collision, holding the back of his neck."),
    "work-injury": ("work-injury.webp", "Warehouse worker in a safety vest holding his lower back while standing next to a crate."),
    "arm-leg-pain": ("extremity-pain.webp", "Man standing indoors holding his forearm with the other hand."),
    "carpal-tunnel": ("carpal-tunnel.webp", "Person at a desk holding one wrist with the other hand beside a laptop."),
    "knee-pain": ("knee-pain.webp", "Runner on a walkway leaning forward and holding one knee."),
    "shoulder-pain": ("shoulder-pain.webp", "Woman indoors holding a blue ice pack against her shoulder."),
    "vertigo": ("vertigo.webp", "Woman holding her head and steadying herself, with the room appearing to spin."),
}

CATALOG_PAGES = [
    ("chiropractic-necessary", "services/chiropractic.json", "Services", "General Chiropractic Care"),
    ("chiropractic-care-kids", "services/pediatric.json", "Services", "Kids Chiropractic Care"),
    ("pregnancy", "services/prenatal.json", "Services", "Prenatal Chiropractic Care"),
    ("corrective-therapy", "services/corrective-therapy.json", "Services", "Corrective Therapy"),
    ("management-of-pain", "services/management-of-pain.json", "Services", "Management of Pain"),
    ("sports-injury", "conditions/sports-injury.json", "Services", "Sports Injury"),
    ("pain-management", "services/pain-management.json", "Services", "Pain Management"),
    ("wellness-care", "services/wellness-care.json", "Services", "Wellness Care"),
    ("acupuncture", "services/acupuncture.json", "Services", "Acupuncture"),
    ("acupuncture-lp", "services/acupuncture.json", "Services", "Acupuncture"),
    ("decompression", "services/decompression.json", "Services", "Spinal Decompression"),
    ("weight-loss", "services/weight-loss.json", "Services", "Medical Weight Loss"),
    ("back-pain", "conditions/back-pain.json", "Conditions", "Back Pain"),
    ("low-back-pain", "conditions/low-back-pain.json", "Conditions", "Low Back Pain"),
    ("neck-pain", "conditions/neck-pain.json", "Conditions", "Neck Pain"),
    ("sciatica", "conditions/sciatica.json", "Conditions", "Sciatica"),
    ("headaches-migraines", "conditions/headaches.json", "Conditions", "Headaches & Migraines"),
    ("scoliosis", "conditions/scoliosis.json", "Conditions", "Scoliosis"),
    ("car-accident", "conditions/auto-injury.json", "Conditions", "Car Accident"),
    ("disc-injury", "conditions/disc-injury.json", "Conditions", "Disc Injury"),
    ("whiplash", "conditions/whiplash.json", "Conditions", "Whiplash"),
    ("work-injury", "conditions/work-injury.json", "Conditions", "Work Injury"),
    ("arm-leg-pain", "conditions/extremity-pain.json", "Conditions", "Arm and Leg Pain"),
    ("carpal-tunnel", "conditions/carpal-tunnel.json", "Conditions", "Carpal Tunnel"),
    ("knee-pain", "conditions/knee-pain.json", "Conditions", "Knee Pain"),
    ("shoulder-pain", "conditions/shoulder-pain.json", "Conditions", "Shoulder Pain"),
    ("vertigo", "conditions/vertigo.json", "Conditions", "Vertigo"),
]

SERVICES_NAV = [
    ("chiropractic-necessary/", "General Chiropractic Care"),
    ("chiropractic-care-kids/", "Kids Chiropractic Care"),
    ("pregnancy/", "Prenatal Chiropractic Care"),
    ("corrective-therapy/", "Corrective Therapy"),
    ("acupuncture/", "Acupuncture"),
    ("decompression/", "Spinal Decompression"),
    ("management-of-pain/", "Management of Pain"),
    ("sports-injury/", "Sports Injury"),
    ("https://www.anthonymassage.com/", "Massage Therapy"),
    ("pain-management/", "Pain Management"),
    ("wellness-care/", "Wellness Care"),
    ("weight-loss/", "Medical Weight Loss"),
]
CONDITIONS_NAV = [
    ("back-pain/", "Back Pain"),
    ("low-back-pain/", "Low Back Pain"),
    ("headaches-migraines/", "Headaches & Migraines"),
    ("neck-pain/", "Neck Pain"),
    ("sciatica/", "Sciatica"),
    ("scoliosis/", "Scoliosis"),
    ("car-accident/", "Car Accident"),
    ("disc-injury/", "Disc Injury"),
    ("whiplash/", "Whiplash"),
    ("work-injury/", "Work Injury"),
    ("arm-leg-pain/", "Arm and Leg Pain"),
    ("carpal-tunnel/", "Carpal Tunnel"),
    ("knee-pain/", "Knee Pain"),
    ("shoulder-pain/", "Shoulder Pain"),
    ("vertigo/", "Vertigo"),
]


def e(s: str) -> str:
    return html.escape(s or "", quote=True)


def tokens(s) -> str:
    if s is None:
        return ""
    if isinstance(s, dict):
        s = s.get("text") or s.get("body") or s.get("title") or ""
    s = str(s)
    s = s.replace("{{city}}", CITY).replace("{{state}}", STATE)
    s = s.replace("{{service_towns}}", TOWNS)
    s = s.replace("\u2014", ", ").replace("\u2013", "-")
    s = s.replace("—", ", ").replace("–", "-")
    return s


def depth_of(slug: str) -> str:
    return "" if slug in ("", ".") else "../"


def tel(phone: str) -> str:
    return f'<a href="tel:{phone}">{e(LOC_DISPLAY.get(phone, pretty_phone(phone)))}</a>'


def pretty_phone(p: str) -> str:
    d = re.sub(r"\D", "", p)
    if len(d) == 10:
        return f"({d[:3]}) {d[3:6]}-{d[6:]}"
    return p


LOC_DISPLAY = {loc["phone"]: loc["display"] for loc in LOCATIONS}


def maps_url(loc: dict) -> str:
    q = f"{loc['line1']} {loc['city']}".replace(" ", "+")
    return f"https://www.google.com/maps/search/?api=1&query={q}"


def nav_html(prefix: str) -> str:
    return f'''<nav class="nav" id="site-nav" aria-label="Main">
<div class="nd"><button type="button" class="nd-t" aria-expanded="false" aria-controls="nd-0">Meet The Team</button>
<div class="nd-m" id="nd-0"><div class="nd-g">
<a href="{prefix}us/">Meet the Chiropractors</a>
<a href="{prefix}us-acupuncturists/">Meet The Acupuncturists</a>
<a href="{prefix}us-nurse-practitioners/">Meet The Nurse Practitioners &amp; Physician Assistants</a>
<a href="{prefix}chris-price/">Meet The Owners</a>
</div></div></div>
<div class="nd"><button type="button" class="nd-t" aria-expanded="false" aria-controls="nd-1">Patients</button>
<div class="nd-m" id="nd-1"><div class="nd-g">
<a href="{prefix}medical-record-request-form/">Medical Record Request Form</a>
<a href="{prefix}special/">New Patient Specials</a>
<a href="{prefix}free-insurance-verification/">Free Insurance Verification</a>
</div></div></div>
<a href="{prefix}referral/">Referral</a>
<a href="{prefix}locations/">Locations</a>
</nav>'''


def header(prefix: str) -> str:
    return f'''<div class="preview" role="status">Design preview, not live &middot; Forms are off &middot; Not for public use</div>
<div class="util"><div class="wrap">
  <div><b>Free Insurance Verification</b> &middot; Se Habla Espa&ntilde;ol</div>
  <div class="u-right">12 locations across Central Texas &middot; <a href="tel:{HUB_PHONE}">{HUB_DISPLAY}</a></div>
</div></div>
<header class="hdr"><div class="wrap">
  <a class="logo" href="{prefix}" aria-label="Anthony Medical &amp; Chiropractic Center home"><img src="{prefix}assets/img/logo.svg" alt="Anthony Medical &amp; Chiropractic Center" width="465" height="60"></a>
  {nav_html(prefix)}
  <a class="btn btn-primary" href="{prefix}locations/">Find a Location</a>
  <button class="burger" type="button" aria-label="Menu" aria-expanded="false" aria-controls="site-nav"><span></span></button>
</div></header>
<div class="stripe" aria-hidden="true"></div>'''


def footer(prefix: str) -> str:
    svc = "".join(
        f'<li><a href="{u if u.startswith("http") else prefix + u}"'
        + (' rel="noopener" target="_blank"' if u.startswith("http") else "")
        + f">{e(n)}</a></li>"
        for u, n in SERVICES_NAV
    )
    cond = "".join(f'<li><a href="{prefix}{u}">{e(n)}</a></li>' for u, n in CONDITIONS_NAV)
    return f'''<footer>
  <div class="wrap">
    <div class="f-grid wide">
      <div><img class="logo-w" src="{prefix}assets/img/logo-white.svg" alt="Anthony Medical &amp; Chiropractic Center"><p>Anthony Medical &amp; Chiropractic Center<br>12 offices across Central Texas</p><p><a href="tel:{HUB_PHONE}"><b>{HUB_DISPLAY}</b></a></p><p>Free insurance verification. Se Habla Espa&ntilde;ol.</p></div>
      <div><h4>About</h4><ul>
        <li><a href="{prefix}us/">Meet the Chiropractors</a></li>
        <li><a href="{prefix}us-acupuncturists/">Meet The Acupuncturists</a></li>
        <li><a href="{prefix}us-nurse-practitioners/">Meet The Nurse Practitioners</a></li>
        <li><a href="{prefix}chris-price/">Meet The Owners</a></li>
        <li><a href="{prefix}locations/">All Locations</a></li>
      </ul></div>
      <div><h4>Patients</h4><ul>
        <li><a href="{prefix}special/">New Patient Specials</a></li>
        <li><a href="{prefix}free-insurance-verification/">Free Insurance Verification</a></li>
        <li><a href="{prefix}medical-record-request-form/">Medical Record Request Form</a></li>
        <li><a href="{prefix}referral/">Referral</a></li>
        <li><a href="{prefix}leave-us-a-review/">Leave Us a Review</a></li>
      </ul></div>
      <div><h4>Services</h4><ul>{svc}</ul></div>
      <div><h4>Conditions</h4><ul>{cond}</ul></div>
    </div>
    <div class="legal">
      <a href="{prefix}privacy-policy/">Privacy Policy</a>
      <a href="{prefix}terms-service/">Terms of Service</a>
      <a href="{prefix}accessibility/">Accessibility</a>
      <a href="{prefix}hipaa-privacy-policy/">HIPAA Policy</a>
      <a href="{prefix}anti-discrimination/">Anti-Discrimination</a>
      <a href="{prefix}healthcare-disclaimer/">Healthcare Disclaimer</a>
      <a href="{prefix}good-faith-estimate/">Good Faith Estimate</a>
      <a href="{prefix}texas-consumer-notice/">Texas Consumer Notice</a>
      <small>&copy; 2026 Anthony Medical &amp; Chiropractic Center. Design preview by Local Ember, not live.</small>
    </div>
  </div>
</footer>
<div class="scta" id="scta" role="region" aria-label="New patient specials and call"><div class="wrap"><a class="btn btn-primary" href="{prefix}special/">See New Patient Specials</a><a class="btn btn-ghost" href="tel:{HUB_PHONE}">Call {HUB_DISPLAY}</a></div></div>
<script src="{prefix}assets/sticky-cta.js" defer></script>
<script src="{prefix}assets/review-comments.js" defer></script>'''


def page(slug: str, title: str, desc: str, main: str) -> str:
    prefix = depth_of(slug)
    home = slug in ("", ".")
    leaflet = '<link rel="stylesheet" href="assets/vendor/leaflet/leaflet.css">\n' if home else ""
    mapjs = (
        '<script src="assets/vendor/leaflet/leaflet.js" defer></script>\n'
        '<script src="assets/loc-map.js" defer></script>\n'
        if home else ""
    )
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<meta name="googlebot" content="noindex,nofollow">
<title>Design preview, not live | {e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="icon" href="{prefix}assets/img/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}assets/site.css">
{leaflet}
<script src="{prefix}assets/nav.js" defer></script>
</head>
<body>
{header(prefix)}
<main id="top">
{main}
</main>
{footer(prefix)}
{mapjs}</body>
</html>
'''


def write_page(slug: str, title: str, desc: str, main: str) -> None:
    dest = ROOT / slug if slug not in ("", ".") else ROOT
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "index.html").write_text(page(slug, title, desc, main), encoding="utf-8")


def loc_cards() -> str:
    bits = []
    for loc in LOCATIONS:
        bits.append(
            f'<div class="loc"><h3>{e(loc["name"])}</h3>'
            f'<p>{e(loc["line1"])}<br>{e(loc["city"])}</p>'
            f'<a class="ph" href="tel:{loc["phone"]}">{e(loc["display"])}</a>'
            f'<div class="links"><a href="{e(loc["preview"])}" rel="noopener" target="_blank">Location preview</a>'
            f'<a href="{e(maps_url(loc))}" rel="noopener" target="_blank">Directions</a></div></div>'
        )
    return "\n".join(bits)


def loc_map_block() -> str:
    pins = [
        {k: loc[k] for k in ("name", "short", "line1", "city", "phone", "display", "preview", "lat", "lng")}
        for loc in LOCATIONS
    ]
    data = json.dumps(pins, separators=(",", ":"))
    return (
        '<p class="loc-note">Map mockup. Each pin is one office. The cards underneath are the same list, '
        'so you can compare the two before choosing.</p>\n'
        '    <div id="loc-map" class="loc-map" role="region" aria-label="Map of the 12 offices"></div>\n'
        f'    <script type="application/json" id="loc-map-data">{data}</script>'
    )


def aside(prefix: str) -> str:
    return f'''<aside class="aside">
  <div class="acard"><h3>Find a location</h3>
  <p>12 offices across Central Texas. Pick the one closest to you.</p>
  <a class="ph" href="tel:{HUB_PHONE}">{HUB_DISPLAY}</a>
  <a class="btn btn-primary" href="{prefix}special/">New Patient Specials</a>
  <a class="btn btn-dark" href="{prefix}locations/">All Locations</a></div>
  <div class="acard b"><h3>Patients</h3><ul>
    <li><a href="{prefix}us/">Meet the chiropractors</a></li>
    <li><a href="{prefix}special/">New patient specials</a></li>
    <li><a href="{prefix}free-insurance-verification/">Free insurance verification</a></li>
    <li><a href="{prefix}medical-record-request-form/">Medical record request</a></li>
  </ul></div>
</aside>'''


def cta_band(prefix: str, h2: str = "Call for an appointment") -> str:
    return f'''<section class="band cta"><div class="wrap">
  <div class="eyebrow" style="color:var(--orange)">We look forward to caring for you</div>
  <h2>{h2}</h2>
  <a class="phone" href="tel:{HUB_PHONE}">{HUB_DISPLAY}</a>
  <p>12 locations across Central Texas. Free insurance verification. Se Habla Espa&ntilde;ol.</p>
  <div class="ctas"><a class="btn btn-primary" href="{prefix}locations/">Find a Location</a><a class="btn btn-ghost" href="{prefix}special/">New Patient Specials</a></div>
</div></section>'''


def extract_home_images() -> dict[str, str]:
    t = ORIG_HOME.read_text(encoding="utf-8")
    uris = re.findall(r"data:image/([^;]+);base64,([A-Za-z0-9+/=]+)", t)
    names = [
        "favicon-old.webp", "logo-old.webp", "hero.webp", "about.webp",
        "cond-adjust.webp", "cond-consult.webp",
        "team-a.webp", "team-b.webp", "team-c.webp", "team-d.webp", "logo-foot.webp",
    ]
    out = {}
    img = ROOT / "assets" / "img"
    img.mkdir(parents=True, exist_ok=True)
    for i, (kind, b64) in enumerate(uris):
        name = names[i] if i < len(names) else f"extra-{i}.{kind}"
        (img / name).write_bytes(base64.b64decode(b64))
        out[name] = name
    return out


def txt(s: str) -> str:
    s = re.sub(r"<br\s*/?>", "\n", s or "", flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n+", "\n", s).strip()
    s = s.replace("\u2014", ", ").replace("\u2013", "-")
    return s


def extract_team(path: Path) -> list[dict]:
    t = path.read_text(encoding="utf-8", errors="replace")
    t = re.sub(r"<script[\s\S]*?</script>", "", t, flags=re.I)
    t = re.sub(r"<style[\s\S]*?</style>", "", t, flags=re.I)
    people = []
    titles = list(re.finditer(r'<h3 class="pp-infobox-title">([\s\S]*?)</h3>', t))
    for i, m in enumerate(titles):
        name = txt(m.group(1))
        before = t[max(0, m.start() - 3500): m.start()]
        after_end = titles[i + 1].start() if i + 1 < len(titles) else min(len(t), m.end() + 12000)
        after = t[m.end(): after_end]
        role_m = re.search(r'pp-infobox-title-prefix">([\s\S]*?)</p>', before)
        img_m = re.search(r'<img[^>]+src="([^"]+)"', before)
        alt_m = re.search(r'alt="([^"]*)"', before)
        desc = re.search(r'pp-description-wrap">([\s\S]*?)</div>', after)
        short = [txt(p) for p in re.findall(r"<p[^>]*>([\s\S]*?)</p>", desc.group(1) if desc else "")]
        short = [p for p in short if p and "Read More" not in p]
        acc = re.search(
            r'uabb-adv-accordion-content[\s\S]*?>([\s\S]*?)</div>\s*</div>',
            after,
        )
        bio = []
        if acc:
            bio = [txt(p) for p in re.findall(r"<p[^>]*>([\s\S]*?)</p>", acc.group(1))]
            bio = [p for p in bio if p]
        people.append({
            "name": name,
            "role": txt(role_m.group(1)) if role_m else "",
            "img": img_m.group(1) if img_m else "",
            "alt": alt_m.group(1) if alt_m else name,
            "short": short,
            "bio": bio,
        })
    return people


def extract_owners(path: Path) -> list[dict]:
    t = path.read_text(encoding="utf-8", errors="replace")
    people = []
    for m in re.finditer(
        r'<img[^>]+src="([^"]+)"[^>]*alt="([^"]*)"[\s\S]{0,2500}?<p class="uabb-infobox-title-prefix">([\s\S]*?)</p><h3 class="uabb-infobox-title">([\s\S]*?)</h3>',
        t,
    ):
        people.append({
            "name": txt(m.group(4)),
            "role": txt(m.group(3)),
            "img": m.group(1),
            "alt": m.group(2),
            "short": [],
            "bio": [],
        })
    note = ""
    rm = re.search(r'<div class="fl-rich-text">\s*<p>([\s\S]*?)</p>', t)
    if rm:
        note = txt(rm.group(1))
    return people, note


def slugify_name(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.lower())
    return s.strip("-")[:60]


def download_photo(url: str, dest: Path) -> str:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 1000:
        return dest.name
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 LocalEmberPreview"})
        data = urllib.request.urlopen(req, timeout=30).read()
        dest.write_bytes(data)
        return dest.name
    except Exception as ex:
        print("photo fail", url, ex)
        return ""


def save_team_photos(groups: dict[str, list[dict]]) -> None:
    folder = ROOT / "assets" / "img" / "team"
    folder.mkdir(parents=True, exist_ok=True)
    for people in groups.values():
        if isinstance(people, tuple):
            people = people[0]
        for p in people:
            url = p.get("img") or ""
            if not url:
                continue
            ext = ".webp" if ".webp" in url.lower() else ".jpg"
            fname = slugify_name(p["name"]) + ext
            got = download_photo(url, folder / fname)
            p["local"] = f"assets/img/team/{got}" if got else ""


def p_tags(paras: list[str]) -> str:
    return "".join(f"<p>{html.escape(tokens(p))}</p>" for p in paras if p)


def bio_block(p: dict, prefix: str) -> str:
    src = prefix + p["local"] if p.get("local") else prefix + "assets/img/hero-poster.svg"
    role = e(p.get("role") or "Team")
    paras = p.get("bio") or []
    short = p.get("short") or []
    seen: set[str] = set()
    ordered: list[str] = []
    for s in short + paras:
        key = re.sub(r"\s+", " ", s).strip()
        if not key or key in seen:
            continue
        seen.add(key)
        ordered.append(s)
    body = p_tags(ordered)
    return f'''<div class="bio"><img src="{e(src)}" alt="{e(p.get("alt") or p["name"])}" width="400" height="400">
<div><div class="role">{role}</div><h2>{e(p["name"])}</h2>{body}</div></div>'''


def render_block(block: dict, prefix: str, slug: str) -> str:
    t = block.get("type")
    if t == "answer":
        text = tokens(block.get("text", ""))
        label = e(block.get("label") or "The short answer")
        stock = STOCK.get(slug)
        inner = f'<div class="answer-copy"><b>{label}</b><p>{html.escape(text)}</p></div>'
        if stock:
            fn, alt = stock
            inner += f'<figure class="answer-img"><img src="{prefix}assets/stock/{fn}" alt="{e(alt)}" width="1600" height="1067"></figure>'
            return f'<div class="answer answer-with-img">{inner}</div>'
        return f'<div class="answer"><b>{label}</b><p>{html.escape(text)}</p></div>'
    if t == "lede":
        return f'<p class="lede">{html.escape(tokens(block.get("text", "")))}</p>'
    if t == "h2":
        return f'<h2>{html.escape(tokens(block.get("text", "")))}</h2>'
    if t == "h3":
        return f'<h3>{html.escape(tokens(block.get("text", "")))}</h3>'
    if t == "p":
        return f'<p>{html.escape(tokens(block.get("text", "")))}</p>'
    if t == "bullets":
        items = "".join(f"<li>{html.escape(tokens(i))}</li>" for i in block.get("items") or [])
        return f"<ul>{items}</ul>"
    if t == "costbox":
        items = "".join(f"<li>{html.escape(tokens(i))}</li>" for i in block.get("items") or [])
        note = html.escape(tokens(block.get("note") or ""))
        extra = f'<p class="note">{note}</p>' if note else ""
        return f'<div class="costbox"><ul>{items}</ul>{extra}</div>'
    if t in ("citation", "cite"):
        stat = html.escape(tokens(block.get("stat") or ""))
        text = html.escape(tokens(block.get("text") or ""))
        src = html.escape(tokens(block.get("source") or ""))
        link = block.get("link_url") or ""
        lt = e(block.get("link_text") or "")
        more = f' <a href="{e(link)}" rel="noopener" target="_blank">{lt}</a>' if link else ""
        return f'<div class="cite"><div class="stat">{stat}</div><div><p>{text}</p><small>{src}{more}</small></div></div>'
    if t in ("columns", "cols"):
        cols = block.get("columns") or block.get("items") or []
        bits = []
        for col in cols:
            if isinstance(col, dict):
                h = html.escape(tokens(col.get("heading") or col.get("title") or ""))
                body = html.escape(tokens(col.get("text") or col.get("body") or ""))
                bits.append(f"<div><h3>{h}</h3><p>{body}</p></div>")
            else:
                bits.append(f"<div><p>{html.escape(tokens(str(col)))}</p></div>")
        return f'<div class="cols">{"".join(bits)}</div>'
    if t == "timeline":
        items = block.get("items") or []
        lis = []
        for it in items:
            if isinstance(it, dict):
                h = html.escape(tokens(it.get("title") or it.get("heading") or ""))
                body = html.escape(tokens(it.get("text") or it.get("body") or ""))
                lis.append(f"<li><b>{h}</b> {body}</li>")
            else:
                lis.append(f"<li>{html.escape(tokens(str(it)))}</li>")
        return f'<ol class="steps">{"".join(lis)}</ol>'
    if t == "quote":
        q = html.escape(tokens(block.get("text") or block.get("quote") or ""))
        who = html.escape(tokens(block.get("cite") or block.get("source") or ""))
        return f"<blockquote><p>{q}</p><cite>{who}</cite></blockquote>"
    if t == "image":
        return ""
    # unknown
    if block.get("text"):
        return f'<p>{html.escape(tokens(block.get("text")))}</p>'
    return ""


def load_catalog(rel: str) -> dict | None:
    path = CATALOG / rel
    if not path.exists():
        print("missing catalog", rel)
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def catalog_main(slug: str, rel: str, crumb: str, label: str) -> tuple[str, str, str]:
    data = load_catalog(rel)
    prefix = "../"
    if not data:
        body = f'<section class="phero"><div class="wrap"><h1>{e(label)}</h1><p class="lead">Catalog file missing.</p></div></section>'
        return label, "", body
    hero = data.get("hero") or {}
    h1p = tokens(hero.get("h1_primary") or (label + " in "))
    h1s = tokens(hero.get("h1_secondary") or CITY)
    sub = tokens(hero.get("sub") or "")
    chips = "".join(f"<span>{html.escape(tokens(m))}</span>" for m in data.get("meta") or [])
    blocks = "".join(render_block(b, prefix, slug) for b in data.get("blocks") or [])
    faqs = data.get("faqs") or []
    faq_html = ""
    if faqs:
        details = []
        for i, f in enumerate(faqs):
            op = " open" if i == 0 else ""
            details.append(
                f"<details{op}><summary>{html.escape(tokens(f.get('q','')))}</summary>"
                f"<p>{html.escape(tokens(f.get('a','')))}</p></details>"
            )
        faq_html = (
            f'<section class="band"><div class="wrap"><div class="bhead">'
            f'<div class="eyebrow e-purple">Questions</div>'
            f'<h2>{html.escape(tokens(data.get("faq_heading") or "Questions we hear most"))}</h2>'
            f'</div><div class="faq-list">{"".join(details)}</div></div></section>'
        )
    related = (data.get("related") or {}).get("items") or []
    rel_html = ""
    if related:
        cards = []
        for it in related:
            href = prefix + (it.get("slug") or "") + "/"
            cards.append(
                f'<a class="svc" href="{e(href)}"><h3>{html.escape(tokens(it.get("title","")))}</h3>'
                f'<p>{html.escape(tokens(it.get("body","")))}</p><span class="more">Learn more</span></a>'
            )
        rel_html = (
            f'<section class="band tight"><div class="wrap"><div class="bhead">'
            f'<div class="eyebrow e-blue">Related</div><h2>{html.escape(tokens((data.get("related") or {}).get("heading") or "Related"))}</h2>'
            f'</div><div class="related-grid">{"".join(cards)}</div></div></section>'
        )
    title_plain = f"{h1p}{h1s}".strip()
    main = f'''<section class="phero"><div class="wrap">
<div class="crumbs"><a href="{prefix}">Home</a> / {e(crumb)} / {e(label)}</div>
<h1>{html.escape(h1p)}<em>{html.escape(h1s)}</em></h1>
<p class="lead">{html.escape(sub)}</p>
<div class="chips">{chips}</div>
<div class="ph-ctas"><a class="btn btn-primary" href="{prefix}special/">See New Patient Specials</a>
<a class="btn btn-ghost" href="tel:{HUB_PHONE}">Call {HUB_DISPLAY}</a></div>
</div></section>
<section class="band"><div class="wrap page-grid"><article class="prose">{blocks}</article>
{aside(prefix)}</div></section>
{faq_html}{rel_html}{cta_band(prefix)}'''
    desc = sub or f"{label} at Anthony Medical & Chiropractic Center in Central Texas."
    return title_plain, desc, main


def formbox(fields: list[str], btn: str) -> str:
    bits = []
    for f in fields:
        bits.append(f"<label>{e(f)}</label><input type=\"text\" disabled>")
    return (
        f'<div class="formbox" aria-disabled="true">{"".join(bits)}'
        f'<button class="btn btn-primary" type="button" disabled>{e(btn)}</button>'
        f'<p class="off">Forms are off in this design preview. Nothing is sent.</p></div>'
    )


def legal_from_cove(slug: str) -> str:
    src = COVE / slug / "index.html"
    if not src.exists():
        return f'<section class="legal-page"><div class="wrap"><h1>{e(slug)}</h1><p>Standard Local Ember policy page.</p></div></section>'
    t = src.read_text(encoding="utf-8")
    m = re.search(r'<section class="legal-page">[\s\S]*?</section>', t)
    return m.group(0) if m else f'<section class="legal-page"><div class="wrap"><h1>{e(slug)}</h1></div></section>'


def home_main(imgs: dict, team: list[dict]) -> str:
    prefix = ""
    members = []
    for p in team[:8]:
        src = p.get("local") or "assets/img/hero-poster.svg"
        members.append(
            f'<div class="member"><img src="{e(src)}" alt="{e(p.get("alt") or p["name"])}">'
            f'<h3>{e(p["name"])}</h3><a href="us/">Read full bio</a></div>'
        )
    return f'''<section class="hero">
  <div class="bg" role="img" aria-label="Chiropractic care at Anthony Medical &amp; Chiropractic Center" style="background-image:url(assets/img/hero.webp)"></div>
  <video class="bgv" autoplay muted loop playsinline preload="auto" poster="assets/img/hero.webp" aria-hidden="true" tabindex="-1"><source src="assets/video/hero.mp4" type="video/mp4"></video>
  <div class="veil"></div>
  <div class="wrap">
    <div class="eyebrow" style="color:#fff">Serving patients across Central Texas</div>
    <h1>Chiropractic, medical care and massage, <em>under one roof.</em></h1>
    <p class="lead">A team-based approach that combines chiropractic care, medical treatments, massage therapy and wellness solutions, at 12 locations from Waco to Round Rock.</p>
    <div class="ctas">
      <a class="btn btn-primary" href="special/">See New Patient Specials</a>
      <a class="btn btn-ghost" href="locations/">Find a Location</a>
    </div>
  </div>
  <div class="trust"><div class="wrap">
    <span><i>12</i> Central Texas locations</span>
    <span><b class="dot" style="background:var(--green)"></b>Free insurance verification</span>
    <span><b class="dot" style="background:var(--orange)"></b>Se Habla Espa&ntilde;ol</span>
    <span><b class="dot" style="background:var(--blue)"></b>CareCredit financing</span>
  </div></div>
</section>

<section class="band specials" id="specials">
  <div class="wrap">
    <div class="bhead">
      <div class="eyebrow e-orange">New patient specials</div>
      <h2>Start with a <span class="accent">new patient special</span></h2>
      <p>Pick the first visit that fits. Each special starts with an initial consultation.</p>
    </div>
    <div class="offer-grid">
      <article class="offer o1">
        <div class="tag">Chiropractic &amp; Massage</div>
        <div class="price"><sup>$</sup>59</div>
        <h3>Initial Consultation, Chiropractic Adjustment &amp; 30-minute Massage</h3>
        <a class="btn btn-dark" href="special/">Claim this special</a>
      </article>
      <article class="offer o2">
        <div class="tag">Chiropractic &amp; Massage</div>
        <div class="price"><sup>$</sup>89</div>
        <h3>Initial Consultation, Chiropractic Adjustment &amp; 60-minute Massage</h3>
        <a class="btn btn-dark" href="special/">Claim this special</a>
      </article>
      <article class="offer o3">
        <div class="tag">Acupuncture</div>
        <div class="price"><sup>$</sup>89</div>
        <h3>Initial Consultation, Acupuncture Session &amp; Chiropractic Adjustments or 30-minute Massage</h3>
        <div class="note">Killeen and Georgetown East only</div>
        <a class="btn btn-dark" href="special/">Claim this special</a>
      </article>
    </div>
    <p class="fine">New Patient Specials are cash-pay rates. Not valid for Medicare, Medicaid or Tricare. We take most health insurance plans and encourage you to share yours when booking as it may reduce the cost of your visit.</p>
  </div>
</section>

<section class="band about">
  <div class="wrap grid">
    <div class="pic">
      <img src="assets/img/about.webp" alt="A chiropractor in consultation with a patient">
      <div class="chip">Multiple specialties, so care is at <b>one convenient location</b>.</div>
    </div>
    <div>
      <div class="eyebrow e-green">About our clinic</div>
      <h2>One team, <span class="accent">working together</span></h2>
      <p>At Anthony Medical and Chiropractic Center, we provide a unique, team-based approach that combines chiropractic care, medical treatments, massage therapy, and wellness solutions under one roof. Our team of experienced chiropractors, massage therapists, nurse practitioners, and physician assistants collaborate to create personalized care plans designed around you, your condition, your goals, and your lifestyle.</p>
      <ul class="ticks">
        <li>Chiropractors</li><li>Massage therapists</li><li>Acupuncturists</li><li>Nurse practitioners &amp; PAs</li>
      </ul>
      <a class="btn btn-dark" href="us/">Meet Our Team</a>
    </div>
  </div>
</section>

<section class="band services" id="services">
  <div class="wrap">
    <div class="bhead">
      <div class="eyebrow e-blue">Services we offer</div>
      <h2>Medical and natural therapies, <span class="accent">working together</span></h2>
      <p>A full spectrum of care under one roof, coordinated by one team.</p>
    </div>
    <div class="svc-grid">
      <a class="svc" href="chiropractic-necessary/"><div class="ic" style="background:var(--green)">C</div><h3>Chiropractic Care</h3><p>Specific adjustments matched to what your spine needs, not a one-size-fits-all routine.</p><span class="more">Learn more</span></a>
      <a class="svc" href="https://www.anthonymassage.com/" rel="noopener" target="_blank"><div class="ic" style="background:var(--orange)">M</div><h3>Massage Therapy</h3><p>Therapeutic massage from licensed therapists, easing tight muscles so the work holds.</p><span class="more">Learn more</span></a>
      <a class="svc" href="acupuncture/"><div class="ic" style="background:var(--purple)">A</div><h3>Acupuncture</h3><p>Thin-needle acupuncture alongside chiropractic care, for muscle tension and ongoing pain.</p><span class="more">Learn more</span></a>
      <a class="svc" href="sports-injury/"><div class="ic" style="background:var(--blue)">R</div><h3>Sports Injury Rehab</h3><p>Guided exercise and movement coaching, paired with chiropractic care, so the change holds after you leave.</p><span class="more">Learn more</span></a>
      <a class="svc" href="decompression/"><div class="ic" style="background:var(--blue)">D</div><h3>Spinal Decompression</h3><p>Gentle motorised traction for the low back, easing pressure on an irritated disc or nerve.</p><span class="more">Learn more</span></a>
      <a class="svc" href="weight-loss/"><div class="ic" style="background:var(--green)">W</div><h3>Medical Weight Loss</h3><p>A coached program built on food, habits, and the metabolic picture behind them.</p><span class="more">Learn more</span></a>
      <a class="svc" href="pregnancy/"><div class="ic" style="background:var(--orange)">P</div><h3>Prenatal &amp; Pediatric</h3><p>Low-force, comfortably positioned care through pregnancy, and gentle, specific care for kids, always at a child&rsquo;s pace.</p><span class="more">Learn more</span></a>
      <a class="svc" href="wellness-care/"><div class="ic" style="background:var(--purple)">X</div><h3>Wellness Care</h3><p>Ongoing care so you keep moving well after the first episode settles.</p><span class="more">Learn more</span></a>
    </div>
  </div>
</section>

<section class="band why">
  <div class="wrap">
    <div class="bhead">
      <div class="eyebrow" style="color:var(--green)">Why our approach is different</div>
      <h2>We treat the person, <span class="accent">not just the problem</span></h2>
      <p>Combining chiropractic, medical and therapeutic expertise, so the neural, muscular and skeletal systems are cared for together.</p>
    </div>
    <div class="why-grid">
      <div class="why-item"><div class="n" style="background:var(--green)">01</div><h3>Root-Cause Focus</h3><p>We focus on correcting underlying dysfunctions, not just easing symptoms.</p></div>
      <div class="why-item"><div class="n" style="background:var(--orange)">02</div><h3>Team Collaboration</h3><p>Medical and chiropractic professionals coordinate each patient&rsquo;s care.</p></div>
      <div class="why-item"><div class="n" style="background:var(--purple);color:#fff">03</div><h3>Science-Based Therapies</h3><p>From manipulation and manual therapy to decompression, assisted stretching and corrective exercise, each treatment is chosen with research behind it.</p></div>
      <div class="why-item"><div class="n" style="background:var(--blue)">04</div><h3>Tailored Treatment Plans</h3><p>Every care plan is designed around the individual diagnosis.</p></div>
      <div class="why-item"><div class="n" style="background:var(--green)">05</div><h3>Affordable, Honest Care</h3><p>A high standard of care balanced with practical, cost-conscious options.</p></div>
      <div class="why-item"><div class="n" style="background:var(--orange)">06</div><h3>One Convenient Location</h3><p>Multiple specialties under one roof, at 12 offices across Central Texas.</p></div>
    </div>
  </div>
</section>

<section class="band cond" id="conditions">
  <div class="wrap">
    <div class="bhead">
      <div class="eyebrow e-purple">Conditions we help</div>
      <h2>Care for a wide range of <span class="accent">conditions</span></h2>
      <p>Conditions that affect mobility, comfort and overall wellness.</p>
    </div>
    <div class="pills">
      <a class="pill" href="back-pain/">Back pain</a>
      <a class="pill" href="neck-pain/">Neck pain</a>
      <a class="pill" href="sciatica/">Sciatica</a>
      <a class="pill" href="headaches-migraines/">Headaches &amp; migraines</a>
      <a class="pill" href="sports-injury/">Sports injury</a>
      <a class="pill" href="knee-pain/">Knee pain</a>
      <a class="pill" href="pregnancy/">Pregnancy</a>
    </div>
    <div class="cond-imgs">
      <figure><img src="assets/img/cond-adjust.webp" alt="Chiropractic adjustment"><figcaption>Chiropractic adjustments</figcaption></figure>
      <figure><img src="assets/img/cond-consult.webp" alt="Consultation"><figcaption>Every plan starts with a consultation</figcaption></figure>
    </div>
  </div>
</section>

<section class="band locs" id="locations">
  <div class="wrap">
    <div class="bhead">
      <div class="eyebrow e-green">Find your location</div>
      <h2>12 offices across <span class="accent">Central Texas</span></h2>
      <p>Each card opens that location&rsquo;s finished design preview. NAP and phone come from those builds.</p>
    </div>
    {loc_map_block()}
    <div class="loc-grid">{loc_cards()}</div>
    <div class="center"><a class="btn btn-dark" href="locations/">View all locations</a></div>
  </div>
</section>

<section class="band" id="team">
  <div class="wrap">
    <div class="bhead">
      <div class="eyebrow e-blue">Meet the team</div>
      <h2>Chiropractors, acupuncturists and <span class="accent">medical providers</span></h2>
      <p>Our outstanding team is here to help you reach your healthcare goals.</p>
    </div>
    <div class="team-grid">{''.join(members)}</div>
    <div class="center"><a class="btn btn-dark" href="us/">Meet the Full Team</a></div>
  </div>
</section>

<section class="band stories">
  <div class="wrap">
    <div class="bhead">
      <div class="eyebrow e-orange">Patient reviews</div>
      <h2>What patients <span class="accent">say</span></h2>
      <p>Google reviews shown on our Round Rock office site, quoted word for word.</p>
    </div>
    <div class="rev-grid">
      <figure class="rev"><div class="stars" aria-label="Google review">&#9733;&#9733;&#9733;&#9733;&#9733;</div><blockquote>Amazing care and great staff all around. I came in for 16 adjustments after my car accident and Dr Cook provided excellent care and service each time. The entire staff was extremely kind and friendly. Highly recommend.</blockquote><cite>Dylan r<small>Google review, Round Rock</small></cite></figure>
      <figure class="rev"><div class="stars" aria-label="Google review">&#9733;&#9733;&#9733;&#9733;&#9733;</div><blockquote>Erica the supervisor is awesome . She is very helpful and patient in explaining all my options . Definitely recommend the clinic to anyone with pain</blockquote><cite>Laxmi p<small>Google review, Round Rock</small></cite></figure>
      <figure class="rev"><div class="stars" aria-label="Google review">&#9733;&#9733;&#9733;&#9733;&#9733;</div><blockquote>Very friendly staff! I came in with some low back pain that limited my flexibility and movement. Dr. Mike provided information on what was causing my issues and developed a treatment plan that included chiropractic adjustments and medical messages.</blockquote><cite>Kyle B<small>Google review, Round Rock</small></cite></figure>
    </div>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div class="bhead">
      <div class="eyebrow e-purple">Frequently asked questions</div>
      <h2>Quick answers to <span class="accent">common questions</span></h2>
    </div>
    <div class="faq-list">
      <details open><summary>Do you accept insurance?</summary><p>Yes! We accept most major health insurance plans. Our team will verify your coverage and explain your benefits before your visit so you&rsquo;ll know exactly what to expect.</p></details>
      <details><summary>What should I expect during my first visit?</summary><p>Your first visit includes a detailed consultation and evaluation with one of our chiropractors. We&rsquo;ll review your health history, identify the root cause of your symptoms, and create a personalized treatment plan focused on your comfort and long-term wellness.</p></details>
      <details><summary>Do I need a referral to see a chiropractor or get a massage?</summary><p>In most cases, you don&rsquo;t need a referral! However, some insurance plans may require one from your primary care physician (PCP). If that&rsquo;s the case, our team can assist by contacting your PCP and helping with the referral process.</p></details>
      <details><summary>How often should I get adjusted?</summary><p>It depends on your condition and goals. Some patients benefit from weekly visits, while others come monthly for maintenance. Your chiropractor will recommend a plan that fits your lifestyle and helps you feel your best.</p></details>
    </div>
  </div>
</section>
{cta_band(prefix)}'''


def kinesio_main() -> str:
    prefix = "../"
    fn, alt = STOCK["kinesio-taping"]
    return f'''<section class="phero"><div class="wrap">
<div class="crumbs"><a href="{prefix}">Home</a> / Services / Kinesio Taping</div>
<h1>Kinesiology taping in <em>Central Texas</em></h1>
<p class="lead">Kinesiology taping, done as part of a chiropractic visit, with a plain account of what the strip is for and what we will not claim it does.</p>
<div class="chips"><span>Same-week new-patient visits</span><span>Put on in the office, you leave wearing it</span><span>Serving Central Texas</span></div>
<div class="ph-ctas"><a class="btn btn-primary" href="{prefix}special/">See New Patient Specials</a><a class="btn btn-ghost" href="tel:{HUB_PHONE}">Call {HUB_DISPLAY}</a></div>
</div></section>
<section class="band"><div class="wrap page-grid"><article class="prose">
<div class="answer answer-with-img"><div class="answer-copy"><b>The short answer</b><p>Kinesiology taping places a stretchy strip on the skin after we have watched how you move. Direction and stretch are chosen for that day, and the joint is supposed to keep bending. In our Central Texas offices the strip is one part of a chiropractic visit. It is not a result, and it is not something we hand you to sort out in the parking lot.</p></div>
<figure class="answer-img"><img src="{prefix}assets/stock/{fn}" alt="{e(alt)}" width="1600" height="1067"></figure></div>
<p class="lede">Colored strips are easy to oversell. This page says what the tape is, when we even consider it, what happens in the room, and what a performance study cannot promise you.</p>
<h2>What is kinesiology taping?</h2>
<p>It is a cotton strip that lengthens, with a sticky side that has to meet bare skin. Lotion, oil, sweat, and hair are the usual reasons it lets go early. Nothing goes over a break in the skin or a rash. Shape, direction, and stretch are decided in the room, not copied from a picture online.</p>
<h2>Who is it for?</h2>
<p>People usually bring a week they still have to finish. They want the joint available for that week. We talk about tape after the exam, not before it.</p>
<ul><li>Someone who wants a little steadiness for a shift, a practice, or a day on their feet, and still has to bend.</li>
<li>A shoulder, a knee, or a low back that feels unsteady in one part of its range, alongside hands-on care.</li>
<li>A return to a hobby or a sport, once the first angry day has passed.</li></ul>
<p>We do not tape a rash, a tear in the skin, or a spot that has reacted to sticky dressings. If a strip would only decorate a problem we have not looked at, it stays in the drawer.</p>
</article>{aside(prefix)}</div></section>
{cta_band(prefix)}'''


def main() -> None:
    print("extract home images")
    imgs = extract_home_images()
    print("team")
    chiros = extract_team(LIVE / "us.html")
    acus = extract_team(LIVE / "us-acupuncturists.html")
    nps = extract_team(LIVE / "us-nurse-practitioners.html")
    owners, owner_note = extract_owners(LIVE / "chris-price.html")
    groups = {"us": chiros, "acu": acus, "np": nps, "own": owners}
    print("photos", len(chiros), len(acus), len(nps), len(owners))
    save_team_photos(groups)

    print("home")
    write_page(
        ".",
        "Anthony Medical & Chiropractic Center",
        "Chiropractic, medical care, massage and acupuncture at 11 Central Texas locations.",
        home_main(imgs, chiros),
    )

    print("locations")
    loc_rows = []
    for loc in LOCATIONS:
        loc_rows.append(
            f'''<article class="loc" style="padding:24px">
            <h3>{e(loc["name"])}</h3>
            <p>{e(loc["line1"])}<br>{e(loc["city"])}</p>
            <a class="ph" href="tel:{loc["phone"]}">{e(loc["display"])}</a>
            <div class="links">
              <a href="{e(loc["preview"])}" rel="noopener" target="_blank">Open location preview</a>
              <a href="{e(maps_url(loc))}" rel="noopener" target="_blank">Get directions</a>
            </div>
            </article>'''
        )
    write_page(
        "locations",
        "Locations | Anthony Medical & Chiropractic Center",
        "12 Anthony Medical & Chiropractic Center offices across Central Texas.",
        f'''<section class="phero"><div class="wrap">
<div class="crumbs"><a href="../">Home</a> / Locations</div>
<h1>12 offices across <em>Central Texas</em></h1>
<p class="lead">Each location has its own phone, address, team and new-patient specials. These cards open the finished design preview for that office.</p>
</div></section>
<section class="band locs"><div class="wrap">
<div class="finder" aria-label="Location search (off in preview)">
<input type="text" placeholder="ZIP code (off in preview)" disabled aria-label="ZIP code">
<button class="btn btn-dark" type="button" disabled>Search</button>
</div>
<div class="loc-grid">{"".join(loc_rows)}</div>
</div></section>
{cta_band("../")}''',
    )

    print("team pages")
    write_page(
        "us",
        "Meet the Chiropractors",
        "Meet the chiropractors at Anthony Medical & Chiropractic Center.",
        f'''<section class="phero"><div class="wrap">
<div class="crumbs"><a href="../">Home</a> / Meet The Team / Chiropractors</div>
<h1>Meet the <em>chiropractors</em></h1>
<p class="lead">Names, titles, photos and bios as they appear on anthonychiro.com/us/.</p>
</div></section>
<section class="band"><div class="wrap">{"".join(bio_block(p, "../") for p in chiros)}</div></section>
{cta_band("../")}''',
    )
    write_page(
        "us-acupuncturists",
        "Meet The Acupuncturists",
        "Meet the acupuncturists at Anthony Medical & Chiropractic Center.",
        f'''<section class="phero"><div class="wrap">
<div class="crumbs"><a href="../">Home</a> / Meet The Team / Acupuncturists</div>
<h1>Meet the <em>acupuncturists</em></h1>
<p class="lead">Names, titles, photos and bios as they appear on anthonychiro.com/us-acupuncturists/.</p>
</div></section>
<section class="band"><div class="wrap">{"".join(bio_block(p, "../") for p in acus)}</div></section>
{cta_band("../")}''',
    )
    write_page(
        "us-nurse-practitioners",
        "Meet The Nurse Practitioners & Physician Assistants",
        "Meet the nurse practitioners and physician assistants at Anthony Medical & Chiropractic Center.",
        f'''<section class="phero"><div class="wrap">
<div class="crumbs"><a href="../">Home</a> / Meet The Team / Nurse Practitioners</div>
<h1>Meet the nurse practitioners &amp; <em>physician assistants</em></h1>
<p class="lead">Names, titles, photos and bios as they appear on anthonychiro.com/us-nurse-practitioners/.</p>
</div></section>
<section class="band"><div class="wrap">{"".join(bio_block(p, "../") for p in nps)}</div></section>
{cta_band("../")}''',
    )
    owner_html = "".join(bio_block(p, "../") for p in owners)
    note = f"<p>{html.escape(owner_note)}</p>" if owner_note else ""
    write_page(
        "chris-price",
        "Meet The Owners",
        "Meet the owners of Anthony Medical & Chiropractic Center.",
        f'''<section class="phero"><div class="wrap">
<div class="crumbs"><a href="../">Home</a> / Meet The Team / Owners</div>
<h1>Meet the <em>owners</em></h1>
<p class="lead">Dr. Chris Price and R. Matthew George, D.C., as they appear on anthonychiro.com/chris-price/.</p>
</div></section>
<section class="band"><div class="wrap">{owner_html}{note}
<p>Should you ever have any questions or concerns please feel free to reach out directly:
<a href="mailto:drprice@anthonychiro.com">drprice@anthonychiro.com</a>,
<a href="mailto:drgeorge@anthonychiro.com">drgeorge@anthonychiro.com</a>.</p>
</div></section>
{cta_band("../")}''',
    )

    print("specials / forms")
    write_page(
        "special",
        "New Patient Specials",
        "New patient specials at Anthony Medical & Chiropractic Center.",
        f'''<section class="phero"><div class="wrap">
<div class="crumbs"><a href="../">Home</a> / New Patient Specials</div>
<h1>New patient <em>special offers</em></h1>
<p class="lead">Each special starts with an initial consultation. Ask your nearest office which offers apply there.</p>
</div></section>
<section class="band specials"><div class="wrap">
<div class="offer-grid">
<article class="offer o1"><div class="tag">Chiropractic &amp; Massage</div><div class="price"><sup>$</sup>59</div><h3>Initial Consultation, Chiropractic Adjustment &amp; 30-minute Massage</h3><button class="btn btn-dark" type="button" disabled>Claim this special</button></article>
<article class="offer o2"><div class="tag">Chiropractic &amp; Massage</div><div class="price"><sup>$</sup>89</div><h3>Initial Consultation, Chiropractic Adjustment &amp; 60-minute Massage</h3><button class="btn btn-dark" type="button" disabled>Claim this special</button></article>
<article class="offer o3"><div class="tag">Acupuncture</div><div class="price"><sup>$</sup>89</div><h3>Initial Consultation, Acupuncture Session &amp; Chiropractic Adjustments or 30-minute Massage</h3><div class="note">Killeen and Georgetown East only</div><button class="btn btn-dark" type="button" disabled>Claim this special</button></article>
</div>
<p class="fine">New Patient Specials are cash-pay rates. Not valid for Medicare, Medicaid or Tricare. We take most health insurance plans and encourage you to share yours when booking as it may reduce the cost of your visit.</p>
<div class="page-grid" style="margin-top:48px"><div>
<h2>Request your special</h2>
{formbox(["First name","Last name","Phone","Email","Preferred location","Which special?"], "Request appointment")}
</div>{aside("../")}</div>
</div></section>
{cta_band("../")}''',
    )
    write_page(
        "medical-record-request-form",
        "Medical Record Request Form",
        "Request a copy of your health care records from Anthony Medical & Chiropractic Center.",
        f'''<section class="phero"><div class="wrap">
<div class="crumbs"><a href="../">Home</a> / Patients / Medical Record Request Form</div>
<h1>Medical record <em>request</em></h1>
<p class="lead">Request a copy of your health care records. How requests work, including what to include and the fees Texas law allows, is on our <a href="../texas-consumer-notice/" style="color:#fff;text-decoration:underline">Texas Consumer Notice</a>.</p>
</div></section>
<section class="band"><div class="wrap page-grid"><article class="prose">
{formbox(["Full name","Date of birth","Phone","Dates of service","Delivery method"], "Submit request")}
</article>{aside("../")}</div></section>
{cta_band("../")}''',
    )
    write_page(
        "referral",
        "Referral",
        "Refer a patient to Anthony Medical & Chiropractic Center.",
        f'''<section class="phero"><div class="wrap">
<div class="crumbs"><a href="../">Home</a> / Patients / Referral</div>
<h1>Send a <em>referral</em></h1>
<p class="lead">Are you a healthcare provider or an attorney&rsquo;s office? These forms let you refer patients to Anthony Medical and Chiropractic Center, Central Scheduling.</p>
</div></section>
<section class="band"><div class="wrap page-grid"><article class="prose">
<h2>Health care providers</h2>
{formbox(["Practice name","Practice phone","Patient name","Patient phone"], "Send referral")}
<h2 style="margin-top:36px">Attorney offices</h2>
{formbox(["Firm name","Firm phone","Client name","Client phone"], "Send referral")}
</article>{aside("../")}</div></section>
{cta_band("../")}''',
    )
    write_page(
        "thank-you-form",
        "Thank you",
        "Thank you for contacting Anthony Medical & Chiropractic Center.",
        f'''<section class="phero"><div class="wrap">
<div class="crumbs"><a href="../">Home</a> / Thank you</div>
<h1>Thank <em>you</em></h1>
<p class="lead">We received your message. A team member from your nearest office will be in touch. If you need us sooner, call {HUB_DISPLAY}.</p>
<div class="ph-ctas"><a class="btn btn-primary" href="../locations/">Find a Location</a></div>
</div></section>
{cta_band("../")}''',
    )
    write_page(
        "free-insurance-verification",
        "Free Insurance Verification",
        "Free insurance verification at Anthony Medical & Chiropractic Center.",
        f'''<section class="phero"><div class="wrap">
<div class="crumbs"><a href="../">Home</a> / Patients / Free Insurance Verification</div>
<h1>Free insurance <em>verification</em></h1>
<p class="lead">Share your plan and we will check your benefits before you come in, so you know what to expect.</p>
</div></section>
<section class="band"><div class="wrap page-grid"><article class="prose">
<p>Se Habla Espa&ntilde;ol. Forms are off in this design preview.</p>
{formbox(["First name","Last name","Phone","Email","Insurance carrier","Member ID"], "Request verification")}
</article>{aside("../")}</div></section>
{cta_band("../")}''',
    )
    write_page(
        "leave-us-a-review",
        "Leave Us a Review",
        "Leave a review for Anthony Medical & Chiropractic Center.",
        f'''<section class="phero"><div class="wrap">
<div class="crumbs"><a href="../">Home</a> / Leave Us a Review</div>
<h1>Leave us a <em>review</em></h1>
<p class="lead">Reviews live on each office&rsquo;s Google Business Profile. Open your location preview to find the right listing.</p>
</div></section>
<section class="band locs"><div class="wrap"><div class="loc-grid">{loc_cards()}</div></div></section>
{cta_band("../")}''',
    )
    write_page(
        "round-rock-tx",
        "Round Rock, TX",
        "Anthony Medical & Chiropractic Center in Round Rock, Texas.",
        f'''<section class="phero"><div class="wrap">
<div class="crumbs"><a href="../">Home</a> / Round Rock</div>
<h1>Chiropractor in <em>Round Rock, TX</em></h1>
<p class="lead">2201 Double Creek Dr, Suite 4001, Round Rock, TX 78664. Call (512) 995-7699.</p>
<div class="ph-ctas">
<a class="btn btn-primary" href="https://localember.github.io/amc-roundrock-design-preview/" rel="noopener" target="_blank">Open Round Rock preview</a>
<a class="btn btn-ghost" href="tel:5129957699">Call (512) 995-7699</a>
</div>
</div></section>
{cta_band("../")}''',
    )

    print("legal")
    legal_titles = {
        "privacy-policy": "Privacy Policy",
        "terms-service": "Terms of Service",
        "accessibility": "Accessibility",
        "hipaa-privacy-policy": "HIPAA Policy",
        "anti-discrimination": "Anti-Discrimination",
        "healthcare-disclaimer": "Healthcare Disclaimer",
        "good-faith-estimate": "Good Faith Estimate",
        "texas-consumer-notice": "Texas Consumer Notice",
    }
    for slug, title in legal_titles.items():
        body = legal_from_cove(slug)
        write_page(slug, title, f"{title} for Anthony Medical & Chiropractic Center.", body + cta_band("../"))

    print("kinesio")
    write_page(
        "kinesio-taping",
        "Kinesiology Taping in Central Texas",
        "Kinesiology taping at Anthony Medical & Chiropractic Center.",
        kinesio_main(),
    )

    print("catalog pages")
    for slug, rel, crumb, label in CATALOG_PAGES:
        title, desc, main_html = catalog_main(slug, rel, crumb, label)
        write_page(slug, title or label, desc, main_html)

    print("robots")
    (ROOT / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    (ROOT / "README.md").write_text(
        """# AMC main site: Design preview, not live

Ticket AMC-2026-11-26-main-site-build.
Full anthonychiro.com brand-hub preview on the Copperas Cove / Alpine AMC chrome
(Nov 25 review: button hover, live main menu minus Home, scroll-away header,
sticky bottom CTA, Short Answer stock images on service and condition pages).

- noindex,nofollow on every page and robots.txt Disallow: /
- Forms off: disabled inputs and buttons, no form actions, no tracking
- Service and condition pages use tools/bd-generator/catalog
- Locations hub links the 11 finished location previews (rows 1160-1169 + Copperas Cove + Pflugerville)
- Location subfolders already in this repo are left untouched
- Review layer: assets/review-comments.js
- Not the live site. Not sent to the client.
""",
        encoding="utf-8",
    )
    print("done")


if __name__ == "__main__":
    main()
