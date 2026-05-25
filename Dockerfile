# Variáveis de ambiente necessárias para execução:
# DB_HOST     - endpoint do banco de dados PostgreSQL
# DB_NAME     - nome do banco de dados
# DB_USER     - usuário do banco de dados
# DB_PASSWORD - senha do banco de dados (obrigatória)
# DB_PORT     - porta do banco (padrão: 5432)
#
# Exemplo de uso:
#   docker run -it --env-file .env sistema-bancario

FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser /app

USER appuser

CMD ["python", "desafio.py"]