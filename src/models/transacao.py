from abc import ABC, abstractmethod
from datetime import datetime


class Transacao(ABC):
    """Interface base para todas as transações bancárias.

    Garante que Deposito e Saque implementem registrar() e valor
    antes de serem aceitos em Cliente.realizar_transacao()
    """

    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass


class Deposito(Transacao):
    """Transação de crédito em conta."""

    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Saque(Transacao):
    """Transação de débito em conta."""

    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Historico:
    """Armazena e consulta o extrato de transações de uma conta."""

    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    @property
    def transacoes_do_dia(self):
        """Retorna apenas as transações realizadas na data atual.

        Usado para verificar o limite diário antes de autorizar
        uma nova operação.
        """
        hoje = datetime.now().date()
        return [
            t for t in self._transacoes
            if datetime.strptime(t["data"], "%d/%m/%Y %H:%M:%S").date() == hoje
        ]

    def adicionar_transacao(self, transacao):
        self._transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        })

    def restaurar_transacao(self, tipo, valor, data):
        """Reinsere uma transação carregada do banco sem passar por registrar().

        Usado exclusivamente em carregar_dados() para reconstituir
        o histórico de sessões anteriores.
        """
        self._transacoes.append({
            "tipo": tipo,
            "valor": valor,
            "data": data
        })
