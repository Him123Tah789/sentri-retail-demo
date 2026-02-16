from typing import Dict, Any
from PIL import Image
from app.tools.media.exif_check import extract_exif
from app.tools.media.heuristics import run_heuristics

def score_ai_likelihood(exif_result: Dict[str, Any], heur: Dict[str, Any]) -> Dict[str, Any]:
    score = 0
    reasons = []

    # EXIF signal (weak-to-medium depending on type)
    if not exif_result["present"]:
        score += 2
        reasons.append("No EXIF metadata (common in AI images, screenshots, or re-saved files)")

    # Heuristic signals
    ind = heur.get("indicators", [])
    score += min(5, len(ind) * 2)  # each indicator adds weight
    reasons.extend(ind)

    # Map to levels (tune as you like)
    if score <= 2:
        level = "LOW"
    elif score <= 6:
        level = "MEDIUM"
    else:
        level = "HIGH"

    actions = [
        "Ask for the original source file (not a screenshot)",
        "Request a live capture (new photo) if identity/verification matters",
        "Verify via additional evidence (reverse image search, vendor confirmation, document checks)"
    ]

    return {
        "ai_likelihood_level": level,
        "ai_likelihood_score": score,  # 0-? heuristic score
        "reasons": reasons,
        "recommended_actions": actions
    }

def scan_image(file_path: str) -> Dict[str, Any]:
    import time
    
    # ✅ Ensure file closes properly
    with Image.open(file_path) as img:
        img.load()  # ✅ force decode now (catch decode errors early)

        # ✅ Cap resolution for speed (keeps aspect ratio)
        img.thumbnail((1600, 1600))

        t0 = time.time()
        exif_result = extract_exif(img)
        print("EXIF:", time.time() - t0)

        t1 = time.time()
        heur = run_heuristics(img)
        print("HEUR:", time.time() - t1)

        likelihood = score_ai_likelihood(exif_result, heur)

        return {
            "exif": exif_result,
            "heuristics": heur,
            "assessment": likelihood,
            "disclaimer": "Heuristic authenticity check, not definitive proof of real/fake."
        }
