"""
FastAPI REST API Server for Smiles Chem Transformer Agent.
"""
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from pydantic import Field
from pathlib import Path
from pydantic import BaseModel
from .base import AuditLogger, PHIGuard, SecurityException
from smiles_transformer.chemistry import analyze_smiles, MoleculeInputError
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Smiles Chem Transformer Agent API",
    description="Enterprise Distributed Component Platform (AI Drug Discovery, Structural Biology & Wet-Lab Robotics)",
    version="3.0.0-ENTERPRISE",
)


class MoleculeRequest(BaseModel):
    smiles: str = Field(min_length=1, max_length=2048)
    max_tautomers: int = Field(default=20, ge=1, le=50)


class ChatRequest(BaseModel):
    query: str


@app.exception_handler(SecurityException)
async def reject_sensitive_data(request: Request, exc: SecurityException):
    return JSONResponse(status_code=422, content={"detail": "Sensitive identifiers are not accepted."})


@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(Path(__file__).resolve().parent.parent / "web" / "index.html")


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "smiles-chem-transformer-agent", "domain": "AI Drug Discovery, Structural Biology & Wet-Lab Robotics", "standard": "wwPDB / IUPAC / OpenSMILES / ISAC Standards", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    dossier = supervisor.process_task(payload)
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}


@app.post("/api/molecule")
def api_molecule(request: MoleculeRequest):
    try:
        return analyze_smiles(request.smiles, request.max_tautomers)
    except MoleculeInputError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail="Molecule analysis is unavailable.") from exc
