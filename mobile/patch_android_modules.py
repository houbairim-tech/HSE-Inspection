from pathlib import Path
import shutil, re

root = Path("source")
android_root = root / "android"
original_root = Path("original_source/desktop"
)
if not android_root.exists():
    raise SystemExit("Android wrapper project missing")
if not (original_root / "index.html").exists():
    raise SystemExit("Original desktop/index.html missing")

assets = android_root / "app/src/main/assets"
assets.mkdir(parents=True, exist_ok=True)
shutil.copytree(original_root, assets, dirs_exist_ok=True)
target = assets / "index.html"
html = target.read_text(encoding="utf-8", errors="ignore")

# Fail the build unless all ten original navigation tabs and both new modules
# are present in the actual HTML that will be packaged into the APK.
labels = ["Dashboard", "Suivi des Actions", "Production", "GEMBA Walk",
          "Contact Sécurité", "Autorisations", "Compte Rendu", "EPC",
          "JCC", "Gestion du personnel"]
missing = [x for x in labels if x.casefold() not in html.casefold()]
if missing:
    raise SystemExit("Missing original tabs: " + ", ".join(missing))
for marker in ["jccOpen", "pzOpen", "jccSave", "pzSave"]:
    if marker.casefold() not in html.casefold():
        raise SystemExit("Missing original module function: " + marker)

# Insert mobile drawer control without replacing any original navigation item,
# event handler, form, or persistence code.
css = """
@media(max-width:768px){
  body{overflow-x:hidden}
  header{display:flex!important;align-items:center;flex-wrap:wrap;gap:8px!important}
  #hseMenuBtn{display:inline-flex!important;align-items:center;justify-content:center;width:42px;height:42px;flex:0 0 42px;border:0;border-radius:12px;background:#10243a;color:#fff;font-size:23px}
  body>nav{position:fixed!important;z-index:1300!important;top:0!important;left:0!important;bottom:0!important;width:min(82vw,310px)!important;height:100dvh!important;max-height:100dvh!important;overflow-y:auto!important;display:flex!important;flex-direction:column!important;align-items:stretch!important;gap:7px!important;padding:calc(72px + env(safe-area-inset-top)) 13px 20px!important;background:linear-gradient(160deg,#10243a,#164c70 72%,#126b76)!important;box-shadow:12px 0 38px #07182d55!important;transform:translateX(-110%);visibility:hidden;transition:transform .24s ease,visibility .24s}
  body.hse-nav-open>nav{transform:translateX(0)!important;visibility:visible!important}
  body>nav .nav-btn{width:100%!important;min-height:46px!important;text-align:left!important;justify-content:flex-start!important;white-space:normal!important;padding:12px 13px!important;border-radius:11px!important;background:transparent!important;color:#e8f3fb!important;border:1px solid #ffffff20!important}
  body>nav .nav-btn.active{background:#ffffff20!important;border-color:#5de0d3!important;color:white!important}
  #hseNavBackdrop{display:none;position:fixed;inset:0;z-index:1250;background:#07182d88}
  body.hse-nav-open #hseNavBackdrop{display:block}
  main{width:100%!important;max-width:100%!important;min-width:0!important;padding-left:10px!important;padding-right:10px!important}
  input,select,textarea{max-width:100%;min-width:0;font-size:16px!important}
  .modal,.modal-content{max-width:100vw!important}
}
@media(min-width:769px){#hseMenuBtn,#hseNavBackdrop{display:none!important}}
"""
if 'id="hseDrawerStyle"' not in html:
    html = html.replace("</head>", '<style id="hseDrawerStyle">' + css + '</style>\\n</head>', 1)

if 'id="hseMenuBtn"' not in html:
    m = re.search(r'<header\\b[^>]*>', html, flags=re.I)
    if not m:
        raise SystemExit("Cannot locate original header for mobile menu button")
    html = html[:m.end()] + '<button id="hseMenuBtn" type="button" aria-label="Open navigation" aria-expanded="false" onclick="hseToggleNav()">☰</button>' + html[m.end():]

if 'id="hseNavBackdrop"' not in html:
    m = re.search(r'<nav\\b[^>]*>', html, flags=re.I)
    if not m:
        raise SystemExit("Cannot locate original navigation")
    html = html[:m.start()] + '<div id="hseNavBackdrop" onclick="hseCloseNav()" aria-hidden="true"></div>' + html[m.start():]

js = '''<script id="hseDrawerScript">
(function(){
  window.hseToggleNav=function(){
    document.body.classList.toggle("hse-nav-open");
    var b=document.getElementById("hseMenuBtn");
    if(b)b.setAttribute("aria-expanded",document.body.classList.contains("hse-nav-open")?"true":"false");
  };
  window.hseCloseNav=function(){
    document.body.classList.remove("hse-nav-open");
    var b=document.getElementById("hseMenuBtn");
    if(b)b.setAttribute("aria-expanded","false");
  };
  document.addEventListener("click",function(e){
    if(e.target.closest("nav .nav-btn"))window.hseCloseNav();
  });
  document.addEventListener("keydown",function(e){if(e.key==="Escape")window.hseCloseNav();});
})();
</script>'''
if 'id="hseDrawerScript"' not in html:
    if "</body>" not in html:
        raise SystemExit("Missing body close tag")
    html = html.replace("</body>", js + "\\n</body>", 1)

target.write_text(html, encoding="utf-8")
# Validate the packaged HTML still has all ten original tabs.
check = target.read_text(encoding="utf-8")
missing = [x for x in labels if x.casefold() not in check.casefold()]
if missing:
    raise SystemExit("Post-patch tab validation failed: " + ", ".join(missing))
print("Verified all 10 original tabs, JCC/personnel handlers, and mobile drawer.")
