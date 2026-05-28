"""Testes de integração do portal do cliente (API)."""

from src.models.cliente import PessoaFisica
from src.models.conta import ContaCorrente
from src.models.transacao import Deposito


class TestPortalSessao:
    def test_login_retorna_token_e_sessao(self, cliente_conta):
        client, _, pf, _ = cliente_conta
        res = client.get(f"/api/portal/sessao/{pf.cpf}")
        assert res.status_code == 200
        body = res.json()
        assert "token" in body
        assert body["sessao"]["cpf"] == pf.cpf
        assert len(body["sessao"]["contas"]) == 1

    def test_cpf_inexistente_retorna_404(self, api_client):
        client, _ = api_client
        res = client.get("/api/portal/sessao/11144477735")
        assert res.status_code == 404


class TestPortalCadastro:
    def test_cadastro_cria_cliente_e_conta(self, api_client, mock_db):
        client, server = api_client
        mock_db.salvar_conta.return_value = 42

        res = client.post(
            "/api/portal/cadastro",
            json={
                "cpf": "11144477735",
                "nome": "Novo Cliente",
                "data_nascimento": "15/05/1988",
                "endereco": "Av. Brasil, 100",
            },
        )
        assert res.status_code == 201
        body = res.json()
        assert body["sessao"]["cpf"] == "11144477735"
        assert body["token"]
        assert len(server.state.contas) == 1


class TestPortalAutorizacao:
    def test_deposito_sem_token_retorna_erro(self, cliente_conta):
        client, _, pf, conta = cliente_conta
        res = client.post(
            "/api/portal/depositos",
            json={"cpf": pf.cpf, "valor": 10.0, "numero_conta": conta.numero},
        )
        assert res.status_code == 422

    def test_deposito_com_cpf_de_outro_usuario_retorna_403(self, cliente_conta):
        client, server, pf, conta = cliente_conta

        outro = PessoaFisica(
            nome="Outro",
            cpf="11144477735",
            data_nascimento="01/01/1980",
            endereco="Rua B",
        )
        conta2 = ContaCorrente.nova_conta(cliente=outro, numero=2)
        outro.adicionar_conta(conta2)
        server.state.clientes.append(outro)
        server.state.contas.append(conta2)

        login = client.get(f"/api/portal/sessao/{pf.cpf}").json()
        token = login["token"]

        res = client.post(
            "/api/portal/depositos",
            headers={"X-Portal-Token": token},
            json={
                "cpf": outro.cpf,
                "valor": 50.0,
                "numero_conta": conta2.numero,
            },
        )
        assert res.status_code == 403

    def test_deposito_autorizado_atualiza_saldo(self, cliente_conta):
        client, _, pf, conta = cliente_conta
        login = client.get(f"/api/portal/sessao/{pf.cpf}").json()

        res = client.post(
            "/api/portal/depositos",
            headers={"X-Portal-Token": login["token"]},
            json={"cpf": pf.cpf, "valor": 100.0, "numero_conta": conta.numero},
        )
        assert res.status_code == 200
        assert res.json()["sessao"]["contas"][0]["saldo"] == 100.0


class TestPortalExtrato:
    def test_extrato_usa_apenas_conta_do_cpf_logado(self, cliente_conta):
        client, _, pf, conta = cliente_conta
        login = client.get(f"/api/portal/sessao/{pf.cpf}").json()

        pf.realizar_transacao(conta, Deposito(25))

        res = client.get(
            f"/api/portal/extrato?numero_conta={conta.numero}",
            headers={"X-Portal-Token": login["token"]},
        )
        assert res.status_code == 200
        assert res.json()["saldo"] == 25.0
