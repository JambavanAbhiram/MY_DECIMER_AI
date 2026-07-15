from rdkit import Chem

def canonicalize(smiles):
    if smiles is None:
        return None
    s=str(smiles).strip()
    if not s:
        return None
    try:
        mol=Chem.MolFromSmiles(s)
        if mol is None:
            return None
        return Chem.MolToSmiles(mol,canonical=True)
    except Exception:
        return None
