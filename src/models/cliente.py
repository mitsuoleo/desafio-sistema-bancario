class Cliente:
    """Representa um correntista do banco.

    Centraliza a regra de limite diário de transações para que
    nenhuma subclasse precise reimplementá-la.
    """

    LIMITE_TRANSACOES_DIARIAS = 10

    def __init__(self, endereco):
        self._endereco = endereco
        self._contas = []

    @property
    def contas(self):
        return self._contas

    @property
    def endereco(self):
        return self._endereco

    def realizar_transacao(self, conta, transacao):
        if len(conta.historico.transacoes_do_dia) >= self.LIMITE_TRANSACOES_DIARIAS:
            print("\nLimite diário de transações atingido. Tente novamente amanhã.")
            return
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self._contas.append(conta)


class PessoaFisica(Cliente):
    """Cliente do tipo pessoa física, identificado por CPF."""

    def __init__(self, nome, cpf, data_nascimento, endereco):
        super().__init__(endereco)
        self._nome = nome
        self._cpf = cpf
        self._data_nascimento = data_nascimento

    @property
    def nome(self):
        return self._nome

    @property
    def cpf(self):
        return self._cpf

    @property
    def data_nascimento(self):
        return self._data_nascimento
