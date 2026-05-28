import os
from contextlib import asynccontextmanager
from pathlib import Path

from src.env import carregar_env

carregar_env()

ENABLE_LEGACY_API = os.getenv("ENABLE_LEGACY_API", "false").lower() in ("1", "true", "yes")
CORS_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:8000,http://127.0.0.1:8000",
    ).split(",")
    if o.strip()
]

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.api.admin_routes import router as admin_router
from src.api.legacy import router as legacy_router
from src.api.portal import router as portal_router
from src.bootstrap import carregar_dados
from src.database import Database

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"


class AppState:
    def __init__(self):
        self.db: Database | None = None
        self.clientes: list = []
        self.contas: list = []


state = AppState()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    state.db = Database()
    state.clientes, state.contas = carregar_dados(state.db)
    yield
    if state.db:
        state.db.fechar()


app = FastAPI(
    title="Sistema Bancário",
    description="API REST para o protótipo web do sistema bancário",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-Admin-Token", "X-Portal-Token"],
)

app.include_router(portal_router)
app.include_router(admin_router)

if ENABLE_LEGACY_API:
    app.include_router(legacy_router)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "clientes": len(state.clientes),
        "contas": len(state.contas),
    }


@app.get("/")
def index():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/cliente")
def pagina_cliente():
    return FileResponse(FRONTEND_DIR / "cliente.html")


@app.get("/admin")
def pagina_admin():
    return FileResponse(FRONTEND_DIR / "admin.html")


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
