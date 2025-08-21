<?php ?>
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Instituição — Painel com 4 Cards</title>
  <link rel="stylesheet" href="style.css">
  <meta name="color-scheme" content="light" />

  <style>
    :root {
      --brand: #1e54b7;
      --brand-600: #17479a;
      --brand-50: #f4f7ff;
      --bg: #ffffff;
      --card: #ffffff;
      --text: #111827;
      --muted: #6b7280;
      --ring: 0 0 0 4px rgba(30, 84, 183, 0.18);
      --radius: 16px;
      --shadow: 0 10px 30px rgba(0,0,0,0.07);
      --border: rgba(0,0,0,0.08);
    }

    html, body { height: 100%; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font: 400 16px/1.5 ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji";
      -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility;
    }
    .container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 48px 24px 80px;
    }

    header {
      display: grid;
      gap: 8px;
      justify-items: center;
      text-align: center;
      margin-bottom: 28px;
    }
    .kicker { color: var(--brand); font-weight: 600; letter-spacing: .04em; text-transform: uppercase; font-size: 12px; }
    h1 { margin: 0; font-size: clamp(26px, 3.2vw, 38px); line-height: 1.15; }
    .subtitle { color: var(--muted); max-width: 70ch; }

    .grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 20px;
    }
    @media (max-width: 1024px) { .grid { grid-template-columns: repeat(2, 1fr); } }
    @media (max-width: 640px) { .grid { grid-template-columns: 1fr; } }

    .card {
      background: var(--card);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      padding: 22px;
      display: grid;
      align-content: start;
      gap: 14px;
      position: relative;
      border: 1px solid var(--border);
    }
    .card:focus-within { outline: none; box-shadow: var(--shadow), var(--ring); }
    .icon {
      width: 40px; height: 40px; border-radius: 10px;
      background: rgba(30,84,183,0.10);
      display: grid; place-items: center;
    }
    .card h2 { font-size: 18px; margin: 2px 0 0; }
    .desc { color: var(--muted); font-size: 14px; }

    details { border-top: 1px solid var(--border); padding-top: 10px; }
    summary {
      list-style: none; cursor: pointer;
      display: inline-flex; align-items: center; gap: 10px;
      padding: 10px 12px; border-radius: 12px;
      border: 1px solid var(--border);
      background: #fff;
      transition: background .2s ease, border-color .2s ease, transform .12s ease;
      user-select: none;
    }
    summary::-webkit-details-marker { display: none; }
    details[open] summary { border-color: rgba(30,84,183,.35); background: var(--brand-50); }
    summary:active { transform: translateY(1px); }

    .menu {
      display: grid; gap: 10px; margin-top: 12px;
    }
    .menu a {
      display: flex; align-items: center; justify-content: space-between;
      text-decoration: none; color: var(--text);
      padding: 12px 14px; border-radius: 12px;
      border: 1px solid var(--border);
      background: #fff;
      transition: transform .12s ease, border-color .2s ease, background .2s ease, box-shadow .2s ease;
      font-size: 14px; font-weight: 500;
    }
    .menu a:hover { background: var(--brand-50); border-color: rgba(30,84,183,0.35); transform: translateY(-1px); box-shadow: 0 6px 18px rgba(0,0,0,0.05); }
    .menu a::after { content: '›'; font-size: 16px; line-height: 1; opacity: .65; }
    .menu small { color: var(--muted); font-weight: 400; }

    .btn-primary {
      display: inline-flex; align-items: center; gap: 10px;
      text-decoration: none;
      padding: 12px 18px;
      border-radius: 9999px;
      font-weight: 600; font-size: 14px;
      color: #fff;
      background: var(--brand);
      border: 1px solid var(--brand-600);
      box-shadow: 0 6px 18px rgba(30,84,183,0.20);
      transition: transform .12s ease, box-shadow .2s ease, background .2s ease, filter .2s ease;
    }
    .btn-primary:hover {
      background: var(--brand-600);
      transform: translateY(-1px);
      box-shadow: 0 10px 24px rgba(30,84,183,0.28);
      filter: saturate(1.03);
    }
    .btn-primary:active { transform: translateY(0); box-shadow: 0 4px 14px rgba(30,84,183,0.18); }

    .support {
      margin-top: 26px; display: flex; justify-content: center; gap: 12px; flex-wrap: wrap; color: var(--muted);
    }
    .badge { padding: 6px 10px; border-radius: 999px; border: 1px dashed var(--border); font-size: 12px; }

    a:focus-visible, summary:focus-visible, .btn-primary:focus-visible { outline: none; box-shadow: var(--ring); }

    @media (prefers-reduced-motion: reduce) {
      * { transition: none !important; }
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <span class="kicker">SEFAZ-RJ</span>
      <h1>Painel principal — Secretaria de Estado de Fazenda do Rio de Janeiro</h1>
      <p class="subtitle">Quatro áreas de acesso rápido com informações e serviços relevantes para contribuintes e empresas.</p>
    </header>

    <div class="grid">
      <section class="card" aria-labelledby="c1-title">
        <div class="icon" aria-hidden="true">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path d="M12 3L1 8l11 5 9-4.09V17" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M7 12.5V17c0 0 2.5 2 5 2s5-2 5-2v-4.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <h2 id="c1-title">Serviços ao Contribuinte</h2>
        <p class="desc">IPVA, ICMS, certidões e serviços frequentes.</p>

        <details>
          <summary aria-controls="c1-menu" aria-expanded="false">Opções e atalhos</summary>
          <nav class="menu" id="c1-menu" aria-label="Atalhos — Serviços ao Contribuinte">
            <a href="#/ipva">IPVA <small>Calendário e emissão de DARJ</small></a>
            <a href="#/icms">ICMS <small>Guias e orientações</small></a>
            <a href="#/certidoes">Certidões Fiscais <small>Emissão e validação</small></a>
          </nav>
        </details>
      </section>

      <section class="card" aria-labelledby="c2-title">
        <div class="icon" aria-hidden="true">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path d="M3 21h18M5 21V7a2 2 0 012-2h10a2 2 0 012 2v14M9 21V5a2 2 0 012-2h2a2 2 0 012 2v16" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
            <path d="M7 10h2M7 14h2M15 10h2M15 14h2" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
          </svg>
        </div>
        <h2 id="c2-title">Institucional & Transparência</h2>
        <p class="desc">Missão, estrutura, relatórios e portais de transparência.</p>

        <details>
          <summary aria-controls="c2-menu" aria-expanded="false">Opções e atalhos</summary>
          <nav class="menu" id="c2-menu" aria-label="Atalhos — Institucional e Transparência">
            <a href="#/sobre">Sobre a SEFAZ-RJ <small>Missão e estrutura</small></a>
            <a href="#/transparencia">Transparência <small>Relatórios e despesas</small></a>
            <a href="#/legislacao">Legislação <small>Normas e decretos</small></a>
          </nav>
        </details>
      </section>

      <section class="card" aria-labelledby="c3-title">
        <div class="icon" aria-hidden="true">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path d="M16 21v-2a4 4 0 00-4-4H7a4 4 0 00-4 4v2" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
            <circle cx="9" cy="7" r="3" stroke="currentColor" stroke-width="1.6"/>
            <path d="M22 21v-2a4 4 0 00-3-3.87" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
            <path d="M16 3.13A3 3 0 0120 6a3 3 0 01-2 2.82" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
          </svg>
        </div>
        <h2 id="c3-title">Empresa & Negócios</h2>
        <p class="desc">Abertura de empresas, incentivos e serviços para negócios.</p>

        <details>
          <summary aria-controls="c3-menu" aria-expanded="false">Opções e atalhos</summary>
          <nav class="menu" id="c3-menu" aria-label="Atalhos — Empresa e Negócios">
            <a href="#/cnae">CNAE & Inscrições <small>Orientações e requisitos</small></a>
            <a href="#/incentivos">Incentivos fiscais <small>Programas e critérios</small></a>
            <a href="#/obrigacoes">Obrigações acessórias <small>Calendários e guias</small></a>
          </nav>
        </details>
      </section>

      <section class="card" aria-labelledby="c4-title">
        <div class="icon" aria-hidden="true">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke="currentColor" stroke-width="1.6"/>
            <path d="M16 2v4M8 2v4M3 10h18" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
          </svg>
        </div>
        <h2 id="c4-title">Atendimento & Agenda</h2>
        <p class="desc">Canais de atendimento, agendamentos e comunicados.</p>

        <details>
          <summary aria-controls="c4-menu" aria-expanded="false">Opções e atalhos</summary>
          <nav class="menu" id="c4-menu" aria-label="Atalhos — Atendimento e Agenda">
            <a href="#/agendamento">Agendamento presencial <small>Unidades e horários</small></a>
            <a href="#/faleconosco">Fale Conosco <small>Protocolos e dúvidas</small></a>
            <a href="#/noticias">Comunicados <small>Notícias oficiais</small></a>
          </nav>
        </details>
      </section>
    </div>
  </div>

  <script>
    document.querySelectorAll('details').forEach(d => {
      const summary = d.querySelector('summary');
      const set = () => summary && summary.setAttribute('aria-expanded', d.open ? 'true' : 'false');
      d.addEventListener('toggle', set); set();
    });
  </script>
</body>
</html>