import os
from typing import Dict
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import httpx
from dotenv import load_dotenv

# ===== carregar .env =====
load_dotenv()
GRAFANA_URL = (os.getenv("GRAFANA_URL") or "").rstrip("/")
GRAFANA_API_KEY = os.getenv("GRAFANA_API_KEY") or ""
GRAFANA_ORG_ID = os.getenv("GRAFANA_ORG_ID") or ""

# mapeie aqui quando souber as labels reais
SERVICE_MAP: Dict[str, Dict[str, str]] = {
    "sincad-web":     {"service": "sincad_web"},
    "sincad-rest":    {"service": "sincad_rest"},
    "sincad-portal":  {"service": "sincad_portal"},
    "sincad-service": {"service": "sincad_service"},
}

app = FastAPI(title="ACSEFAZ Monitor")

def _headers():
    h = {"Authorization": f"Bearer {GRAFANA_API_KEY}", "Accept": "application/json"}
    if GRAFANA_ORG_ID:
        h["X-Grafana-Org-Id"] = str(GRAFANA_ORG_ID)
    return h

def _match(alert: dict, wanted: dict) -> bool:
    labels = alert.get("labels") or {}
    return all(labels.get(k) == v for k, v in wanted.items())

@app.get("/grafana_diag")
async def grafana_diag():
    """Diagnóstico para saber se URL/key/org estão OK e o que a API responde."""
    if not GRAFANA_URL or not GRAFANA_API_KEY:
        raise HTTPException(500, "GRAFANA_URL ou GRAFANA_API_KEY ausentes no .env")

    out = {"env": {"url": GRAFANA_URL, "org": GRAFANA_ORG_ID, "apiKeySet": bool(GRAFANA_API_KEY)}}

    async with httpx.AsyncClient(timeout=8.0) as cli:
        def pack(r):
            try:
                body = r.json()
            except Exception:
                body = r.text[:1000]
            return {"code": r.status_code, "body": body}

        r1 = await cli.get(f"{GRAFANA_URL}/api/health", headers=_headers())
        r2 = await cli.get(f"{GRAFANA_URL}/api/ruler/grafana/api/v1/rules", headers=_headers())
        r3 = await cli.get(f"{GRAFANA_URL}/api/alertmanager/grafana/api/v2/alerts?active=true&silenced=false&inhibited=false", headers=_headers())
        # legado (pode não existir; é só pra diagnóstico)
        r4 = await cli.get(f"{GRAFANA_URL}/api/alerts", headers=_headers())

    return JSONResponse({
        "env": out["env"],
        "health": pack(r1),
        "rules":  pack(r2),
        "alerts_v2": pack(r3),
        "alerts_legacy": pack(r4)
    })

@app.get("/grafana_status")
async def grafana_status(svc: str = Query(..., description="ex.: sincad-web")):
    """Retorna ok/down com base nas labels mapeadas para cada serviço."""
    if not GRAFANA_URL or not GRAFANA_API_KEY:
        raise HTTPException(500, "Config ausente (URL/API_KEY)")

    wanted = SERVICE_MAP.get(svc)
    if not wanted:
        raise HTTPException(400, "svc desconhecido (adicione no SERVICE_MAP)")

    async with httpx.AsyncClient(timeout=8.0) as cli:
        # 1) tenta Unified Alerting (v2)
        url_v2 = f"{GRAFANA_URL}/api/alertmanager/grafana/api/v2/alerts?active=true&silenced=false&inhibited=false"
        r = await cli.get(url_v2, headers=_headers())
        if r.status_code == 200:
            alerts = r.json() if r.headers.get("content-type","").startswith("application/json") else []
            firing = [a for a in alerts if _match(a, wanted) and str(a.get("status",{}).get("state","")).lower()=="firing"]
            return {"ok": len(firing) == 0, "active_alerts": len(firing), "source": "v2"}

        # 2) fallback para alerting legado
        url_legacy = f"{GRAFANA_URL}/api/alerts"
        r2 = await cli.get(url_legacy, headers=_headers())
        if r2.status_code == 200:
            legacy = r2.json() if r2.headers.get("content-type","").startswith("application/json") else []
            down = any(str(a.get("state","")).lower() == "alerting" for a in legacy)
            return {"ok": not down, "active_alerts": 1 if down else 0, "source": "legacy"}

    raise HTTPException(502, "Não foi possível consultar alertas (v2 e legado)")

# Sirva sua pasta 'src' no mesmo host/porta (evita CORS)
app.mount("/", StaticFiles(directory="src", html=True), name="static")
