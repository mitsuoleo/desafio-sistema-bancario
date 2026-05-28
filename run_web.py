"""Inicia o servidor web do protótipo (API + frontend)."""

import sys

from src.env import carregar_env

carregar_env()


def _verificar_dependencia(nome_import: str, nome_pacote: str) -> None:
    try:
        __import__(nome_import)
    except ModuleNotFoundError:
        print(
            f"Pacote '{nome_pacote}' não encontrado neste interpretador:\n"
            f"  {sys.executable}\n\n"
            "Instale as dependências com o MESMO comando 'python' que você usa para rodar o projeto:\n"
            f'  "{sys.executable}" -m pip install -r requirements.txt',
            file=sys.stderr,
        )
        sys.exit(1)


def main():
    _verificar_dependencia("uvicorn", "uvicorn[standard]")
    _verificar_dependencia("fastapi", "fastapi")
    _verificar_dependencia("psycopg2", "psycopg2-binary")

    import uvicorn

    uvicorn.run("src.api.server:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
