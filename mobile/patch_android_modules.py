from pathlib import Path
import shutil

root = Path("source")
android_root = root / "android"
if not android_root.exists():
    raise SystemExit("Android project not found in source archive")

# The committed archive currently contains the Android WebView project only.
# Use its own index.html as the build source; do not fail looking for a
# separate desktop HTML that is not present in this archive.
target = android_root / "app/src/main/assets/index.html"
if not target.exists():
    candidates = list(android_root.rglob("index.html"))
    if not candidates:
        raise SystemExit("No Android index.html found")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(candidates[0], target)

html = target.read_text(errors="ignore")
print("Android source HTML:", target, "bytes:", len(html))
print("Navigation markup present:", "<nav" in html.lower())
print("Header markup present:", "<header" in html.lower())

# Mobile drawer control. Existing navigation buttons and application
# JavaScript are retained; only the presentation layer changes.
css = r"""
/* HSE 107E slide-out navigation drawer */
@media(max-width:768px){
  header{display:flex!important;align-items:center;flex-wrap:wrap;gap:8px!important}
  #hseMenuBtn{display:inline-flex!important;align-items:center;justify-content:center;width:42px;height:42px;flex:0 0 42px;border:0;border-radius:12px;background:#10243a;color:#fff;font-size:23px;box-shadow:0 4px 12px #10243a30}
  body>nav{position:fixed!important;z-index:1300!important;top:0!important;left:0!important;bottom:0!important;width:min(82vw,310px)!important;height:100dvh!important;max-height:100dvh!important;overflow-y:auto!important;display:flex!important;flex-direction:column!important;align-items:stretch!important;gap:7px!important;padding:calc(72px + env(safe-area-inset-top)) 13px 20px!important;background:linear-gradient(160deg,#10243a,#164c70 72%,#126b76)!important;box-shadow:12px 0 38px #07182d55!important;transform:translateX(-110%);visibility:hidden;transition:transform .24s ease,visibility .24s}
  body.hse-nav-open>nav{transform:translateX(0)!important;visibility:visible!important}
  body>nav .nav-btn{width:100%!important;min-height:46px!important;text-align:left!important;justify-content:flex-start!important;white-space:normal!important;padding:12px 13px!important;border-radius:11px!important;background:transparent!important;color:#e8f3fb!important;border:1px solid #ffffff20!important}
  body>nav .nav-btn.active{background:#ffffff20!important;border-color:#5de0d3!important;color:white!important;box-shadow:inset 3px 0 #5de0d3}
  #hseNavBackdrop{display:none;position:fixed;inset:0;z-index:1250;background:#07182d88;backdrop-filter:blur(2px)}
  body.hse-nav-open #hseNavBackdrop{display:block}
  main{width:100%!important;max-width:100%!important;min-width:0!important}
}
@media(min-width:769px){#hseMenuBtn,#hseNavBackdrop{display:none!important}}
"""
if "HSE 107E slide-out navigation drawer" not in html:
    if "</head>" in html:
        html = html.replace("</head>", "<style id='hseDrawerStyle'>"+css+"</style>\\n</head>", 1)
    else:
        html = "<style id='hseDrawerStyle'>"+css+"</style>\\n" + html

if 'id="hseMenuBtn"' not in html and "<header" in html.lower():
    import re
    html = re.sub(r'(<header\\b[^>]*>)', r'\\1<button id="hseMenuBtn" type="button" aria-label="Open navigation" aria-expanded="false" onclick="hseToggleNav()">☰</button>', html, count=1, flags=re.I)

if 'id="hseNavBackdrop"' not in html and "<nav" in html.lower():
    import re
    html = re.sub(r'(<nav\\b)', r'<div id="hseNavBackdrop" onclick="hseCloseNav()" aria-hidden="true"></div>\\1', html, count=1, flags=re.I)

js = r'''<script id="hseDrawerScript">
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
  document.addEventListener("keydown",function(e){
    if(e.key==="Escape")window.hseCloseNav();
  });
})();
</script>'''
if 'id="hseDrawerScript"' not in html and "</body>" in html:
    html = html.replace("</body>", js+"\\n</body>", 1)

target.write_text(html)
print("Mobile drawer injected. Existing Android application source and modules retained.")
