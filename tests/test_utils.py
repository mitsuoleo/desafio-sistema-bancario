"""Testes unitários para funções utilitárias.

Execute com:  pytest tests/ -v
"""

import pytest
from src.utils import formatar_cpf, formatar_data, filtrar_cliente
from src.models.cliente import PessoaFisica


# ---------------------------------------------------------------------------
# formatar_cpf
# ---------------------------------------------------------------------------

class TestFormatarCpf:
    def test_cpf_somente_digitos(self):
        assert formatar_cpf("12345678901") == "123.456.789-01"

    def test_cpf_ja_formatado(self):
        assert formatar_cpf("123.456.789-01") == "123.456.789-01"

    def test_cpf_incompleto_retorna_sem_formatacao(self):
        assert formatar_cpf("1234") == "1234"


# ---------------------------------------------------------------------------
# formatar_data
# ---------------------------------------------------------------------------

class TestFormatarData:
    def test_data_somente_digitos(self):
        assert formatar_data("01011990") == "01/01/1990"

    def test_data_com_barras(self):
        assert formatar_data("01/01/1990") == "01/01/1990"

    def test_data_com_hifens(self):
        assert formatar_data("01-01-1990") == "01/01/1990"

    def test_data_invalida_retorna_original(self):
        assert formatar_data("invalido") == "invalido"


# ---------------------------------------------------------------------------
# filtrar_cliente
# ---------------------------------------------------------------------------

class TestFiltrarCliente:
    @pytest.fixture
    def clientes(self):
        return [
            PessoaFisica("Ana", "11122233344", "01/01/1985", "Rua X"),
            PessoaFisica("Bruno", "55566677788", "02/02/1990", "Rua Y"),
        ]

    def test_encontra_cliente_por_cpf_sem_formatacao(self, clientes):
        resultado = filtrar_cliente("11122233344", clientes)
        assert resultado is not None
        assert resultado.nome == "Ana"

    def test_encontra_cliente_por_cpf_com_formatacao(self, clientes):
        resultado = filtrar_cliente("111.222.333-44", clientes)
        assert resultado is not None
        assert resultado.nome == "Ana"

    def test_retorna_none_quando_nao_encontrado(self, clientes):
        resultado = filtrar_cliente("00000000000", clientes)
        assert resultado is None
