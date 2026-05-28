# Sistema Bancário

Sistema bancário desenvolvido em Python como desafio da Trilha Python da Suzano na plataforma [DIO](https://www.dio.me/). Inclui terminal interativo, API REST e protótipo web com **painel do cliente** e **painel administrativo**.

## Funcionalidades

### Terminal (`main.py`)

- Depositar, sacar, extrato
- Cadastro de clientes e contas
- Listagem e exclusão

### Web ([http://localhost:8000](http://localhost:8000))

| Painel | URL | Acesso |
|--------|-----|--------|
| **Cliente** | `/cliente` | CPF → cadastro + conta na 1ª vez; depois só suas contas |
| **Banco** | `/admin` | `admin` / `banco1234` (configurável no `.env`) |

O cliente **não vê** dados de outros CPFs. O banco consulta visão geral e busca por CPF com extratos.

## Regras de negócio

- Limite de **10 transações diárias** por conta
- Limite de **3 saques** por dia
- Limite de **R$ 500,00** por saque

## Pré-requisitos

- Python 3.10+
- PostgreSQL

## Configuração

```bash
cp .env.example .env   # Windows: copy .env.example .env
```

Edite o `.env`:

| Variável | Descrição |
|----------|-----------|
| `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT` | PostgreSQL |
| `PORTAL_SECRET` | Segredo do token de sessão do cliente |
| `ADMIN_USUARIO`, `ADMIN_SENHA`, `ADMIN_TOKEN` | Login do painel do banco |
| `CORS_ORIGINS` | Origens permitidas (vírgula) |
| `ENABLE_LEGACY_API` | `true` só se precisar da API antiga sem auth |

## Como executar

### Terminal

```bash
pip install -r requirements.txt
python main.py
```

### Protótipo web

```bash
pip install -r requirements.txt
python run_web.py
```

Abra [http://localhost:8000](http://localhost:8000). Documentação da API: [http://localhost:8000/docs](http://localhost:8000/docs).

### Docker

```bash
docker build -t sistema-bancario .
docker run -it --env-file .env sistema-bancario
```

## Testes automatizados

```bash
pytest tests/ -v
```

| Arquivo | Cobertura |
|---------|-----------|
| `tests/test_conta.py` | Regras de conta, saque, depósito, limites |
| `tests/test_utils.py` | Formatação de CPF e data |
| `tests/test_auth_tokens.py` | Tokens HMAC do portal |
| `tests/test_api_portal.py` | API do cliente, isolamento por CPF |
| `tests/test_api_admin.py` | Login admin, rotas protegidas |

Os testes de API usam banco **mockado** (não exigem PostgreSQL).

## Arquitetura da API

```
/api/health          — status
/api/portal/*        — cliente (token X-Portal-Token após login)
/api/admin/*         — funcionário (token X-Admin-Token após login)
/api/*               — legado (somente se ENABLE_LEGACY_API=true)
```

## Segurança

Consulte [SECURITY.md](SECURITY.md) para riscos conhecidos, mitigações e limitações do protótipo de estudo.

**Resumo:** a API legada sem autenticação está desligada por padrão; o portal valida token vinculado ao CPF; o admin exige credenciais e token. Ainda assim, **não é um sistema pronto para produção**.

## Estrutura do projeto

```
├── main.py              # CLI
├── run_web.py           # Servidor FastAPI + frontend
├── src/
│   ├── api/             # server, portal, admin, legacy, auth
│   ├── models/          # Cliente, Conta, Transação
│   ├── services/        # Operações terminal
│   └── database.py      # PostgreSQL
├── frontend/            # HTML/CSS/JS (landing, cliente, admin)
└── tests/
```

## Linguagens e ferramentas

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
