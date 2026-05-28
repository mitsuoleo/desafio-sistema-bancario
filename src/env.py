from pathlib import Path

from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parents[1]


def carregar_env():
    """Carrega variáveis do arquivo .env na raiz do projeto."""
    load_dotenv(_PROJECT_ROOT / ".env")
