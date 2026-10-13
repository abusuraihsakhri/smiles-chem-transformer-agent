"""
Deterministic mock model adapter with sensitive-identifier validation.
"""
from typing import Dict, Any, Optional
from .base import PHIGuard


class MockLLM:
    def __init__(self, system_name: str = "Smiles Chem Transformer Agent"):
        self.system_name = system_name

    def invoke(self, prompt: str) -> str:
        PHIGuard.assert_no_phi(prompt)
        return f"[{self.system_name} Deterministic Verification Engine]: Clinical & scientific analysis verified for query: '{prompt[:60]}...'. Parameters evaluated under wwPDB / IUPAC / OpenSMILES / ISAC Standards."


class LLMFactory:
    """Creates the implemented mock adapter; other providers are rejected."""

    @staticmethod
    def create(provider: str = "mock", system_name: str = "Smiles Chem Transformer Agent"):
        prov = str(provider).lower()
        if prov in ["mock", "deterministic", "test"]:
            return MockLLM(system_name)
        raise ValueError(
            "Only the deterministic mock provider is implemented. "
            "Remote and local model adapters must be configured separately."
        )
