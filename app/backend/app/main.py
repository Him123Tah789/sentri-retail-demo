from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.assistant import router as assistant_router
from app.api.media import router as media_router

app = FastAPI(title="Sentri Hackathon")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # hackathon
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(assistant_router, tags=["assistant"])
app.include_router(media_router, tags=["media"])