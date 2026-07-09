"""
recognition/recognizer.py

DECIMER Recognition Engine

Author: DECIMER Project
"""

from pathlib import Path
import os
from typing import Counter
import cv2
import numpy as np
from PIL import Image
from rdkit import Chem
from rdkit.Chem.MolStandardize import rdMolStandardize

from core.config import TEMP_ROOT

class DecimerRecognizer:

    IMPROBABLE={
        "Ga","Ge","As","Se","Sb","Te",
        "Sn","Pb","Hg","Tl","Bi",
        "Al","Si","B",
        "Zn","Fe","Cu","Ni","Co","Mn","Cr"
    }

    HALOGENS={"F","Cl","Br","I"}

    def __init__(
        self,
        try_hand_drawn=True,
        use_pubchem=True,
        use_molscribe=True,
    ):

        self.try_hand_drawn=try_hand_drawn
        self.use_pubchem=use_pubchem
        self.use_molscribe=use_molscribe

        self.work_dir=Path(TEMP_ROOT)/"recognizer"
        self.work_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.fragment_chooser=(
            rdMolStandardize.LargestFragmentChooser()
        )

        self.pubchem_cache={}

        self._molscribe=None

    # ---------------------------------------------------------

    @staticmethod
    def _strip_frame(
        gray,
        dark=70,
        area_frac=0.03,
    ):

        mask=(gray<dark).astype(np.uint8)

        n,labels,stats,_=cv2.connectedComponentsWithStats(
            mask,
            8,
        )

        H,W=gray.shape

        output=gray.copy()

        for i in range(1,n):

            x,y,w,h,area=stats[i]

            touches=(
                x==0 or
                y==0 or
                x+w==W or
                y+h==H
            )

            if touches and area>area_frac*H*W:
                output[labels==i]=255

        return output

    # ---------------------------------------------------------

    def clean_image(
        self,
        image,
        binarize=True,
    ):

        if isinstance(image,(str,Path)):
            image=cv2.imread(str(image))

        if image is None:
            raise FileNotFoundError(image)

        if image.ndim==3:
            gray=cv2.cvtColor(
                image,
                cv2.COLOR_BGR2GRAY,
            )
        else:
            gray=image

        H,W=gray.shape

        clean=(
            gray.mean()>235 and
            gray.std()<45
        )

        if not clean:

            gray=self._strip_frame(gray)

            if max(H,W)<500:

                pil=Image.fromarray(gray)

                pil=pil.resize(
                    (
                        pil.width*2,
                        pil.height*2,
                    ),
                    Image.LANCZOS,
                )

                gray=np.array(pil)

            kernel=max(
                15,
                (min(gray.shape)//12)|1,
            )

            background=cv2.morphologyEx(

                gray,

                cv2.MORPH_CLOSE,

                cv2.getStructuringElement(

                    cv2.MORPH_ELLIPSE,

                    (kernel,kernel),

                ),

            )

            gray=cv2.normalize(

                cv2.divide(

                    gray,

                    background,

                    scale=255,

                ),

                None,

                0,

                255,

                cv2.NORM_MINMAX,

            ).astype(np.uint8)

            gray=cv2.bilateralFilter(

                gray,

                7,

                50,

                50,

            )

        if not binarize:
            return gray

        _,binary=cv2.threshold(

            gray,

            0,

            255,

            cv2.THRESH_BINARY+
            cv2.THRESH_OTSU,

        )

        return binary

    # ---------------------------------------------------------

    def _save_variant(
        self,
        image,
        filename,
    ):

        path=self.work_dir/filename

        cv2.imwrite(
            str(path),
            image,
        )

        return str(path)

    # ---------------------------------------------------------

    def _variants(
        self,
        image_path,
    ):

        image_path=Path(image_path)

        stem=image_path.stem

        variants={}

        variants["original"]=str(image_path)

        binary=self.clean_image(
            image_path,
            True,
        )

        gray=self.clean_image(
            image_path,
            False,
        )

        variants["cleaned_binary"]=self._save_variant(

            binary,

            f"{stem}_binary.png",

        )

        variants["cleaned_gray"]=self._save_variant(

            gray,

            f"{stem}_gray.png",

        )

        return variants
    
    # ---------------------------------------------------------

    def _predict_decimer(
        self,
        image_path,
        hand_drawn=False,
    ):

        from DECIMER import predict_SMILES

        kwargs_list=[
            {
                "confidence":True,
                "hand_drawn":hand_drawn,
            },
            {
                "confidence":True,
            },
            {
                "hand_drawn":hand_drawn,
            },
            {}
        ]

        for kwargs in kwargs_list:

            try:

                result=predict_SMILES(
                    str(image_path),
                    **kwargs,
                )

                if isinstance(result,tuple):

                    try:
                        confidence=float(
                            np.mean(
                                [
                                    c[1]
                                    for c in result[1]
                                ]
                            )
                        )
                    except Exception:
                        confidence=None

                    return result[0],confidence

                return result,None

            except TypeError:
                continue

            except Exception:
                continue

        return None,None

    # ---------------------------------------------------------

    def _predict_molscribe(
        self,
        image_path,
    ):

        if not self.use_molscribe:
            return None,None

        try:

            if self._molscribe is None:

                import torch
                import huggingface_hub
                from molscribe import MolScribe

                checkpoint=huggingface_hub.hf_hub_download(
                    "yujieq/MolScribe",
                    "swin_base_char_aux_1m.pth",
                )

                self._molscribe=MolScribe(
                    checkpoint,
                    device=torch.device("cpu"),
                )

            result=self._molscribe.predict_image_file(
                str(image_path)
            )

            return (
                result.get("smiles"),
                result.get("confidence"),
            )

        except Exception:

            return None,None

    # ---------------------------------------------------------

    def _sanitize(
        self,
        smiles,
    ):

        if not smiles:
            return None,{}

        mol=Chem.MolFromSmiles(smiles)

        if mol is None:
            return None,{}

        fragments=Chem.GetMolFrags(
            mol,
            asMols=True,
        )

        had_fragments=len(fragments)>1

        mol=self.fragment_chooser.choose(mol)

        elements={
            atom.GetSymbol()
            for atom in mol.GetAtoms()
        }

        smiles=Chem.MolToSmiles(
            mol,
            canonical=True,
        )

        return smiles,{
            "improbable":sorted(
                elements &
                self.IMPROBABLE
            ),
            "halogens":sorted(
                elements &
                self.HALOGENS
            ),
            "had_fragments":had_fragments,
        }

    # ---------------------------------------------------------

    def _pubchem_verify(
        self,
        smiles,
    ):

        if not self.use_pubchem:
            return None

        if smiles is None:
            return None

        if smiles in self.pubchem_cache:
            return self.pubchem_cache[smiles]

        try:

            import time
            import pubchempy as pcp
            from rdkit.Chem import inchi

            mol=Chem.MolFromSmiles(smiles)

            if mol is None:
                return None

            inchi_key=inchi.InchiToInchiKey(
                inchi.MolToInchi(mol)
            )

            answer=None

            for _ in range(3):

                try:

                    compounds=pcp.get_compounds(
                        inchi_key,
                        "inchikey",
                    )

                    answer=len(compounds)>0

                    break

                except Exception:

                    time.sleep(1)

            self.pubchem_cache[smiles]=answer

            return answer

        except Exception:

            return None

    # ---------------------------------------------------------

    def _run_models(
        self,
        image_path,
    ):

        predictions=[]

        for hand_drawn in (
            [False,True]
            if self.try_hand_drawn
            else [False]
        ):

            smiles,confidence=self._predict_decimer(
                image_path,
                hand_drawn,
            )

            smiles,info=self._sanitize(smiles)

            if (
                smiles and
                not info.get("improbable")
            ):

                predictions.append({

                    "model":"DECIMER",

                    "smiles":smiles,

                    "confidence":
                        confidence or 0.0,

                    "halogens":
                        bool(info["halogens"]),

                    "had_fragments":
                        bool(info["had_fragments"]),

                })

        smiles,confidence=self._predict_molscribe(
            image_path
        )

        smiles,info=self._sanitize(smiles)

        if (
            smiles and
            not info.get("improbable")
        ):

            predictions.append({

                "model":"MolScribe",

                "smiles":smiles,

                "confidence":
                    confidence or 0.0,

                "halogens":
                    bool(info["halogens"]),

                "had_fragments":
                    bool(info["had_fragments"]),

            })

        return predictions
    
    # ---------------------------------------------------------

    def predict(
        self,
        image_path,
    ):
        """
        Predict SMILES for a single image.

        Parameters
        ----------
        image_path : str | Path

        Returns
        -------
        dict
        """

        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(image_path)

        variants = self._variants(image_path)

        reads = []

        for variant_name, variant_path in variants.items():

            predictions = self._run_models(variant_path)

            for prediction in predictions:

                prediction["variant"] = variant_name

                reads.append(prediction)

        if not reads:

            return {
                "smiles": None,
                "trust": False,
                "votes": 0,
                "total": 0,
                "agreement": 0.0,
                "confidence": None,
                "pubchem": None,
                "needs_review": True,
                "predictions": [],
            }

        votes = Counter(
            prediction["smiles"]
            for prediction in reads
        )

        best_smiles, best_votes = votes.most_common(1)[0]

        total = len(reads)

        agreement = best_votes / total

        confidence = max(
            prediction["confidence"]
            for prediction in reads
            if prediction["smiles"] == best_smiles
        )

        halogens = any(
            prediction["halogens"]
            for prediction in reads
            if prediction["smiles"] == best_smiles
        )

        pubchem = self._pubchem_verify(
            best_smiles
        )

        trust = (
            (
                best_votes >= 2 and
                agreement >= 0.5
            )
            or
            (
                confidence >= 0.90 and
                len(votes) == 1
            )
        )

        if pubchem is False and best_votes < 2:
            trust = False

        needs_review = (
            (not trust)
            or
            halogens
        )

        return {

            "smiles": best_smiles,

            "trust": bool(trust),

            "votes": best_votes,

            "total": total,

            "agreement": round(
                agreement,
                3,
            ),

            "confidence": (
                round(confidence, 3)
                if confidence is not None
                else None
            ),

            "pubchem": pubchem,

            "needs_review": bool(
                needs_review
            ),

            "predictions": reads,

        }

    # ---------------------------------------------------------

    def predict_folder(
        self,
        folder,
    ):

        folder = Path(folder)

        extensions = {
            ".png",
            ".jpg",
            ".jpeg",
            ".bmp",
            ".tif",
            ".tiff",
        }

        results = []

        for image in sorted(folder.iterdir()):

            if (
                not image.is_file()
                or
                image.suffix.lower() not in extensions
            ):
                continue

            try:

                result = self.predict(image)

                result["image"] = image.name

                results.append(result)

            except Exception as exc:

                results.append({

                    "image": image.name,

                    "smiles": None,

                    "error": str(exc),

                })

        return results

    # ---------------------------------------------------------

    def benchmark(
        self,
        folder,
        ground_truth,
    ):

        results = self.predict_folder(folder)

        total = 0

        correct = 0

        for result in results:

            if result.get("smiles") is None:
                continue

            stem = Path(
                result["image"]
            ).stem

            if stem not in ground_truth:
                continue

            pred = Chem.MolToSmiles(
                Chem.MolFromSmiles(
                    result["smiles"]
                )
            )

            gt = Chem.MolToSmiles(
                Chem.MolFromSmiles(
                    ground_truth[stem]
                )
            )

            total += 1

            if pred == gt:
                correct += 1

        accuracy = (
            correct / total
            if total
            else 0.0
        )

        return {

            "accuracy": accuracy,

            "correct": correct,

            "total": total,

        }

    # ---------------------------------------------------------

    def __call__(
        self,
        image_path,
    ):

        return self.predict(image_path)