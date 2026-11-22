/* HSE107E Cloud Sync - shared Android/Windows client */
(() => {
  const API = 'https://hse107e-api.hse107e-cloud-api.workers.dev';
  const TOKEN_KEY = 'hse107e_cloud_token';
  const USER_KEY = 'hse107e_cloud_user';
  const SKIP = /^(hse107e_cloud_|__|drive|google)/i;

  const json = async (url, opts={}) => {
    const r = await fetch(API + url, {
      ...opts,
      headers: { 'Content-Type':'application/json', ...(opts.headers||{}) }
    });
    let d={}; try { d=await r.json(); } catch {}
    if (!r.ok) throw new Error(d.error || ('HTTP '+r.status));
    return d;
  };

  const token = () => localStorage.getItem(TOKEN_KEY) || '';
  const auth = () => token() ? ({Authorization:'Bearer '+token()}) : {};
  const user = () => {
    try { return JSON.parse(localStorage.getItem(USER_KEY)||'null'); }
    catch { return null; }
  };
  const saveUser = u => localStorage.setItem(USER_KEY, JSON.stringify(u||null));

  async function login(email,password){
    const d=await json('/auth/login',{
      method:'POST',
      body:JSON.stringify({email,password})
    });
    localStorage.setItem(TOKEN_KEY,d.token);
    saveUser(d.user);
    return d.user;
  }

  async function bootstrap(email,password,displayName,code){
    const d=await json('/auth/bootstrap',{
      method:'POST',
      headers:{'X-Bootstrap-Code':code},
      body:JSON.stringify({email,password,displayName})
    });
    localStorage.setItem(TOKEN_KEY,d.token);
    saveUser(d.user);
    return d.user;
  }

  async function logout(){
    try { await json('/auth/logout',{method:'POST',headers:auth()}); } catch {}
    localStorage.removeItem(TOKEN_KEY);
    saveUser(null);
  }

  function collect(){
    const out={};
    for(let i=0;i<localStorage.length;i++){
      const k=localStorage.key(i);
      if(!k || SKIP.test(k)) continue;
      const v=localStorage.getItem(k);
      if(v==null || v.length>900000) continue;
      try { out[k]=JSON.parse(v); } catch { out[k]=v; }
    }
    return out;
  }

  async function push(){
    if(!token()) throw new Error('Cloud non connecté');
    const data=collect(), keys=Object.keys(data);
    let done=0;
    const all=await json('/records?module=app',{headers:auth()});
    const existing=new Map((all.records||[]).map(x=>[x.record_key,x]));
    for(const k of keys){
      const base=Number(existing.get(k)?.version||0);
      await json('/records',{
        method:'POST',
        headers:auth(),
        body:JSON.stringify({
          module:'app',
          key:k,
          payload:data[k],
          baseVersion:base
        })
      });
      done++;
    }
    return {done,total:keys.length};
  }

  async function pull(){
    if(!token()) throw new Error('Cloud non connecté');
    const d=await json('/records?module=app',{headers:auth()});
    let n=0;
    for(const r of (d.records||[])){
      try {
        localStorage.setItem(
          r.record_key,
          typeof r.payload==='string' ? r.payload : JSON.stringify(r.payload)
        );
        n++;
      } catch {}
    }
    if(n) location.reload();
    return n;
  }

  function style(){
    if(document.getElementById('hse107eCloudStyle')) return;
    const s=document.createElement('style');
    s.id='hse107eCloudStyle';
    s.textContent=`
      #hse107eCloudBtn{
        position:fixed;right:14px;bottom:14px;z-index:99999;
        border:0;border-radius:999px;padding:12px 17px;
        background:linear-gradient(135deg,#0f766e,#0b5f9a);
        color:#fff;font-weight:800;font-size:14px;
        box-shadow:0 6px 22px #0004;cursor:pointer;
      }
      #hse107eCloudModal{
        position:fixed;inset:0;z-index:100000;display:none;
        align-items:center;justify-content:center;padding:16px;
        background:#07182dcc;font-family:Arial,sans-serif;
      }
      #hse107eCloudModal.open{display:flex}
      #hse107eCloudCard{
        width:min(430px,100%);background:#fff;border-radius:20px;
        padding:22px;box-shadow:0 20px 70px #0007;
      }
      #hse107eCloudCard h2{margin:0 0 6px;color:#10243a;font-size:21px}
      #hse107eCloudCard p{margin:0 0 18px;color:#5d6874;font-size:13px}
      .hse-cloud-field{display:block;width:100%;box-sizing:border-box;margin:7px 0;
        padding:12px;border:1px solid #cfd8df;border-radius:10px;font-size:15px}
      .hse-cloud-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}
      .hse-cloud-actions button{flex:1;min-height:44px;border:0;border-radius:10px;
        padding:10px 12px;font-weight:700;cursor:pointer}
      .hse-cloud-primary{background:#0f766e;color:#fff}
      .hse-cloud-secondary{background:#e9eef2;color:#10243a}
      #hse107eCloudMsg{min-height:20px;margin-top:10px;font-size:12px;color:#b42318}
      .hse-cloud-user{padding:10px;background:#f1f7f7;border-radius:10px;margin:8px 0 12px;font-size:13px}
    `;
    document.head.appendChild(s);
  }

  function openModal(){
    style();
    let m=document.getElementById('hse107eCloudModal');
    if(!m){
      m=document.createElement('div');
      m.id='hse107eCloudModal';
      m.innerHTML=`
        <div id="hse107eCloudCard">
          <h2>☁️ HSE 107E Cloud</h2>
          <p>Connexion et synchronisation entre Android et Windows</p>
          <div id="hse107eCloudBody"></div>
          <div id="hse107eCloudMsg"></div>
        </div>`;
      document.body.appendChild(m);
      m.addEventListener('click',e=>{if(e.target===m)m.classList.remove('open');});
    }
    const body=document.getElementById('hse107eCloudBody');
    const msg=document.getElementById('hse107eCloudMsg');
    msg.textContent='';
    const u=user();

    if(!u){
      body.innerHTML=`
        <input id="hseCloudEmail" class="hse-cloud-field" type="email" placeholder="Email administrateur">
        <input id="hseCloudPassword" class="hse-cloud-field" type="password" placeholder="Mot de passe">
        <div class="hse-cloud-actions">
          <button class="hse-cloud-primary" id="hseCloudLogin">Connexion</button>
          <button class="hse-cloud-secondary" id="hseCloudCreate">Créer le premier administrateur</button>
        </div>`;
      document.getElementById('hseCloudLogin').onclick=async()=>{
        try{
          await login(
            document.getElementById('hseCloudEmail').value.trim(),
            document.getElementById('hseCloudPassword').value
          );
          msg.style.color='#087443'; msg.textContent='Connexion Cloud réussie.';
          setTimeout(()=>{m.classList.remove('open');location.reload();},500);
        }catch(e){msg.style.color='#b42318';msg.textContent=e.message||String(e);}
      };
      document.getElementById('hseCloudCreate').onclick=async()=>{
        const code=prompt('Code bootstrap');
        if(!code)return;
        try{
          await bootstrap(
            document.getElementById('hseCloudEmail').value.trim(),
            document.getElementById('hseCloudPassword').value,
            prompt('Nom affiché','HSE Administrator')||'HSE Administrator',
            code
          );
          msg.style.color='#087443'; msg.textContent='Administrateur créé et connecté.';
          setTimeout(()=>{m.classList.remove('open');location.reload();},500);
        }catch(e){msg.style.color='#b42318';msg.textContent=e.message||String(e);}
      };
    }else{
      body.innerHTML=`
        <div class="hse-cloud-user">Connecté : <b>${u.email||u.displayName||'Utilisateur'}</b></div>
        <div class="hse-cloud-actions">
          <button class="hse-cloud-primary" id="hseCloudSync">☁️ Synchroniser</button>
          <button class="hse-cloud-secondary" id="hseCloudPull">↓ Télécharger</button>
          <button class="hse-cloud-secondary" id="hseCloudLogout">Déconnexion</button>
        </div>`;
      document.getElementById('hseCloudSync').onclick=async()=>{
        try{const r=await push();msg.style.color='#087443';msg.textContent=`Synchronisation terminée : ${r.done}/${r.total}`;}
        catch(e){msg.style.color='#b42318';msg.textContent=e.message||String(e);}
      };
      document.getElementById('hseCloudPull').onclick=async()=>{
        try{const n=await pull();msg.style.color='#087443';msg.textContent=`Données Cloud récupérées : ${n}`;}
        catch(e){msg.style.color='#b42318';msg.textContent=e.message||String(e);}
      };
      document.getElementById('hseCloudLogout').onclick=async()=>{
        await logout(); m.classList.remove('open'); location.reload();
      };
    }
    m.classList.add('open');
  }

  function button(){
    style();
    if(document.getElementById('hse107eCloudBtn')) return;
    const b=document.createElement('button');
    b.id='hse107eCloudBtn';
    b.textContent=user()?'☁️ Cloud':'☁️ Cloud — Connexion';
    b.onclick=openModal;
    document.body.appendChild(b);
  }

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',button);
  else button();

  window.HSE107ECloud={login,bootstrap,logout,push,pull,collect,api:API};
})();