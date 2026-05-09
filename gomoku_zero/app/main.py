from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api import game_api, training_api, data_api
from app.config import CONFIG

app = FastAPI(title="GomokuZero", description="AlphaGo Zero风格五子棋自对弈训练系统")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(game_api.router, prefix="/api/game", tags=["game"])
app.include_router(training_api.router, prefix="/api/training", tags=["training"])
app.include_router(data_api.router, prefix="/api/data", tags=["data"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_dir = os.path.join(BASE_DIR, "static")
dist_dir = os.path.join(BASE_DIR, "dist")

if os.path.exists(dist_dir):
    @app.get("/")
    async def serve_frontend():
        return FileResponse(os.path.join(dist_dir, "index.html"))

    @app.get("/{path:path}")
    async def serve_static(path: str):
        file_path = os.path.join(dist_dir, path)
        if os.path.exists(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(dist_dir, "index.html"))

elif os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    async def root():
        templates_dir = os.path.join(BASE_DIR, "templates")
        html_path = os.path.join(templates_dir, "index.html")
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read()

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
