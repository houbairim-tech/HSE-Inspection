from pathlib import Path
import re

root = Path("source/android")
if not root.exists():
    raise SystemExit("Android project not found in source archive")

index = root / "app/src/main/assets/index.html"
if not index.exists():
    raise SystemExit("Android index.html not found")

html = index.read_text(errors="ignore")

nav_marker = '<button class="nav-btn" data-tab="epc" onclick="switchTab(\'epc\')">EPC</button>'
nav_add = nav_marker + """
    <button class="nav-btn" data-tab="jcc" onclick="switchTab('jcc')">JCC</button>
    <button class="nav-btn" data-tab="personnel" onclick="switchTab('personnel')">Gestion du personnel</button>"""
if 'data-tab="jcc"' not in html:
    html = html.replace(nav_marker, nav_add, 1)

sections = """
<div id="tab-jcc" class="hidden">
  <section class="hse-hero"><div class="eyebrow">HSE 107E · JCC</div><h2>JCC</h2><p>Gestion des réunions / causeries JCC et suivi des actions associées.</p></section>
  <div class="card">
    <h3>Nouvelle JCC</h3>
    <div class="grid-2">
      <div><label>Date</label><input id="jcc-date" type="date"></div>
      <div><label>Lieu / Zone</label><input id="jcc-zone" type="text" placeholder="Ex. AT04, 107D..."></div>
      <div><label>Animateur</label><input id="jcc-anim" type="text" placeholder="Nom et prénom"></div>
      <div><label>Thème</label><input id="jcc-theme" type="text" placeholder="Thème de la JCC"></div>
      <div><label>Participants</label><input id="jcc-part" type="text" placeholder="Nombre ou noms"></div>
      <div><label>Statut</label><select id="jcc-status"><option>Réalisée</option><option>Programmée</option><option>Annulée</option></select></div>
    </div>
    <div><label>Observations / Actions</label><textarea id="jcc-obs" placeholder="Observations, actions et remarques"></textarea></div>
    <div class="filters" style="margin-top:12px"><button class="btn btn-success" onclick="saveJcc()">💾 Enregistrer</button><button class="btn btn-outline" onclick="resetJcc()">↺ Réinitialiser</button></div>
  </div>
  <div class="card" style="margin-top:12px"><h3>Historique JCC</h3><div id="jcc-list"></div></div>
</div>

<div id="tab-personnel" class="hidden">
  <section class="hse-hero"><div class="eyebrow">HSE 107E · RH / HSE</div><h2>Gestion du personnel</h2><p>Enregistrement et suivi des informations du personnel.</p></section>
  <div class="card">
    <h3>Ajouter un personnel</h3>
    <div class="grid-2">
      <div><label>Matricule</label><input id="per-matricule" type="text" placeholder="Matricule"></div>
      <div><label>Nom et prénom</label><input id="per-nom" type="text" placeholder="Nom et prénom"></div>
      <div><label>Fonction</label><input id="per-fonction" type="text" placeholder="Fonction"></div>
      <div><label>Société</label><input id="per-societe" type="text" placeholder="Société"></div>
      <div><label>Téléphone</label><input id="per-tel" type="tel" placeholder="Téléphone"></div>
      <div><label>Habilitation</label><input id="per-hab" type="text" placeholder="Habilitation / formation"></div>
      <div><label>Date d'entrée</label><input id="per-date" type="date"></div>
      <div><label>Statut</label><select id="per-status"><option>Actif</option><option>Inactif</option></select></div>
    </div>
    <div class="filters" style="margin-top:12px"><button class="btn btn-success" onclick="savePersonnel()">💾 Enregistrer</button><button class="btn btn-outline" onclick="resetPersonnel()">↺ Réinitialiser</button></div>
  </div>
  <div class="card" style="margin-top:12px"><h3>Personnel enregistré</h3><div id="personnel-list"></div></div>
</div>
"""
if 'id="tab-jcc"' not in html:
    html = html.replace('<!-- EPC INSPECTION -->', sections + '\n<!-- EPC INSPECTION -->', 1)

js = """
const JCC_KEY='hse107e_jcc_v1', PERSONNEL_KEY='hse107e_personnel_v1';
let jccData=load(JCC_KEY,[]), personnelData=load(PERSONNEL_KEY,[]);
function escA(v){return String(v==null?'':v).replace(/[&<>"]/g,function(m){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m]});}
function resetJcc(){['jcc-date','jcc-zone','jcc-anim','jcc-theme','jcc-part','jcc-obs'].forEach(function(id){var e=$(id);if(e)e.value=''});if($('jcc-status'))$('jcc-status').value='Réalisée';}
function saveJcc(){var date=$('jcc-date').value,theme=$('jcc-theme').value.trim(),anim=$('jcc-anim').value.trim();if(!date||!theme||!anim){alert('Veuillez renseigner la date, le thème et l’animateur.');return;}jccData.push({id:uid(),date:date,zone:$('jcc-zone').value.trim(),animateur:anim,theme:theme,participants:$('jcc-part').value.trim(),status:$('jcc-status').value,observations:$('jcc-obs').value.trim()});if(save(JCC_KEY,jccData)){resetJcc();renderJcc();if(window.v2Toast)v2Toast('JCC enregistrée avec succès');}}
function delJcc(id){if(!confirm('Supprimer cette JCC ?'))return;jccData=jccData.filter(function(x){return x.id!==id});save(JCC_KEY,jccData);renderJcc();}
function renderJcc(){var el=$('jcc-list');if(!el)return;if(!jccData.length){el.innerHTML='<div class="empty">Aucune JCC enregistrée.</div>';return;}el.innerHTML=jccData.slice().reverse().map(function(x){return '<div class="card" style="margin:8px 0;padding:10px"><strong>'+escA(x.theme)+'</strong> · '+escA(x.date)+'<div style="font-size:.82rem;margin-top:5px">📍 '+escA(x.zone)+' · 👤 '+escA(x.animateur)+' · '+escA(x.status)+'</div><div style="font-size:.82rem;margin-top:5px">'+escA(x.observations)+'</div><button class="btn btn-sm btn-outline" style="margin-top:8px" onclick="delJcc(\\''+x.id+'\\')">🗑 Supprimer</button></div>';}).join('');}
function resetPersonnel(){['per-matricule','per-nom','per-fonction','per-societe','per-tel','per-hab','per-date'].forEach(function(id){var e=$(id);if(e)e.value=''});if($('per-status'))$('per-status').value='Actif';}
function savePersonnel(){var nom=$('per-nom').value.trim(),fonction=$('per-fonction').value.trim();if(!nom||!fonction){alert('Veuillez renseigner le nom et la fonction.');return;}personnelData.push({id:uid(),matricule:$('per-matricule').value.trim(),nom:nom,fonction:fonction,societe:$('per-societe').value.trim(),tel:$('per-tel').value.trim(),habilitation:$('per-hab').value.trim(),dateEntree:$('per-date').value,status:$('per-status').value});if(save(PERSONNEL_KEY,personnelData)){resetPersonnel();renderPersonnel();if(window.v2Toast)v2Toast('Personnel enregistré avec succès');}}
function delPersonnel(id){if(!confirm('Supprimer ce personnel ?'))return;personnelData=personnelData.filter(function(x){return x.id!==id});save(PERSONNEL_KEY,personnelData);renderPersonnel();}
function renderPersonnel(){var el=$('personnel-list');if(!el)return;if(!personnelData.length){el.innerHTML='<div class="empty">Aucun personnel enregistré.</div>';return;}el.innerHTML=personnelData.slice().reverse().map(function(x){return '<div class="card" style="margin:8px 0;padding:10px"><strong>'+escA(x.nom)+'</strong><div style="font-size:.82rem;margin-top:4px">'+escA(x.fonction)+' · '+escA(x.societe)+'</div><div style="font-size:.78rem;margin-top:4px">Matricule: '+escA(x.matricule)+' · Habilitation: '+escA(x.habilitation)+' · Statut: '+escA(x.status)+'</div><button class="btn btn-sm btn-outline" style="margin-top:8px" onclick="delPersonnel(\\''+x.id+'\\')">🗑 Supprimer</button></div>';}).join('');}
"""
if 'const JCC_KEY=' not in html:
    html = html.replace('const TABS=', js + '\nconst TABS=', 1)

old_tabs = "const TABS=[['dashboard','Dashboard'],['actions','Suivi des Actions'],['production','Production'],['gemba','GEMBA Walk'],['contacts','Contact Sécurité'],['autorisations','Autorisations'],['compte','Compte Rendu'],['epc','EPC']];"
new_tabs = "const TABS=[['dashboard','Dashboard'],['actions','Suivi des Actions'],['production','Production'],['gemba','GEMBA Walk'],['contacts','Contact Sécurité'],['autorisations','Autorisations'],['compte','Compte Rendu'],['epc','EPC'],['jcc','JCC'],['personnel','Gestion du personnel']];"
html = html.replace(old_tabs, new_tabs, 1)
html = html.replace("  if (tab==='epc') renderEpc();", "  if (tab==='epc') renderEpc();\n  if (tab==='jcc') renderJcc();\n  if (tab==='personnel') renderPersonnel();", 1)

if 'onclick="saveIns()"' not in html:
    raise SystemExit("Inspection save button missing")
if 'onsubmit="saveForm(event)"' not in html:
    raise SystemExit("Suivi des Actions save form missing")

index.write_text(html)
print("JCC and Personnel modules injected successfully")
