from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json
import logging
from pathlib import Path
from datetime import datetime
import subprocess
import os

from .cli import (
    save_state,
    AGENTS_DIR,
    STATE_PATH,
    load_config,
    load_all_agents,
)
from .builder import create_agent_files
from .agents.oracle import OracleAgent
from .metrics import init_sentry
from prometheus_client import generate_latest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
init_sentry(os.getenv("SENTRY_DSN"))

app = FastAPI(title="Architect Agent System")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


class SpawnRequest(BaseModel):
    description: str
    name: Optional[str] = None


class InvokeRequest(BaseModel):
    parameters: Dict[str, Any] = {}


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    agents = load_all_agents()
    logger.info("Dashboard requested - %d agents", len(agents))
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "agents": agents, "agent_count": len(agents)},
    )


@app.post("/spawn")
async def spawn_agent(req: SpawnRequest):
    name = req.name or ''.join(c for c in req.description.lower().replace(' ', '_') if c.isalnum() or c == '_')[:20]
    try:
        agent_dir = create_agent_files(name, req.description, AGENTS_DIR)
    except FileExistsError:
        logger.error("Agent %s already exists", name)
        raise HTTPException(status_code=400, detail="Agent already exists")
    save_state(name, {"purpose": req.description, "path": str(agent_dir), "status": "created"})
    logger.info("Spawned agent %s", name)
    return {"status": "success", "agent": name}


@app.get("/agents")
async def list_agents():
    agents = load_all_agents()
    logger.info("Listing agents - %d found", len(agents))
    return {"agents": agents}


@app.post("/invoke/{agent_name}")
async def invoke_agent(agent_name: str, req: InvokeRequest | None = None):
    agents = load_all_agents()
    if not agents:
        raise HTTPException(status_code=404, detail="No agents")
    if agent_name not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    if agent_name == "oracle":
        config = load_config()
        if not config.get("llm_provider"):
            raise HTTPException(status_code=400, detail="No LLM configured")
        agent = OracleAgent(config)
        limit = req.parameters.get("limit", 10) if req else 10
        logger.info("Invoking oracle with limit=%d", limit)
        result = agent.run(limit)
    else:
        agent_dir = Path(agents[agent_name]["path"])
        cmd = ["python", "-m", f"{agent_name}.cli"]
        if req and req.parameters.get("verbose"):
            cmd.append("--verbose")
        logger.info("Running agent %s via CLI", agent_name)
        process = subprocess.run(cmd, cwd=agent_dir.parent, capture_output=True, text=True)
        result = {
            "returncode": process.returncode,
            "stdout": process.stdout,
            "stderr": process.stderr,
        }
    agents[agent_name]["invocations"] = agents[agent_name].get("invocations", 0) + 1
    agents[agent_name]["last_run"] = datetime.utcnow().isoformat()
    with open(STATE_PATH, "w") as f:
        json.dump(agents, f, indent=2)
    logger.info("Invocation complete for %s", agent_name)
    return result


@app.get("/metrics")
async def metrics() -> HTMLResponse:
    """Expose Prometheus metrics."""
    data = generate_latest()
    return HTMLResponse(data, media_type="text/plain")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
