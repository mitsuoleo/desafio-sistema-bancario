"""Testes unitários para os modelos de conta e cliente.

Execute com:  pytest tests/ -v
"""

import pytest
from src.models.cliente import PessoaFisica
from src.models.conta import ContaCorrente
from src.models.transacao import Deposito, Saque


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def cliente():
    return PessoaFisica(
        nome="João Silva",
        cpf="12345678901",
        data_nascimento="01/01/1990",
        endereco="Rua A, 1 - Centro - SP/SP",
    )


@pytest.fixture
def conta(cliente):
    c = ContaCorrente.nova_conta(cliente=cliente, numero=1)
    cliente.adicionar_conta(c)
    return c


# ---------------------------------------------------------------------------
# Depósito
# ---------------------------------------------------------------------------

class TestDeposito:
    def test_deposito_valido_aumenta_saldo(self, conta):
        conta.depositar(200)
        assert conta.saldo == 200

    def test_deposito_zero_nao_altera_saldo(self, conta):
        resultado = conta.depositar(0)
        assert resultado is False
        assert conta.saldo == 0

    def test_deposito_negativo_nao_altera_saldo(self, conta):
        resultado = conta.depositar(-50)
        assert resultado is False
        assert conta.saldo == 0

    def test_deposito_registrado_no_historico(self, conta, cliente):
        cliente.realizar_transacao(conta, Deposito(100))
        assert len(conta.historico.transacoes) == 1
        assert conta.historico.transacoes[0]["tipo"] == "Deposito"


# ---------------------------------------------------------------------------
# Saque
# ---------------------------------------------------------------------------

class TestSaque:
    def test_saque_valido_reduz_saldo(self, conta):
        conta.depositar(300)
        conta.sacar(100)
        assert conta.saldo == 200

    def test_saque_acima_do_saldo_recusado(self, conta):
        conta.depositar(100)
        resultado = conta.sacar(200)
        assert resultado is False
        assert conta.saldo == 100

    def test_saque_acima_do_limite_por_operacao_recusado(self, conta):
        conta.depositar(1000)
        # limite padrão de ContaCorrente é R$ 500
        resultado = conta.sacar(600)
        assert resultado is False
        assert conta.saldo == 1000

    def test_limite_diario_de_saques(self, conta, cliente):
        conta.depositar(2000)
        # 3 saques devem passar, o 4º deve ser bloqueado
        for _ in range(3):
            cliente.realizar_transacao(conta, Saque(100))
        saldo_antes = conta.saldo
        cliente.realizar_transacao(conta, Saque(100))
        assert conta.saldo == saldo_antes  # 4º saque não executou


# ---------------------------------------------------------------------------
# Limite diário de transações
# ---------------------------------------------------------------------------

class TestLimiteDiarioTransacoes:
    def test_limite_de_10_transacoes_diarias(self, conta, cliente):
        conta.depositar(5000)
        for _ in range(10):
            cliente.realizar_transacao(conta, Deposito(10))
        saldo_antes = conta.saldo
        # 11ª transação deve ser bloqueada
        sucesso = cliente.realizar_transacao(conta, Deposito(10))
        assert sucesso is False
        assert conta.saldo == saldo_antes


# ---------------------------------------------------------------------------
# realizar_transacao retorna bool correto
# ---------------------------------------------------------------------------

class TestRealizarTransacaoRetorno:
    def test_retorna_true_em_operacao_bem_sucedida(self, conta, cliente):
        conta.depositar(500)
        sucesso = cliente.realizar_transacao(conta, Saque(100))
        assert sucesso is True

    def test_retorna_false_quando_limite_diario_atingido(self, conta, cliente):
        conta.depositar(5000)
        for _ in range(10):
            cliente.realizar_transacao(conta, Deposito(1))
        sucesso = cliente.realizar_transacao(conta, Deposito(1))
        assert sucesso is False

    def test_retorna_false_quando_operacao_recusada(self, conta, cliente):
        sucesso = cliente.realizar_transacao(conta, Saque(100))
        assert sucesso is False
        assert conta.saldo == 0
