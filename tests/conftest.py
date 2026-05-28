"""Fixtures compartilhadas para testes da API (sem PostgreSQL real)."""

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from src.models.cliente import PessoaFisica
from src.models.conta import ContaCorrente


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.listar_clientes.return_value = []
    db.listar_contas.return_value = []
    db.salvar_cliente.return_value = None
    db.salvar_conta.return_value = 1
    db.salvar_operacao.return_value = None
    db.excluir_cliente.return_value = None
    db.excluir_conta.return_value = None
    db.fechar.return_value = None
    return db


@pytest.fixture
def api_client(mock_db, monkeypatch):
    monkeypatch.setenv("PORTAL_SECRET", "test-portal-secret")
    monkeypatch.setenv("ADMIN_TOKEN", "test-admin-token")
    monkeypatch.setenv("ADMIN_USUARIO", "admin")
    monkeypatch.setenv("ADMIN_SENHA", "banco1234")
    monkeypatch.setenv("ENABLE_LEGACY_API", "false")
    monkeypatch.setattr("src.api.auth.PORTAL_SECRET", "test-portal-secret")
    monkeypatch.setattr("src.api.auth.ADMIN_TOKEN", "test-admin-token")
    monkeypatch.setattr("src.api.auth.ADMIN_USUARIO", "admin")
    monkeypatch.setattr("src.api.auth.ADMIN_SENHA", "banco1234")

    monkeypatch.setattr("src.api.server.Database", lambda: mock_db)

    from src.api import server

    server.state.clientes = []
    server.state.contas = []
    server.state.db = mock_db

    with TestClient(server.app) as client:
        yield client, server


@pytest.fixture
def cliente_conta(api_client):
    client, server = api_client
    pf = PessoaFisica(
        nome="Maria Teste",
        cpf="52998224725",
        data_nascimento="01/01/1990",
        endereco="Rua Teste, 1",
    )
    conta = ContaCorrente.nova_conta(cliente=pf, numero=1)
    pf.adicionar_conta(conta)
    server.state.clientes.append(pf)
    server.state.contas.append(conta)
    return client, server, pf, conta
