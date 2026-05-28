"""Testes do painel administrativo."""

from src.models.transacao import Deposito


class TestAdminLogin:
    def test_login_correto_retorna_token(self, api_client):
        client, _ = api_client
        res = client.post(
            "/api/admin/login",
            json={"usuario": "admin", "senha": "banco1234"},
        )
        assert res.status_code == 200
        assert res.json()["token"] == "test-admin-token"

    def test_login_incorreto_retorna_401(self, api_client):
        client, _ = api_client
        res = client.post(
            "/api/admin/login",
            json={"usuario": "admin", "senha": "errada"},
        )
        assert res.status_code == 401


class TestAdminProtegido:
    def test_resumo_sem_token_retorna_erro(self, api_client):
        client, _ = api_client
        res = client.get("/api/admin/resumo")
        assert res.status_code == 422

    def test_resumo_com_token_lista_contas(self, cliente_conta):
        client, _, pf, conta = cliente_conta
        token = client.post(
            "/api/admin/login",
            json={"usuario": "admin", "senha": "banco1234"},
        ).json()["token"]

        conta.depositar(200)

        res = client.get(
            "/api/admin/resumo",
            headers={"X-Admin-Token": token},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["total_clientes"] == 1
        assert body["total_contas"] == 1
        assert body["saldo_total"] == 200.0

    def test_busca_por_cpf_retorna_extrato(self, cliente_conta):
        client, _, pf, conta = cliente_conta
        token = client.post(
            "/api/admin/login",
            json={"usuario": "admin", "senha": "banco1234"},
        ).json()["token"]

        pf.realizar_transacao(conta, Deposito(75))

        res = client.get(
            f"/api/admin/clientes/{pf.cpf}",
            headers={"X-Admin-Token": token},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["nome"] == pf.nome
        assert len(body["contas"]) == 1
        assert len(body["contas"][0]["transacoes"]) == 1


class TestLegacyApiDesabilitada:
    def test_listar_clientes_legado_retorna_404(self, api_client):
        client, _ = api_client
        res = client.get("/api/clientes")
        assert res.status_code == 404
