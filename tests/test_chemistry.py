import pytest
from smiles_transformer.chemistry import MoleculeInputError, analyze_smiles


def test_canonical_stereo_and_formula():
    result = analyze_smiles("OCC")
    assert result["canonical_smiles"] == "CCO"
    assert result["molecular_formula"] == "C2H6O"
    assert result["atom_count"] == 3
    assert result["inchikey"] is None or len(result["inchikey"]) == 27
    assert result["tautomers"]
    stereo = analyze_smiles("F[C@H](Cl)Br")
    assert "@" in stereo["canonical_smiles"]


def test_bad_valence_and_limits():
    for smiles in ("", " ", "this is not smiles", "C(C)(C)(C)(C)C", "C" * 2049):
        with pytest.raises(MoleculeInputError):
            analyze_smiles(smiles)
    for n in (0, 51, 2.5, True):
        with pytest.raises(MoleculeInputError):
            analyze_smiles("CCO", max_tautomers=n)


def test_tautomer_enumeration_has_unique_canonical_results():
    res = analyze_smiles("CC(=O)C", max_tautomers=1)
    assert len(res["tautomers"]) == 1
    assert res["tautomer_count"] >= 1
    assert res["tautomers_truncated"] == (res["tautomer_count"] > 1)
