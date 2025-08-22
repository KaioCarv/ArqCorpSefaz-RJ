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