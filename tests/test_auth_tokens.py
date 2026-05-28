import pytest

from src.api.auth import (
    ADMIN_SENHA,
    ADMIN_USUARIO,
    criar_token_portal,
    validar_cpf_autorizado,
    validar_token_portal,
)


class TestPortalToken:
    def test_token_valido_para_cpf(self, monkeypatch):
        monkeypatch.setenv("PORTAL_SECRET", "segredo-teste")
        token = criar_token_portal("529.982.247-25")
        assert validar_token_portal(token) == "52998224725"

    def test_token_invalido_rejeitado(self, monkeypatch):
        monkeypatch.setenv("PORTAL_SECRET", "segredo-teste")
        assert validar_token_portal("52998224725.assinatura-falsa") is None

    def test_cpf_do_corpo_deve_coincidir_com_token(self, monkeypatch):
        monkeypatch.setenv("PORTAL_SECRET", "segredo-teste")
        token = criar_token_portal("52998224725")
        assert validar_cpf_autorizado(token, "52998224725") == "52998224725"

    def test_cpf_diferente_do_token_levanta_erro(self, monkeypatch):
        monkeypatch.setenv("PORTAL_SECRET", "segredo-teste")
        token = criar_token_portal("52998224725")
        with pytest.raises(ValueError, match="cpf_nao_autorizado"):
            validar_cpf_autorizado(token, "11144477735")


class TestAdminCredenciaisPadrao:
    def test_credenciais_padrao_estudo(self):
        assert ADMIN_USUARIO == "admin"
        assert ADMIN_SENHA == "banco1234"
