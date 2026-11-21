from pathlib import Path
import shutil, re

root = Path("source")
android_root = root / "android"
original_root = Path("original_source/desktop")
original_html = original_root / "index.html"
if not android_root.exists():
    raise SystemExit("Android wrapper project missing in DOC-20261119-WA0121.zip")
if not original_html.exists():
    raise SystemExit("Original desktop/index.html missing from Hse-ande source archive")

assets = android_root / "app/src/main/assets"
assets.mkdir(parents=True, exist_ok=True)
# Copy the complete original desktop application into WebView assets so that
# local images and libraries keep their relative paths.
shutil.copytree(original_root, assets, dirs_exist_ok=True)
target = assets / "index.html"
html = target.read_text(encoding="utf-8", errors="ignore")

required = ["PZ_FORMS", "jccOpen", "pzOpen", "jccSave", "pzSave"]
for marker in required:
    if marker.lower() not in html.lower():
        raise SystemExit("Original module check failed: " + marker)
print("Original source verified:", target, "bytes:", len(html))
print("JCC markers:", html.lower().count("jcc"))
print("Personnel markers:", html.lower().count("gestion du personnel"))

css = r"""
@media(max-width:768px){
header{display:flex!important;align-items:center;flex-wrap:wrap;gap:8px!important}
#hseMenuBtn{display:inline-flex!important;align-items:center;justify-content:center;width:42px;height:42px;flex:0 0 42px;border:0;border-radius:12px;background:#10243a;color:#fff;font-size:23px}
body>nav{position:fixed!important;z-index:1300!important;top:0!important;left:0!important;bottom:0!important;width:min(82vw,310px)!important;height:100dvh!important;max-height:100dvh!important;overflow-y:auto!important;display:flex!important;flex-direction:column!important;align-items:stretch!important;gap:7px!important;padding:calc(72px + env(safe-area-inset-top)) 13px 20px!important;background:linear-gradient(160deg,#10243a,#164c70 72%,#126b76)!important;box-shadow:12px 0 38px #07182d55!important;transform:translateX(-110%);visibility:hidden;transition:transform .24s ease,visibility .24s}
body.hse-nav-open>nav{transform:translateX(0)!important;visibility:visible!important}
body>nav .nav-btn{width:100%!important;min-height:46px!important;text-align:left!important;justify-content:flex-start!important;white-space:normal!important;padding:12px 13px!important;border-radius:11px!important;background:transparent!important;color:#e8f3fb!important;border:1px solid #ffffff20!important}
body>nav .nav-btn.active{background:#ffffff20!important;border-color:#5de0d3!important;color:white!important}
#hseNavBackdrop{display:none;position:fixed;inset:0;z-index:1250;background:#07182d88}
body.hse-nav-open #hseNavBackdrop{display:block}
main{width:100%!important;max-width:100%!important;min-width:0!important}
}
@media(min-width:769px){#hseMenuBtn,#hseNavBackdrop{display:none!important}}
"""
if 'id="hseDrawerStyle"' not in html:
    html=html.replace("</head>", '<style id="hseDrawerStyle">'+css+'</style>\\n</head>',1)
if 'id="hseMenuBtn"' not in html:
    html=re.sub(r'(<header\\b[^>]*>)',r'\\1<button id="hseMenuBtn" type="button" aria-label="Open navigation" aria-expanded="false" onclick="hseToggleNav()">☰</button>',html,count=1,flags=re.I)
if 'id="hseNavBackdrop"' not in html:
    html=re.sub(r'(<nav\\b)',r'<div id="hseNavBackdrop" onclick="hseCloseNav()" aria-hidden="true"></div>\\1',html,count=1,flags=re.I)
js=r'''<script id="hseDrawerScript">(function(){
window.hseToggleNav=function(){document.body.classList.toggle("hse-nav-open");var b=document.getElementById("hseMenuBtn");if(b)b.setAttribute("aria-expanded",document.body.classList.contains("hse-nav-open")?"true":"false");};
window.hseCloseNav=function(){document.body.classList.remove("hse-nav-open");var b=document.getElementById("hseMenuBtn");if(b)b.setAttribute("aria-expanded","false");};
document.addEventListener("click",function(e){if(e.target.closest("nav .nav-btn"))window.hseCloseNav();});
document.addEventListener("keydown",function(e){if(e.key==="Escape")window.hseCloseNav();});
})();</script>'''
if 'id="hseDrawerScript"' not in html:
    html=html.replace("</body>",js+"\\n</body>",1)
target.write_text(html,encoding="utf-8")
print("Original JCC/personnel modules preserved; mobile drawer applied.")
