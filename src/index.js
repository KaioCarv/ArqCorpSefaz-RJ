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


// Função para chamar o backend FastAPI e pegar status de múltiplos painéis
async function carregarPainelStatus(titulosOuIds) {
  const qs = encodeURIComponent(titulosOuIds.join(","));
  const res = await fetch(`/multi_status?panels=${qs}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

// Função para aplicar cores/status no DOM
function aplicarStatusNoDOM(items) {
  // cria map para busca rápida por nome e id
  const byName = new Map(items.map(it => [it.name.toLowerCase(), it]));
  const byId = new Map(items.map(it => [String(it.id), it]));

  document.querySelectorAll(".tile[data-panel]").forEach(el => {
    const token = el.dataset.panel;
    const it = (token.match(/^\d+$/) ? byId.get(token) : byName.get(token.toLowerCase()));
    if (!it) return;

    // Aplica cor retornada pelo Grafana
    el.style.backgroundColor = it.color || "";
    el.style.color = "#fff";
    
    // Marca se está "down" ou "up"
    el.classList.toggle("is-down", !!it.down);
    el.classList.toggle("is-up", !it.down);

    // Tooltip com info
    el.title = `${it.name} — status: ${it.down ? "OFFLINE" : "ONLINE"}`;
  });
}

// Atualiza todos os botões
async function atualizar() {
  const tokens = Array.from(document.querySelectorAll(".tile[data-panel]"))
    .map(el => el.dataset.panel);
  if (!tokens.length) return;

  try {
    const data = await carregarPainelStatus(tokens);
    aplicarStatusNoDOM(data.items || []);
    document.getElementById("last").textContent = "Atualizado: " + new Date().toLocaleTimeString();
  } catch (e) {
    console.error(e);
    document.getElementById("last").textContent = "Falha ao atualizar";
  }
}

// Executa ao carregar a página
document.addEventListener("DOMContentLoaded", () => {
  atualizar();
  setInterval(atualizar, 15000); // atualiza a cada 15s
  const refreshBtn = document.getElementById("refresh");
  if (refreshBtn) refreshBtn.addEventListener("click", atualizar);
});

