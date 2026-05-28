# Segurança — Sistema Bancário (protótipo de estudo)

Este documento descreve riscos conhecidos e mitigações aplicadas. **Não use em produção sem revisão profissional.**

## Mitigações implementadas

| Risco | Mitigação |
|-------|-----------|
| API legada expunha todos os clientes sem login | Rotas `/api/clientes`, `/api/contas`, etc. **desabilitadas por padrão** (`ENABLE_LEGACY_API=false`) |
| Qualquer um operava conta informando CPF no body | Portal exige header `X-Portal-Token` (HMAC do CPF + `PORTAL_SECRET`) em depósitos, saques, extrato e nova conta |
| CPF no body diferente da sessão | Servidor compara CPF do token com CPF da requisição (403 se divergir) |
| Enumeração de CPF | Removido endpoint `/api/portal/cpf/{cpf}/existe` |
| SQL injection | Queries parametrizadas (`psycopg2` com `%s`) |
| CORS aberto | Restrito a `CORS_ORIGINS` (padrão: localhost) |
| Timing attack no login admin | `hmac.compare_digest` em usuário, senha e token |

## Limitações aceitas no protótipo

- **Login do cliente** = conhecimento do CPF (sem senha, sem MFA).
- **Token admin** fixo ou configurável por `.env` — não é JWT com expiração.
- **Token portal** não expira; quem obtém o token pode operar até trocar `PORTAL_SECRET`.
- Credenciais padrão `admin` / `banco1234` para fins didáticos.
- Sem HTTPS, rate limiting, auditoria ou criptografia de dados em repouso além do PostgreSQL.
- Valores monetários na API usam `float` na serialização JSON (modelo interno usa `Decimal`).

## Recomendações para produção

1. Senha/PIN ou biometria no portal do cliente.
2. JWT com expiração e refresh token; revogação em logout.
3. `PORTAL_SECRET` e `ADMIN_TOKEN` longos e aleatórios (gerados por secrets manager).
4. HTTPS obrigatório, rate limit e logs de auditoria.
5. Validar CPF com dígitos verificadores.
6. Nunca commitar `.env` (já listado no `.gitignore`).
