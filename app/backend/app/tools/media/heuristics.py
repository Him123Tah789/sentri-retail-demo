from typing import Dict, Any, List
import numpy as np
import cv2
from PIL import Image

def _to_bgr_np(img: Image.Image) -> np.ndarray:
    rgb = np.array(img.convert("RGB"))
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

def detect_over_smoothing(bgr: np.ndarray) -> float:
    # Low edge energy can indicate heavy smoothing (common in AI portraits)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    # Resize for speed
    gray = cv2.resize(gray, (512, 512), interpolation=cv2.INTER_AREA)
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    score = float(lap.var())  # higher = more detail, lower = smoother
    return score

def detect_repeated_texture(bgr: np.ndarray) -> float:
    # Simple periodicity hint via FFT magnitude peaks (very rough but explainable)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    # Resize for speed
    gray = cv2.resize(gray, (512, 512), interpolation=cv2.INTER_AREA)
    f = np.fft.fft2(gray)
    fshift = np.fft.fftshift(f)
    mag = np.log(np.abs(fshift) + 1.0)
    # measure "spikiness" (more spikes can hint repeated patterns)
    return float(np.percentile(mag, 99) - np.percentile(mag, 50))

def detect_jpeg_compression_artifacts(img: Image.Image) -> float:
    # Rough measure: if PNG with no EXIF but looks like screenshot, not suspicious by itself.
    # Here we detect blockiness-like artifact strength using DCT energy (lightweight)
    bgr = _to_bgr_np(img)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (256, 256))
    dct = cv2.dct(gray.astype(np.float32) / 255.0)
    # high frequency energy proxy
    hf = np.mean(np.abs(dct[32:, 32:]))
    return float(hf)

def classify_image_type(img: Image.Image) -> str:
    # Very simple classification for demo purposes
    w, h = img.size
    if w > 1200 and h > 1200:
        return "photo_or_high_res"
    if w > 900 and h < 700:
        return "screenshot_or_banner"
    return "general_image"

def run_heuristics(img: Image.Image) -> Dict[str, Any]:
    bgr = _to_bgr_np(img)

    smooth_var = detect_over_smoothing(bgr)     # low => smoother
    repeat_score = detect_repeated_texture(bgr) # higher => more periodicity hints
    jpeg_hf = detect_jpeg_compression_artifacts(img)

    indicators: List[str] = []
    # Thresholds are heuristic — tune for your demo set
    if smooth_var < 50:
        indicators.append("Low edge detail (possible over-smoothing)")
    if repeat_score > 4.0:
        indicators.append("Potential repeated texture patterns")
    # jpeg_hf is not a strong detector; keep it as a weak signal
    if jpeg_hf < 0.01:
        indicators.append("Very low high-frequency DCT energy (could be over-smoothed or heavily compressed)")

    return {
        "type_guess": classify_image_type(img),
        "scores": {
            "edge_detail_variance": round(smooth_var, 3),
            "repeat_texture_score": round(repeat_score, 3),
            "dct_highfreq_energy": round(jpeg_hf, 5),
        },
        "indicators": indicators
    }
