import hashlib
import hmac
import os
ADMIN_USUARIO = os.getenv("ADMIN_USUARIO", "admin")
ADMIN_SENHA = os.getenv("ADMIN_SENHA", "banco1234")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "admin-session-proto")

PORTAL_SECRET = os.getenv("PORTAL_SECRET", "dev-portal-secret-altere-em-producao")


def criar_token_portal(cpf: str) -> str:
    """Token vinculado ao CPF (HMAC). Não substitui autenticação forte em produção."""
    cpf_digitos = "".join(filter(str.isdigit, cpf))
    assinatura = hmac.new(
        PORTAL_SECRET.encode(),
        cpf_digitos.encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"{cpf_digitos}.{assinatura}"


def validar_token_portal(token: str) -> str | None:
    if not token or "." not in token:
        return None
    cpf, assinatura = token.rsplit(".", 1)
    if len(cpf) != 11 or not cpf.isdigit():
        return None
    esperada = hmac.new(
        PORTAL_SECRET.encode(),
        cpf.encode(),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(assinatura, esperada):
        return None
    return cpf


def validar_cpf_autorizado(token: str, cpf_informado: str) -> str:
    """Garante que o CPF do corpo/query pertence à sessão do token."""
    cpf_sessao = validar_token_portal(token)
    cpf_body = "".join(filter(str.isdigit, cpf_informado))
    if not cpf_sessao or cpf_sessao != cpf_body:
        raise ValueError("cpf_nao_autorizado")
    return cpf_sessao


