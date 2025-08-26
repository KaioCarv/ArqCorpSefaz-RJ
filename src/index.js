// === Accordions EXTERNOS (do card) ===
const accordions = document.querySelectorAll('.card > details.accordion');
  accordions.forEach(d => {
    const summary = d.querySelector(':scope > summary');
    const set = () => summary && summary.setAttribute('aria-expanded', d.open ? 'true' : 'false');
    d.addEventListener('toggle', () => {
      if (d.open) {
        accordions.forEach(o => { if (o !== d && o.open) o.open = false; });
      }
      set();
    });
    set();
  });

  // === Submenus internos (SINCAD-WEB etc.) ===
  document.querySelectorAll('.menu').forEach(menu => {
    const items = menu.querySelectorAll('details.menu-item');
    items.forEach(d => {
      const summary = d.querySelector('summary');
      const set = () => summary && summary.setAttribute('aria-expanded', d.open ? 'true' : 'false');
      d.addEventListener('toggle', () => {
        if (d.open) items.forEach(o => { if (o !== d) o.open = false; });
        set();
      });
      set();
    });
  });

  // Fecha submenus ao clicar fora (não mexe nos accordions externos)
  document.addEventListener('click', (e) => {
    document.querySelectorAll('.menu details.menu-item[open]').forEach(d => {
      if (!d.contains(e.target)) d.open = false;
    });
  });

//----------------------------------------------------------------------------------------------------------------------------------------------

function pingImage(url, timeout = 6000){
  return new Promise(resolve => {
    const img = new Image();
    let done = false;
    const end = (ok) => { if (!done){ done = true; clearTimeout(t); resolve(ok); } };
    const bust = (url.includes('?') ? '&' : '?') + 't=' + Date.now();
    const t = setTimeout(() => end(false), timeout);
    img.onload  = () => end(true);   // resposta HTTP OK + imagem válida
    img.onerror = () => end(false);  // erro de rede ou não é imagem
    img.src = url + bust;
  });
}

async function atualizarMonitores(){
  const itens = document.querySelectorAll('.tile[data-check]');
  for (const el of itens){
    const ok = await pingImage(el.dataset.check);
    el.classList.toggle('is-down', !ok);
    el.classList.toggle('is-up', ok);
    el.title = ok ? 'Online' : 'Offline';
  }
}

// Deixa todos verdes e monitora os que têm data-check
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.tile').forEach(el => el.classList.add('is-up'));
  atualizarMonitores();
  setInterval(atualizarMonitores, 30000);
});

//-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
async function atualizar(){
  const tiles = document.querySelectorAll('.tile[data-svc]');
  for (const el of tiles){
    const svc = el.dataset.svc;
    try{
      const r = await fetch(`/grafana_status?svc=${encodeURIComponent(svc)}`, { cache: 'no-store' });
      const data = await r.json();
      const ok = !!data.ok;
      el.classList.toggle('is-down', !ok);
      el.classList.toggle('is-up', ok);
      el.title = ok ? 'Online (Grafana)' : `OFFLINE (${data.source}${data.active_alerts?` - ${data.active_alerts} alerta(s)`:''})`;
    }catch(e){
      el.classList.add('is-down'); el.classList.remove('is-up');
      el.title = 'OFFLINE (erro na consulta ao backend)';
    }
  }
}
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.tile[data-svc]').forEach(el => el.classList.add('is-up'));
  atualizar();
  setInterval(atualizar, 30000);
});

