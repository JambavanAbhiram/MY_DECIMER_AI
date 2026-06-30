#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import sys
get_ipython().system('{sys.executable} -m pip install -q DECIMER rdkit pubchempy pandas')


# In[ ]:


import os, cv2, numpy as np, pandas as pd
from PIL import Image
from rdkit import Chem
from rdkit.Chem.Draw import rdMolDraw2D

IMAGE_DIR   = "/content"                 # folder with your images
OUT_DIR     = "/content/output"          # results go here
TRY_HAND_DRAWN = True                    # also try DECIMER's hand-drawn model (slower, helps sketches)
USE_PUBCHEM    = True                    # verify reads against PubChem (needs internet)

# OPTIONAL: known correct SMILES to measure real accuracy. Leave {} if you don't have them.
GROUND_TRUTH = {
    # "molecule": "CN1C=NC2=C1C(=O)N(C)C(=O)N2C",
    # "mix1_aspirin_lowres": "CC(=O)Oc1ccccc1C(=O)O",
}
os.makedirs(OUT_DIR, exist_ok=True)


# In[ ]:


def _strip_frame(gray, dark=70, area_frac=0.03):
    mask=(gray<dark).astype(np.uint8); n,lab,st,_=cv2.connectedComponentsWithStats(mask,8)
    H,W=gray.shape; out=gray.copy()
    for i in range(1,n):
        x,y,w,h,a=st[i]
        if (x==0 or y==0 or x+w==W or y+h==H) and a>area_frac*H*W: out[lab==i]=255
    return out

def clean_image(src, binarize=True):
    img=cv2.imread(src) if isinstance(src,str) else src
    if img is None: raise FileNotFoundError(src)
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) if img.ndim==3 else img
    H,W=gray.shape
    is_clean = gray.mean()>235 and gray.std()<45          # already a clean digital drawing?
    if not is_clean:
        gray=_strip_frame(gray)
        if max(H,W)<500:                                  # upscale tiny images
            pil=Image.fromarray(gray); gray=np.array(pil.resize((pil.width*2,pil.height*2),Image.LANCZOS))
        k=max(15,(min(gray.shape)//12)|1)                 # flat-field: remove paper/stains/gradient
        bg=cv2.morphologyEx(gray,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(k,k)))
        gray=cv2.normalize(cv2.divide(gray,bg,scale=255),None,0,255,cv2.NORM_MINMAX).astype(np.uint8)
        gray=cv2.bilateralFilter(gray,7,50,50)
    if not binarize: return gray
    _,b=cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU); return b


# In[ ]:


# 4) Recognise: multi-variant CONSENSUS + salt-stripping (the accuracy engine)
from collections import Counter
from rdkit.Chem.MolStandardize import rdMolStandardize
_chooser = rdMolStandardize.LargestFragmentChooser()
IMPROBABLE = set("Ga Ge As Se Sb Te Sn Pb Hg Tl Bi Al Si B Zn Fe Cu Ni Co Mn Cr".split())
_pubchem_cache = {}

def _variants(image_path, work_dir):
    os.makedirs(work_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(image_path))[0]
    v = {"original": image_path}
    bp = os.path.join(work_dir, base + "_bin.png");  cv2.imwrite(bp, clean_image(image_path, True))
    gp = os.path.join(work_dir, base + "_gray.png"); cv2.imwrite(gp, clean_image(image_path, False))
    v["cleaned_binary"] = bp; v["cleaned_gray"] = gp
    return v

def _decimer_model(path, hand_drawn=False):
    from DECIMER import predict_SMILES
    for kw in ({"confidence": True, "hand_drawn": hand_drawn}, {"confidence": True},
               {"hand_drawn": hand_drawn}, {}):
        try:
            out = predict_SMILES(path, **kw)
            if isinstance(out, tuple):
                try: conf = float(np.mean([c[1] for c in out[1]]))
                except Exception: conf = None
                return out[0], conf
            return out, None
        except TypeError:
            continue
    return None, None

def _molscribe_model(path, hand_drawn=False):
    try:
        global _MOLSCRIBE
        if "_MOLSCRIBE" not in globals():
            from molscribe import MolScribe
            import torch, huggingface_hub
            ckpt = huggingface_hub.hf_hub_download("yujieq/MolScribe", "swin_base_char_aux_1m.pth")
            _MOLSCRIBE = MolScribe(ckpt, device=torch.device("cpu"))
        r = _MOLSCRIBE.predict_image_file(path)
        return r["smiles"], r.get("confidence")
    except Exception:
        return None, None   # not installed -> skipped in the vote

MODELS = [("DECIMER", _decimer_model), ("MolScribe", _molscribe_model)]

def _sanitize(smiles):
    if not smiles: return None, {}
    m = Chem.MolFromSmiles(smiles)
    if m is None: return None, {}
    n_frag = len(Chem.GetMolFrags(m))
    m = _chooser.choose(m)
    elems = {a.GetSymbol() for a in m.GetAtoms()}
    return Chem.MolToSmiles(m), {
        "improbable": sorted(elems & IMPROBABLE),
        "halogens": sorted(elems & set("F Cl Br I".split())),
        "had_fragments": n_frag > 1,
    }

def _pubchem_ok(smiles):
    if not USE_PUBCHEM or not smiles: return None
    if smiles in _pubchem_cache: return _pubchem_cache[smiles]
    import time
    try:
        import pubchempy as pcp
        from rdkit.Chem import inchi as rdi
        ik = rdi.InchiToInchiKey(rdi.MolToInchi(Chem.MolFromSmiles(smiles)))
        ans = None
        for _ in range(3):
            try:
                ans = bool(pcp.get_compounds(ik, "inchikey")); break
            except Exception:
                time.sleep(1.0)
        _pubchem_cache[smiles] = ans
        return ans
    except Exception:
        return None

def recognize(image_path, work_dir):
    reads = []
    for vpath in _variants(image_path, work_dir).values():
        for mname, mfn in MODELS:
            for hd in ([False, True] if (TRY_HAND_DRAWN and mname == "DECIMER") else [False]):
                smi, conf = mfn(vpath, hand_drawn=hd)
                clean, info = _sanitize(smi)
                if clean and not info.get("improbable"):
                    reads.append((clean, conf or 0.0, bool(info.get("halogens")),
                                  bool(info.get("had_fragments"))))
    if not reads:
        return {"smiles": None, "trust": False, "votes": 0, "total": 0,
                "agreement": 0, "confidence": None, "needs_review": True}

    votes = Counter(r[0] for r in reads)
    best, n = votes.most_common(1)[0]
    total = len(reads)
    best_conf = max(r[1] for r in reads if r[0] == best)
    had_halogen = any(r[2] for r in reads if r[0] == best)
    agreement = n / total

    in_pc = _pubchem_ok(best)
    trust = (n >= 2 and agreement >= 0.5) or (best_conf >= 0.9 and len(votes) == 1)
    if in_pc is False and n < 2:
        trust = False
    needs_review = (not trust) or had_halogen

    return {"smiles": best, "trust": bool(trust), "votes": n, "total": total,
            "agreement": round(agreement, 2), "confidence": round(best_conf, 3),
            "in_pubchem": in_pc, "needs_review": bool(needs_review)}


# In[ ]:


def redraw(smiles, out_base, width=1600, height=1200, bond_width=4):
    mol=Chem.MolFromSmiles(smiles)
    if mol is None: return None
    d=rdMolDraw2D.MolDraw2DCairo(width,height); d.drawOptions().bondLineWidth=bond_width
    rdMolDraw2D.PrepareAndDrawMolecule(d,mol); d.FinishDrawing()
    png=out_base+"_highres.png"; open(png,"wb").write(d.GetDrawingText())
    d2=rdMolDraw2D.MolDraw2DSVG(width,height); d2.drawOptions().bondLineWidth=bond_width
    rdMolDraw2D.PrepareAndDrawMolecule(d2,mol); d2.FinishDrawing()
    open(out_base+"_highres.svg","w").write(d2.GetDrawingText())
    return png


# In[ ]:


# 6) Run on every image -> CSV + accuracy summary  (always redraws; trust is a LABEL)
work_dir = os.path.join(OUT_DIR, "_tmp")
rows = []; n = correct = trusted = 0

image_files = sorted(f for f in os.listdir(IMAGE_DIR)
                     if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff"))
                     and "_highres" not in f and "_cleaned" not in f)

for fname in image_files:
    path = os.path.join(IMAGE_DIR, fname); name = os.path.splitext(fname)[0]; n += 1
    try:
        best = recognize(path, work_dir)
    except Exception as e:
        rows.append({"image": fname, "smiles": f"ERROR: {e}", "trust": False,
                     "needs_review": True}); continue

    # ALWAYS draw the best structure so you can see every result; trust just tells you whether to double-check
    highres = redraw(best["smiles"], os.path.join(OUT_DIR, name)) if best["smiles"] else None

    correct_flag = None
    if name in GROUND_TRUTH:
        gt = Chem.MolFromSmiles(GROUND_TRUTH[name])
        gt = Chem.MolToSmiles(gt) if gt else None
        correct_flag = int(best["smiles"] == gt); correct += correct_flag
    trusted += int(best["trust"])

    rows.append({"image": fname, "smiles": best["smiles"], "votes": f"{best['votes']}/{best['total']}",
                 "agreement": best["agreement"], "confidence": best["confidence"],
                 "in_pubchem": best.get("in_pubchem"), "trust": best["trust"],
                 "needs_review": best["needs_review"], "highres": highres, "correct": correct_flag})
    tag = "OK   " if best["trust"] else "CHECK"
    print(f"[{tag}] {fname:28s} {best['votes']}/{best['total']} agree  {best['smiles']}")

df = pd.DataFrame(rows); df.to_csv(os.path.join(OUT_DIR, "results.csv"), index=False)
print("\n================ SUMMARY ================")
print(f"images processed : {n}")
print(f"trusted          : {trusted}/{n}  (others are produced too, just flagged needs_review)")
n_gt = sum(1 for r in rows if r.get('correct') is not None)
if n_gt:
    print(f"EXACT-MATCH ACC  : {correct}/{n_gt} = {100*correct/n_gt:.0f}%   (vs GROUND_TRUTH)")
else:
    print("EXACT-MATCH ACC  : fill GROUND_TRUTH in cell 2 to measure real accuracy")
print(f"\nResults CSV: {os.path.join(OUT_DIR, 'results.csv')}")
df

