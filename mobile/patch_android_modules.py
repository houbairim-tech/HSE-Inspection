from pathlib import Path

root = Path("source/android")
if not root.exists():
    raise SystemExit("Android project not found in source archive")

index = root / "app/src/main/assets/index.html"
if not index.exists():
    raise SystemExit("Android index.html not found")

html = index.read_text(errors="ignore")

# The original source archive already contains the complete JCC and
# Gestion du personnel modules. Preserve those modules exactly: fields,
# options, validation, editing, filters, training controls, company
# management, checklist, actions, photos, preview/PDF and Excel export.
required_original = [
    'data-tab="jcc"',
    'data-tab="pers"',
    'id="tab-jcc"',
    'id="tab-pers"',
    'const JCC_FIELDS=',
    'const PZ_FORMS=',
    'function jccOpen',
    'function pzOpen',
    'function jccSave',
    'function pzSave',
]
for marker in required_original:
    if marker not in html:
        raise SystemExit("Original JCC/Personnel module missing: " + marker)

if 'onclick="saveIns()"' not in html:
    raise SystemExit("Inspection save button missing")
if 'onsubmit="saveForm(event)"' not in html:
    raise SystemExit("Suivi des Actions save form missing")

# Do not inject simplified replacement modules.
index.write_text(html)
print("Original JCC and Gestion du personnel modules preserved unchanged.")
