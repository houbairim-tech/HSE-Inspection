from pathlib import Path
import shutil

root = Path("source")
android_root = root / "android"
if not android_root.exists():
    raise SystemExit("Android project not found in source archive")

candidates = list(root.rglob("index.html"))
ranked = []
for p in candidates:
    try:
        s = p.read_text(errors="ignore")
    except Exception:
        continue
    score = sum(marker.lower() in s.lower() for marker in [
        "JCC", "PZ_FORMS", "jccOpen", "pzOpen", "jccSave", "pzSave"
    ])
    ranked.append((score, p, s))

ranked.sort(key=lambda item: item[0], reverse=True)
for score, p, _ in ranked[:10]:
    print(f"HTML candidate score={score}: {p}")

# Prefer the full desktop application source when present, otherwise use
# the strongest original HTML candidate. Never inject replacement forms.
if not ranked or ranked[0][0] < 4:
    raise SystemExit("Could not identify original JCC + personnel source HTML")

score, original, html = ranked[0]
target = android_root / "app/src/main/assets/index.html"
target.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(original, target)

for marker in ["PZ_FORMS", "jccOpen", "pzOpen", "jccSave", "pzSave"]:
    if marker.lower() not in html.lower():
        raise SystemExit("Original JCC/Personnel module verification failed: " + marker)

print("Using original application:", original)
print("Original JCC and Gestion du personnel form code preserved.")
