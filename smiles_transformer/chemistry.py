"""RDKit-backed SMILES validation, normalization, descriptors and tautomer analysis."""
from __future__ import annotations

from typing import Any

MAX_SMILES_LENGTH = 2048
MAX_ATOMS = 256
MAX_TAUTOMERS = 128


class MoleculeInputError(ValueError):
    """The supplied SMILES is invalid or exceeds operational limits."""


def analyze_smiles(smiles: str, max_tautomers: int = 20) -> dict[str, Any]:
    """Analyze a single structure; all chemistry is calculated by RDKit.

    Canonical SMILES retains stereochemical information. Tautomers are
    enumerated and canonicalized without claiming experimental predominance.
    """
    if not isinstance(smiles, str) or not smiles.strip():
        raise MoleculeInputError("Provide a nonempty SMILES string.")
    smiles = smiles.strip()
    if len(smiles) > MAX_SMILES_LENGTH:
        raise MoleculeInputError(f"SMILES must be at most {MAX_SMILES_LENGTH} characters.")
    if type(max_tautomers) is not int or not 1 <= max_tautomers <= 50:
        raise MoleculeInputError("max_tautomers must be an integer between 1 and 50.")

    try:
        from rdkit import Chem, rdBase
        from rdkit.Chem import Descriptors, rdMolDescriptors
        from rdkit.Chem.MolStandardize import rdMolStandardize
    except ImportError as exc:
        raise RuntimeError("RDKit is required. Install with pip install '.[chem]'.") from exc

    with rdBase.BlockLogs():
        try:
            mol = Chem.MolFromSmiles(smiles)
        except (ValueError, RuntimeError) as exc:
            raise MoleculeInputError("Invalid SMILES or unsupported valence.") from exc
    if mol is None:
        raise MoleculeInputError("Invalid SMILES or unsupported valence.")
    if mol.GetNumAtoms() > MAX_ATOMS:
        raise MoleculeInputError(f"Molecule exceeds {MAX_ATOMS} atoms.")

    canonical = Chem.MolToSmiles(mol, canonical=True, isomericSmiles=True)
    enumerator = rdMolStandardize.TautomerEnumerator()
    enumerator.SetMaxTautomers(MAX_TAUTOMERS)
    with rdBase.BlockLogs():
        enumerated = enumerator.Enumerate(mol)
    tautomer_smiles = sorted({Chem.MolToSmiles(t, canonical=True, isomericSmiles=True)
                              for t in enumerated})
    try:
        preferred = Chem.MolToSmiles(enumerator.Canonicalize(mol), isomericSmiles=True)
    except (RuntimeError, ValueError):
        preferred = canonical

    inchi = None
    inchikey = None
    try:
        from rdkit.Chem import inchi as rd_inchi
        inchi = rd_inchi.MolToInchi(mol) or None
        if inchi:
            inchikey = rd_inchi.InchiToInchiKey(inchi) or None
    except (ImportError, RuntimeError, ValueError):
        pass

    return {
        "input_smiles": smiles,
        "canonical_smiles": canonical,
        "tautomer_canonical_smiles": preferred,
        "molecular_formula": rdMolDescriptors.CalcMolFormula(mol),
        "molecular_weight": round(Descriptors.MolWt(mol), 4),
        "exact_mass": round(Descriptors.ExactMolWt(mol), 4),
        "atom_count": mol.GetNumAtoms(),
        "bond_count": mol.GetNumBonds(),
        "formal_charge": Chem.GetFormalCharge(mol),
        "inchi": inchi,
        "inchikey": inchikey,
        "tautomers": tautomer_smiles[:max_tautomers],
        "tautomer_count": len(tautomer_smiles),
        "tautomers_truncated": len(tautomer_smiles) > max_tautomers or len(enumerated) >= MAX_TAUTOMERS,
        "note": "Computed structures are not experimental evidence of tautomer abundance or stability.",
    }
