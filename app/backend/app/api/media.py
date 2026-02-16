import os, uuid, json, time
from fastapi import APIRouter, UploadFile, File
from starlette.concurrency import run_in_threadpool
from app.tools.media.image_scan import scan_image
from app.llm.llm_router import llm_explain

router = APIRouter()

MAX_BYTES = 8 * 1024 * 1024  # 8MB hackathon cap
CHUNK_SIZE = 1024 * 1024     # 1MB chunks

@router.post("/scan/image")
async def scan_image_api(file: UploadFile = File(...), use_llm: bool = False):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        return {"ok": False, "error": "Unsupported image type. Use jpg/png/webp."}

    os.makedirs("/tmp", exist_ok=True)
    tmp = f"/tmp/{uuid.uuid4().hex}{ext}"

    t0 = time.time()

    try:
        # ✅ Stream upload to disk (prevents huge in-memory reads)
        size = 0
        with open(tmp, "wb") as f:
            while True:
                chunk = await file.read(CHUNK_SIZE)
                if not chunk:
                    break
                size += len(chunk)
                if size > MAX_BYTES:
                    # Clean up partial file
                    f.close()
                    if os.path.exists(tmp):
                        os.remove(tmp)
                    return {"ok": False, "error": f"File too large. Max {MAX_BYTES//1024//1024}MB."}
                f.write(chunk)

        t_upload = time.time()

        # ✅ Run heavy CPU scan off the event loop
        tool_result = await run_in_threadpool(scan_image, tmp)

        t_scan = time.time()

        # ✅ LLM explanation should NEVER block returning tool_result
        explanation = None
        if use_llm:
            try:
                # run LLM in threadpool too (prevents blocking if llm_explain is slow)
                # Note: llm_explain is synchronous, so we run it in threadpool
                explanation = await run_in_threadpool(
                    llm_explain,
                    user_message="Explain the heuristic image authenticity result clearly and give next steps.",
                    system_extra=(
                        "You are Sentri. Explain the heuristic image authenticity scan in simple terms. "
                        "Do not claim 100% certainty. Provide verification steps."
                    ),
                    context_json=json.dumps(tool_result, ensure_ascii=False),
                )
            except Exception as e:
                print(f"LLM Explanation failed: {e}")
                explanation = "Explanation unavailable. Showing forensic results only."

        t_llm = time.time()

        return {
            "ok": True,
            "tool_result": tool_result,
            "assistant_explanation": explanation,
            "timing_ms": {
                "upload": int((t_upload - t0) * 1000),
                "scan": int((t_scan - t_upload) * 1000),
                "llm": int((t_llm - t_scan) * 1000) if use_llm else 0,
                "total": int((t_llm - t0) * 1000) if use_llm else int((t_scan - t0) * 1000),
            },
            "file_bytes": size,
        }

    except Exception as e:
        return {"ok": False, "error": str(e)}

    finally:
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except:
            pass
