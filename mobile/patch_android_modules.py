from pathlib import Path
import shutil

root = Path("source")
android_root = root / "android"
if not android_root.exists():
    raise SystemExit("Android project not found in source archive")

# The source archive can contain multiple HTML copies. Use the ORIGINAL
# complete application page (the one containing the original JCC and
# Gestion du personnel modules), not a simplified Android-only page.
candidates = list(root.rglob("index.html"))
original = None
for p in candidates:
    try:
        s = p.read_text(errors="ignore")
    except Exception:
        continue
    if all(marker in s for marker in [
        "JCC", "Gestion du personnel", "PZ_FORMS", "jccOpen", "pzOpen"
    ]):
        original = p
        break

if original is None:
    raise SystemExit("Complete original index.html with JCC and Personnel modules was not found")

target = android_root / "app/src/main/assets/index.html"
target.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(original, target)

# Preserve the original application logic and all original fields/options.
html = target.read_text(errors="ignore")
for marker in [
    "PZ_FORMS", "jccOpen", "pzOpen", "jccSave", "pzSave",
    "JCC", "Gestion du personnel"
]:
    if marker not in html:
        raise SystemExit("Original module verification failed: " + marker)

if 'onclick="saveIns()"' not in html:
    raise SystemExit("Inspection save button missing")
if 'onsubmit="saveForm(event)"' not in html:
    raise SystemExit("Suivi des Actions save form missing")

print("Using original application:", original)
print("Original JCC and Gestion du personnel modules preserved.")
