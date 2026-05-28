# Sistema Bancário

Sistema bancário desenvolvido em Python como desafio da Trilha Python da Suzano na plataforma [DIO](https://www.dio.me/). Inclui terminal interativo, API REST e protótipo web com **painel do cliente** e **painel administrativo**.

## Funcionalidades

### Terminal (`main.py`)

- Depositar, sacar, extrato
- Cadastro de clientes e contas
- Listagem e exclusão

### Web ([http://localhost:8000](http://localhost:8000))

Interface web totalmente redesenhada com um **Design System Premium em Dark Mode** (Outfit/Inter typography, glassmorphism, textura fosca e animações fluidas).

| Painel | URL | Acesso / Recursos |
|--------|-----|-------------------|
| **Cliente** | `/cliente` | CPF → cadastro estruturado (com seleção de UF do Brasil) + conta na 1ª vez; visualização de contas em formato de **cartões bancários realistas**, saques, depósitos e extrato cronológico. |
| **Banco** | `/admin` | `admin` / `banco1234` (configurável no `.env`); visualização consolidada do saldo, consulta de perfil de clientes, e **nova aba para exclusão administrativa de contas e clientes** protegida por token. |

O cliente **não vê** dados de outros CPFs. O banco consulta a visão geral, busca por CPF com extratos detalhados e gerencia exclusões.

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
/api/health          — Status e integridade
/api/portal/*        — Cliente (autenticado com X-Portal-Token)
/api/admin/*         — Funcionário (autenticado com X-Admin-Token)
  ├── GET /resumo    — Visão consolidada e métricas
  ├── GET /clientes  — Consulta de perfil cadastral por CPF
  ├── DELETE /clientes/{cpf}  — Exclusão de perfil e contas [NOVO]
  └── DELETE /contas/{numero} — Exclusão de conta corrente [NOVO]
/api/*               — Legado (sem autenticação, desabilitado por padrão)
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
