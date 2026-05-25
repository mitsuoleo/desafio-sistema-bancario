from src.models.transacao import Historico, Saque


class Conta:
    """Conta bancária base com saldo, histórico e operações de crédito/débito."""

    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        """Fábrica que padroniza a criação de contas sem expor o __init__."""
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def restaurar_saldo(self, valor):
        """Define o saldo carregado do banco sem acionar depositar().

        Usado exclusivamente em carregar_dados() para evitar
        acesso direto a _saldo e mensagens indevidas no terminal.
        """
        self._saldo = valor

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\nDepósito realizado com sucesso!")
            return True
        else:
            print("\nValor inválido. O depósito deve ser maior que zero.")
            return False

    def sacar(self, valor):
        if valor > self._saldo:
            print("\nSaldo insuficiente para realizar o saque.")
            return False
        elif valor > 0:
            self._saldo -= valor
            print("\nSaque realizado com sucesso!")
            return True
        else:
            print("\nValor inválido. O saque deve ser maior que zero.")
            return False


class ContaCorrente(Conta):
    """Conta corrente com limite de valor por saque e limite diário de saques.

    Sobrescreve sacar() para aplicar as restrições antes de delegar
    a operação à classe pai.
    """

    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        saques_realizados = len([
            t for t in self.historico.transacoes
            if t["tipo"] == Saque.__name__
        ])

        if valor > self._limite:
            print("\nValor do saque excede o limite permitido.")
        elif saques_realizados >= self._limite_saques:
            print("\nNúmero máximo de saques atingido.")
        else:
            return super().sacar(valor)
        return False
