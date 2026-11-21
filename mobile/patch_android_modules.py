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
        html = p.read_text(errors="ignore")
    except Exception:
        continue
    score = sum(marker.lower() in html.lower() for marker in [
        "JCC", "PZ_FORMS", "jccOpen", "pzOpen", "jccSave", "pzSave"
    ])
    ranked.append((score, p, html))
ranked.sort(key=lambda x: x[0], reverse=True)
for score, p, _ in ranked[:10]:
    print(f"HTML candidate score={score}: {p}")
if not ranked or ranked[0][0] < 4:
    raise SystemExit("Original JCC + personnel source HTML not found")

_, original, html = ranked[0]
target = android_root / "app/src/main/assets/index.html"
target.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(original, target)

for marker in ["PZ_FORMS", "jccOpen", "pzOpen", "jccSave", "pzSave"]:
    if marker.lower() not in html.lower():
        raise SystemExit("Original module verification failed: " + marker)

# Responsive phone layout with a slide-in navigation drawer. The original
# navigation buttons and original JCC/Personnel forms remain unchanged.
css = r"""<style id="hseMobileNavStyle">
:root{--hse-ink:#10243a;--hse-blue:#145b91;--hse-cyan:#16a6a1;--hse-surface:#f4f7fb}
@media(max-width:760px){
body{padding:0 0 calc(16px + env(safe-area-inset-bottom));overflow-x:hidden;background:var(--hse-surface)}
header{position:sticky;top:0;z-index:1100;display:flex;align-items:center;gap:10px;padding:10px 12px!important;padding-top:calc(10px + env(safe-area-inset-top))!important;background:rgba(255,255,255,.97);backdrop-filter:blur(12px);box-shadow:0 3px 16px #10243a18}
header .brand{min-width:0;flex:1;gap:7px}.logo-img{max-width:34px;max-height:34px}.brand h1,#appTitle{font-size:13px!important;line-height:1.25;margin:0;max-width:175px}
.header-actions{display:flex;gap:5px;flex-wrap:wrap;justify-content:flex-end}.header-actions .btn{font-size:11px!important;padding:7px 8px!important;min-height:34px}
#hseMenuBtn{display:inline-flex;align-items:center;justify-content:center;flex:0 0 40px;width:40px;height:40px;border:0;border-radius:12px;background:var(--hse-ink);color:white;font-size:22px}
body>nav{position:fixed!important;z-index:1300;top:0;left:0;bottom:0;width:min(82vw,310px);height:100dvh;overflow-y:auto;display:flex!important;flex-direction:column;gap:6px;padding:calc(68px + env(safe-area-inset-top)) 14px 20px!important;background:linear-gradient(165deg,#10243a,#164c70 70%,#126b76);box-shadow:12px 0 38px #07182d44;transform:translateX(-110%);visibility:hidden;transition:transform .24s ease,visibility .24s}
body.hse-nav-open>nav{transform:translateX(0);visibility:visible}
body>nav .nav-btn{width:100%;text-align:left;justify-content:flex-start;padding:13px 14px!important;min-height:46px;border-radius:11px!important;background:transparent!important;color:#e8f3fb!important;border:1px solid #ffffff18!important;font-size:14px!important}
body>nav .nav-btn.active{background:#ffffff20!important;border-color:#5de0d3!important;color:white!important;box-shadow:inset 3px 0 #5de0d3}
#hseNavBackdrop{display:none;position:fixed;inset:0;z-index:1250;background:#07182d88;backdrop-filter:blur(2px)}body.hse-nav-open #hseNavBackdrop{display:block}
main{width:100%!important;max-width:100%!important;padding:12px!important;margin:0!important}
main .grid,main .grid-2,main .form-grid{grid-template-columns:minmax(0,1fr)!important}
main input,main select,main textarea{max-width:100%;min-width:0;font-size:16px!important;min-height:44px}
.modal{padding:8px!important}.modal-content{width:100%!important;max-width:100%!important;max-height:92dvh!important;overflow:auto!important;border-radius:16px!important}
table{display:block;max-width:100%;overflow-x:auto}
}
@media(min-width:761px){#hseMenuBtn,#hseNavBackdrop{display:none!important}}
</style>"""
if 'id="hseMobileNavStyle"' not in html:
    html = html.replace("</head>", css + "\n</head>", 1)
if 'id="hseMenuBtn"' not in html:
    html = html.replace("<header>", '<header>\n<button id="hseMenuBtn" type="button" aria-label="Ouvrir le menu" aria-expanded="false" onclick="hseToggleNav()">☰</button>', 1)
if 'id="hseNavBackdrop"' not in html:
    html = html.replace("<nav>", '<div id="hseNavBackdrop" onclick="hseCloseNav()" aria-hidden="true"></div>\n<nav aria-label="Navigation principale">', 1)
js = r'''<script id="hseMobileNavScript">
(function(){
window.hseToggleNav=function(){document.body.classList.toggle("hse-nav-open");var b=document.getElementById("hseMenuBtn");if(b)b.setAttribute("aria-expanded",document.body.classList.contains("hse-nav-open")?"true":"false");};
window.hseCloseNav=function(){document.body.classList.remove("hse-nav-open");var b=document.getElementById("hseMenuBtn");if(b)b.setAttribute("aria-expanded","false");};
document.addEventListener("click",function(e){if(e.target.closest("nav .nav-btn"))window.hseCloseNav();});
document.addEventListener("keydown",function(e){if(e.key==="Escape")window.hseCloseNav();});
})();
</script>'''
if 'id="hseMobileNavScript"' not in html:
    html = html.replace("</body>", js + "\n</body>", 1)
target.write_text(html)
print("Using original application:", original)
print("Original JCC/Personnel forms preserved; mobile slide-out navigation applied.")
