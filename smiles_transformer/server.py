"""
FastAPI REST API Server for SMILES-Grammar: Molecular Valence, Tautomer Enumerator & RDKit Canonicalizer.
"""
from typing import Dict, Any
from .models import FrontierPayload
from .agents import SMILESGrammarCoordinator

coordinator = SMILESGrammarCoordinator()


def create_app():
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel, Field
        from fastapi import HTTPException

        app = FastAPI(
            title="SMILES-Grammar: Molecular Valence, Tautomer Enumerator & RDKit Canonicalizer",
            description="Legacy numeric-rule audit coordinator plus RDKit-backed SMILES analysis.",
            version="2.0.0-FRONTIER",
        )

        class TaskRequest(BaseModel):
            task_id: str = "TASK-2026-001"
            target_identifier: str = "TARGET-BIO-KEY"
            primary_metric: float = 28.5
            secondary_metric: float = 14.2
            status_descriptor: str = "DISCORDANT_ANOMALY"
            is_critical_flag: bool = True
            attributes: Dict[str, Any] = Field(default_factory=dict)

        class MoleculeRequest(BaseModel):
            smiles: str = Field(min_length=1, max_length=2048)
            max_tautomers: int = Field(default=20, ge=1, le=50)

        class ChatRequest(BaseModel):
            query: str

        @app.get("/health")
        def health():
            return {"status": "HEALTHY", "system": "smiles-chem-transformer-agent", "domain": "Computational Chemistry & AI Drug Discovery", "version": "2.0.0-FRONTIER"}

        @app.post("/api/audit")
        def api_audit(req: TaskRequest):
            payload = FrontierPayload(
                task_id=req.task_id,
                target_identifier=req.target_identifier,
                primary_metric=req.primary_metric,
                secondary_metric=req.secondary_metric,
                status_descriptor=req.status_descriptor,
                is_critical_flag=req.is_critical_flag,
                attributes=req.attributes,
            )
            return coordinator.process(payload)

        @app.post("/api/chat")
        def api_chat(req: ChatRequest):
            return {"response": coordinator.query_supervisory_chat(req.query)}

        @app.post("/api/molecule")
        def api_molecule(req: MoleculeRequest):
            from .chemistry import analyze_smiles, MoleculeInputError
            try:
                return analyze_smiles(req.smiles, req.max_tautomers)
            except MoleculeInputError as exc:
                raise HTTPException(status_code=422, detail=str(exc)) from exc
            except RuntimeError as exc:
                raise HTTPException(status_code=503, detail="Molecule analysis is unavailable.") from exc

        return app
    except ImportError:
        return None
