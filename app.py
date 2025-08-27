# app.py
# ----------------------------------
# Backend FastAPI que lê o dashboard do Grafana (Zabbix) e
# expõe endpoints para o seu front pintar os botões com as cores reais.

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

GRAFANA_URL = (os.getenv("GRAFANA_URL") or "").rstrip("/")
GRAFANA_API_KEY = os.getenv("GRAFANA_API_KEY") or ""
GRAFANA_ORG_ID = os.getenv("GRAFANA_ORG_ID") or ""
DASHBOARD_UID = os.getenv("DASHBOARD_UID") or ""  # ex.: "aetaxi4410irkf"

app = FastAPI(title="SEFAZ Monitor (Grafana/Zabbix)")

# -------------------------------
# Helpers
# -------------------------------

def _headers() -> Dict[str, str]:
    if not GRAFANA_URL or not GRAFANA_API_KEY:
        raise HTTPException(500, "Configure GRAFANA_URL e GRAFANA_API_KEY no .env")
    h = {"Authorization": f"Bearer {GRAFANA_API_KEY}", "Accept": "application/json"}
    if GRAFANA_ORG_ID:
        h["X-Grafana-Org-Id"] = str(GRAFANA_ORG_ID)
    return h

def _last_numeric_from_result(result: Dict[str, Any]) -> Optional[float]:
    """Tenta achar o último valor numérico em frames/tables/series (Grafana 8+ e legados)."""
    # frames (padrão moderno)
    for fr in result.get("frames") or []:
        values = (fr.get("data") or {}).get("values") or []
        for col in reversed(values):
            if isinstance(col, list):
                for v in reversed(col):
                    try:
                        if v is None:
                            continue
                        return float(v)
                    except Exception:
                        pass
    # tables (legado)
    for tb in result.get("tables") or []:
        for row in reversed(tb.get("rows") or []):
            for v in reversed(row):
                try:
                    if v is None:
                        continue
                    return float(v)
                except Exception:
                    pass
    # series (bem legado)
    for s in result.get("series") or []:
        for p in reversed(s.get("points") or []):
            if isinstance(p, (list, tuple)) and p:
                try:
                    return float(p[0])
                except Exception:
                    pass
    return None

def _hex_from_css(color: str) -> str:
    """Converte 'rgb(a)'/nome para hex (#rrggbb) quando possível; senão retorna a própria string."""
    if not color:
        return color
    color = color.strip().lower()
    named = {
        "red": "#ef4444",
        "green": "#22c55e",
        "yellow": "#eab308",
        "orange": "#f97316",
        "blue": "#3b82f6",
        "purple": "#a855f7",
        "gray": "#9ca3af",
        "white": "#ffffff",
        "black": "#000000",
        "dark-red": "#8b0000",
        "semi-dark-red": "#b22222",
    }
    if color in named:
        return named[color]
    if color.startswith(("rgba", "rgb")):
        nums = color[color.find("(") + 1 : color.find(")")].split(",")
        if len(nums) >= 3:
            try:
                r = int(float(nums[0]))
                g = int(float(nums[1]))
                b = int(float(nums[2]))
                return f"#{r:02x}{g:02x}{b:02x}"
            except Exception:
                pass
    return color

def _match_panel(all_panels: List[Dict[str, Any]], token: str) -> Optional[Dict[str, Any]]:
    """Encontra painel por id, title ou options.panelName (case-insensitive)."""
    tk = token.strip()
    if not tk:
        return None
    if tk.isdigit():
        p = next((x for x in all_panels if x.get("id") == int(tk)), None)
        if p:
            return p
    t = tk.lower()
    for x in all_panels:
        if str(x.get("title", "")).lower() == t:
            return x
        if str((x.get("options") or {}).get("panelName", "")).lower() == t:
            return x
    return None

def _is_redish(hex_color: str) -> bool:
    """Heurística simples para detectar 'vermelho'."""
    if not hex_color or not hex_color.startswith("#") or len(hex_color) < 7:
        return False
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    return (r > g + 20) and (r > b + 20)

# -------------------------------
# Grafana access
# -------------------------------

async def _get_dashboard_json(cli: httpx.AsyncClient) -> Dict[str, Any]:
    url = f"{GRAFANA_URL}/api/dashboards/uid/{DASHBOARD_UID}"
    r = await cli.get(url, headers=_headers())
    if r.status_code != 200:
        raise HTTPException(r.status_code, f"Erro ao ler dashboard: HTTP {r.status_code}")
    return r.json()

async def _panel_status_by_obj(cli: httpx.AsyncClient, panel: Dict[str, Any]) -> Dict[str, Any]:
    """Consulta a mesma query do painel e deduz 'down' e 'color'."""
    pid = panel.get("id")
    title = panel.get("title")
    opts = panel.get("options") or {}
    panel_name = opts.get("panelName")
    ptype = (panel.get("type") or "").lower()
    datasource = panel.get("datasource") or {}
    targets = panel.get("targets") or []

    # Janela de tempo curta para "estado atual"
    now = datetime.now(timezone.utc)
    body = {
        "queries": [],
        "range": {"from": (now - timedelta(minutes=5)).isoformat(), "to": now.isoformat()},
        "from": (now - timedelta(minutes=5)).isoformat(),
        "to": now.isoformat(),
    }
    ref = 65  # 'A', 'B', ...
    for t in targets:
        q = dict(t)
        q.setdefault("refId", chr(ref))
        ref += 1
        q["datasource"] = datasource
        q.setdefault("intervalMs", 10000)
        q.setdefault("maxDataPoints", 200)
        body["queries"].append(q)

    last_val: Optional[float] = None
    if body["queries"]:
        r = await cli.post(f"{GRAFANA_URL}/api/ds/query", headers=_headers(), json=body)
        if r.status_code == 200:
            data = r.json()
            for res in (data.get("results") or {}).values():
                last_val = _last_numeric_from_result(res)
                if last_val is not None:
                    break
        else:
            # Falha na query – sinalize erro, cor de desastre, down True
            bad = _hex_from_css(opts.get("ColorDisaster") or "#ef4444")
            return {
                "id": pid,
                "title": title,
                "name": panel_name,
                "value": None,
                "color": bad,
                "down": True,
                "error": f"query HTTP {r.status_code}",
            }

    # Lógica de estado para o plugin 'serrrios-statusoverview-panel':
    # - regra simples: se last_val > 0 => DOWN (há triggers/alertas)
    # - senão UP
    ok_color = _hex_from_css(opts.get("ColorOK") or "#22c55e")
    bad_color = _hex_from_css(opts.get("ColorDisaster") or "#ef4444")

    down: Optional[bool] = None
    if "statusoverview" in ptype:
        if last_val is not None:
            down = last_val > 0
        else:
            # sem dado — mantenha UP por padrão, mas você pode marcar como down se preferir
            down = False
    else:
        # Outros tipos: heurística básica (se cor do OK/Disaster estiver invertida, o down será ajustado pela cor)
        down = False

    color = bad_color if down else ok_color

    return {
        "id": pid,
        "title": title,
        "name": panel_name,
        "value": last_val,
        "color": color,
        "down": bool(down),
    }

# -------------------------------
# Endpoints
# -------------------------------

@app.get("/grafana_diag")
async def grafana_diag():
    async with httpx.AsyncClient(timeout=10.0) as cli:
        health = await cli.get(f"{GRAFANA_URL}/api/health", headers=_headers())
        dash = await cli.get(f"{GRAFANA_URL}/api/dashboards/uid/{DASHBOARD_UID}", headers=_headers())
    return JSONResponse(
        {
            "env": {
                "url": GRAFANA_URL,
                "org": GRAFANA_ORG_ID or None,
                "dashboard_uid": DASHBOARD_UID or None,
                "apiKeySet": bool(GRAFANA_API_KEY),
            },
            "health": {"code": health.status_code, "body": (health.json() if "json" in health.headers.get("content-type","") else health.text[:300])},
            "dashboard": {"code": dash.status_code, "ok": dash.status_code == 200},
        }
    )

@app.get("/dashboard_panels")
async def dashboard_panels():
    async with httpx.AsyncClient(timeout=10.0) as cli:
        data = await _get_dashboard_json(cli)
    panels = data.get("dashboard", {}).get("panels", [])
    out = []
    for p in panels:
        opts = p.get("options") or {}
        out.append(
            {
                "id": p.get("id"),
                "title": p.get("title"),          # pode ser None nesse plugin
                "name": opts.get("panelName"),    # nome visível no bloco
                "type": p.get("type"),
            }
        )
    return {"uid": DASHBOARD_UID, "count": len(out), "panels": out}

@app.get("/multi_status")
async def multi_status(
    panels: str = Query(..., description="lista separada por vírgula: id OU title OU panelName (exatos)")
):
    tokens = [s.strip() for s in panels.split(",") if s.strip()]
    if not tokens:
        raise HTTPException(400, "informe ao menos um painel")

    async with httpx.AsyncClient(timeout=15.0) as cli:
        dash = await _get_dashboard_json(cli)
        all_panels = dash.get("dashboard", {}).get("panels", [])
        resolved: List[Dict[str, Any]] = []
        for tk in tokens:
            p = _match_panel(all_panels, tk)
            if p:
                resolved.append(p)

        if not resolved:
            raise HTTPException(404, "painéis não encontrados")

        out = []
        for p in resolved:
            out.append(await _panel_status_by_obj(cli, p))
        return {"count": len(out), "items": out}

# -------------------------------
# Static frontend (pasta src/)
# -------------------------------
# Sirva seu index.html/css/js a partir de ./src
app.mount("/", StaticFiles(directory="src", html=True), name="static")

# Execução local (fora do Docker)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=True)
