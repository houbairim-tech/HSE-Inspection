/* HSE107E Cloud Sync - shared Android/Windows client */
(() => {
  const API = 'https://hse107e-api.hse107e-cloud-api.workers.dev';
  const TOKEN_KEY = 'hse107e_cloud_token';
  const USER_KEY = 'hse107e_cloud_user';
  const SKIP = /^(hse107e_cloud_|__|drive|google)/i;
  const json = async (url, opts={}) => {
    const r = await fetch(API + url, { ...opts, headers: { 'Content-Type':'application/json', ...(opts.headers||{}) }});
    let d={}; try { d=await r.json(); } catch {}
    if (!r.ok) throw new Error(d.error || ('HTTP '+r.status));
    return d;
  };
  const token = () => localStorage.getItem(TOKEN_KEY) || '';
  const auth = () => token() ? ({Authorization:'Bearer '+token()}) : {};
  const user = () => { try{return JSON.parse(localStorage.getItem(USER_KEY)||'null')}catch{return null} };
  const saveUser = u => localStorage.setItem(USER_KEY, JSON.stringify(u||null));
  async function login(email,password){
    const d=await json('/auth/login',{method:'POST',body:JSON.stringify({email,password})});
    localStorage.setItem(TOKEN_KEY,d.token); saveUser(d.user); return d.user;
  }
  async function bootstrap(email,password,displayName,code){
    const d=await json('/auth/bootstrap',{method:'POST',headers:{'X-Bootstrap-Code':code},body:JSON.stringify({email,password,displayName})});
    localStorage.setItem(TOKEN_KEY,d.token); saveUser(d.user); return d.user;
  }
  async function logout(){ try{await json('/auth/logout',{method:'POST',headers:auth()});}catch{} localStorage.removeItem(TOKEN_KEY);saveUser(null); }
  function collect(){
    const out={};
    for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(!k||SKIP.test(k))continue;const v=localStorage.getItem(k);if(v==null)continue;if(v.length>900000)continue;try{out[k]=JSON.parse(v)}catch{out[k]=v}}
    return out;
  }
  async function push(){
    if(!token()) throw new Error('Cloud non connecté');
    const data=collect(), keys=Object.keys(data);
    let done=0;
    for(const k of keys){
      let base=0;
      try{const r=await json('/records?module=app'); const old=(r.records||[]).find(x=>x.record_key===k); base=Number(old?.version||0);}catch{}
      await json('/records',{method:'POST',headers:auth(),body:JSON.stringify({module:'app',key:k,payload:data[k],baseVersion:base})});
      done++;
    }
    return {done,total:keys.length};
  }
  async function pull(){
    if(!token()) throw new Error('Cloud non connecté');
    const d=await json('/records?module=app',{headers:auth()});
    let n=0;
    for(const r of (d.records||[])){try{localStorage.setItem(r.record_key,typeof r.payload==='string'?r.payload:JSON.stringify(r.payload));n++;}catch{}}
    if(n) location.reload();
    return n;
  }
  function button(){
    if(document.getElementById('hse107eCloudBtn')) return;
    const b=document.createElement('button');b.id='hse107eCloudBtn';b.textContent='☁️ Cloud';
    Object.assign(b.style,{position:'fixed',right:'14px',bottom:'14px',zIndex:99999,border:'0',borderRadius:'999px',padding:'11px 16px',background:'#0f766e',color:'#fff',fontWeight:'700',boxShadow:'0 5px 18px #0003',cursor:'pointer'});
    b.onclick=async()=>{
      const u=user();
      const choice=prompt(u?'Cloud connecté à '+(u.email||u.displayName)+'\n\n1 = Synchroniser\n2 = Télécharger depuis Cloud\n3 = Déconnexion':'Cloud HSE107E\n\n1 = Connexion\n2 = Créer le premier administrateur');
      if(!choice)return;
      try{
        if(!u && choice==='1'){const e=prompt('Email');const p=prompt('Mot de passe (12 caractères minimum)');await login(e,p);alert('Connexion Cloud réussie.');return;}
        if(!u && choice==='2'){const code=prompt('Code bootstrap');const e=prompt('Email administrateur');const p=prompt('Mot de passe (12 caractères minimum)');const n=prompt('Nom affiché','HSE Administrator');await bootstrap(e,p,n,code);alert('Administrateur créé et connecté.');return;}
        if(u&&choice==='1'){const r=await push();alert('Synchronisation envoyée: '+r.done+'/'+r.total+' éléments.');return;}
        if(u&&choice==='2'){const n=await pull();alert('Données Cloud récupérées: '+n+' éléments.');return;}
        if(u&&choice==='3'){await logout();alert('Déconnecté du Cloud.');}
      }catch(e){alert('Cloud HSE107E: '+(e.message||e));}
    };
    document.body.appendChild(b);
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',button); else button();
  window.HSE107ECloud={login,bootstrap,logout,push,pull,collect,api:API};
})();