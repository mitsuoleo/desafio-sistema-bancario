import textwrap
from abc import ABC, abstractmethod
from datetime import datetime
from database import Database


class Transacao(ABC):
    """Interface base para todas as transações bancárias

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
    """Transação de crédito em conta"""

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
    """Transação de débito em conta"""

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
    """Armazena e consulta o extrato de transações de uma conta"""

    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    @property
    def transacoes_do_dia(self):
        """Retorna apenas as transações realizadas na data atual

        Usado para verificar o limite diário antes de autorizar
        uma nova operação
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


class Cliente:
    """Representa um correntista do banco

    Centraliza a regra de limite diário de transações para que
    nenhuma subclasse precise reimplementá-la
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
    """Cliente do tipo pessoa física, identificado por CPF"""

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


class Conta:
    """Conta bancária base com saldo, histórico e operações de crédito/débito"""

    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        """Fábrica que padroniza a criação de contas sem expor o __init__"""
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

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\nDepósito realizado com sucesso!")
            return True
        else:
            print("\nValor inválido. O depósito deve ser maior que zero")
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
    """Conta corrente com limite de valor por saque e limite diário de saques

    Sobrescreve sacar() para aplicar as restrições antes de delegar
    a operação à classe pai
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


# ---------------------------------------------------------------------------
# Helpers de formatação
# ---------------------------------------------------------------------------

def formatar_cpf(cpf):
    """Converte qualquer entrada de CPF para o formato xxx.xxx.xxx-xx

    Aceita CPF com ou sem pontuação. Retorna sem formatação se
    a quantidade de dígitos for diferente de 11
    """
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) != 11:
        return cpf
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def formatar_data(data_nascimento):
    """Normaliza datas de nascimento para o formato dd/mm/aaaa

    Aceita sequências de 8 dígitos e os formatos dd/mm/YYYY e dd-mm-YYYY.
    Retorna a string original quando nenhum formato é reconhecido
    """
    digits = ''.join(filter(str.isdigit, data_nascimento))
    if len(digits) == 8:
        return f"{digits[:2]}/{digits[2:4]}/{digits[4:]}"
    for fmt in ("%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(data_nascimento, fmt).strftime("%d/%m/%Y")
        except ValueError:
            continue
    return data_nascimento


# ---------------------------------------------------------------------------
# Consultas e seleção de conta
# ---------------------------------------------------------------------------

def filtrar_cliente(cpf, clientes):
    """Busca um cliente pelo CPF, ignorando pontuação na comparação"""
    cpf_digitado = ''.join(filter(str.isdigit, cpf))
    clientes_filtrados = [
        cliente for cliente in clientes
        if ''.join(filter(str.isdigit, cliente.cpf)) == cpf_digitado
    ]
    return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente):
    """Retorna a conta do cliente

    Se o cliente tiver mais de uma conta, exibe a lista e pede
    que o usuário escolha pelo número. Retorna None se não houver
    contas ou se a escolha for inválida
    """
    if not cliente.contas:
        print("\nCliente não possui contas cadastradas")
        return None

    if len(cliente.contas) == 1:
        return cliente.contas[0]

    print("\nContas do cliente:")
    for conta in cliente.contas:
        print(f"  Nº {conta.numero} | Saldo: R$ {conta.saldo:.2f}")
    try:
        numero = int(input("\nInforme o número da conta: "))
    except ValueError:
        print("\nNúmero inválido.")
        return None

    conta_escolhida = next((c for c in cliente.contas if c.numero == numero), None)
    if not conta_escolhida:
        print("\n=== Conta não encontrada para este cliente! ===")
        return None

    return conta_escolhida


# ---------------------------------------------------------------------------
# Operações de transação
# ---------------------------------------------------------------------------

def depositar(clientes, db):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n=== Cliente não encontrado! ===")
        return

    try:
        valor = float(input("Informe o valor do depósito: "))
    except ValueError:
        print("\nValor inválido.")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    transacao = Deposito(valor)
    cliente.realizar_transacao(conta, transacao)

    ultima = conta.historico.transacoes[-1] if conta.historico.transacoes else None
    if ultima and ultima["tipo"] == "Deposito":
        db.atualizar_saldo(conta.numero, conta.saldo)
        db.salvar_transacao(conta.numero, "Depósito", valor)


def sacar(clientes, db):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n=== Cliente não encontrado! ===")
        return

    try:
        valor = float(input("Informe o valor do saque: "))
    except ValueError:
        print("\nValor inválido.")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    transacao = Saque(valor)
    cliente.realizar_transacao(conta, transacao)

    ultima = conta.historico.transacoes[-1] if conta.historico.transacoes else None
    if ultima and ultima["tipo"] == "Saque":
        db.atualizar_saldo(conta.numero, conta.saldo)
        db.salvar_transacao(conta.numero, "Saque", valor)


def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n=== Cliente não encontrado! ===")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n================ EXTRATO ================")
    transacoes = conta.historico.transacoes

    if not transacoes:
        print("Não foram realizadas movimentações.")
    else:
        for t in transacoes:
            print(f"\n{t['tipo']}:\n\tR$ {t['valor']:.2f}\n\tData: {t['data']}")

    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")

    realizadas_hoje = len(conta.historico.transacoes_do_dia)
    print(f"\nTransações realizadas: {realizadas_hoje}/{Cliente.LIMITE_TRANSACOES_DIARIAS}")
    print("==========================================")


# ---------------------------------------------------------------------------
# Gerenciamento de clientes
# ---------------------------------------------------------------------------

def criar_cliente(clientes, db):
    cpf = input("Informe o CPF (somente números): ")
    if filtrar_cliente(cpf, clientes):
        print("\n=== Já existe cliente com esse CPF! ===")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd/mm/aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    cliente = PessoaFisica(nome=nome, cpf=cpf, data_nascimento=data_nascimento, endereco=endereco)
    clientes.append(cliente)
    db.salvar_cliente(cpf, nome, data_nascimento, endereco)
    print("\n=== Cliente criado com sucesso! ===")


def listar_clientes(clientes):
    if not clientes:
        print("\nNenhum cliente cadastrado!")
        return
    for cliente in clientes:
        print("=" * 100)
        print(textwrap.dedent(f"""\
            Nome:\t\t{cliente.nome}
            CPF:\t\t{formatar_cpf(cliente.cpf)}
            Data Nasc.:\t{formatar_data(cliente.data_nascimento)}
            Endereço:\t{cliente.endereco}"""))
        print("=" * 100)


def excluir_cliente(clientes, contas, db):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n=== Cliente não encontrado! ===")
        return

    print(f"\nCliente: {cliente.nome}")
    if cliente.contas:
        print(f"Atenção: este cliente possui {len(cliente.contas)} conta(s). Todas serão excluídas.")

    confirmacao = input("\nConfirma exclusão do cliente e todas as suas contas? (s/n): ")
    if confirmacao.lower() != "s":
        print("\nOperação cancelada.")
        return

    for conta in cliente.contas:
        if conta in contas:
            contas.remove(conta)

    db.excluir_cliente(cliente.cpf)
    clientes.remove(cliente)
    print(f"\n=== Cliente {cliente.nome} excluído com sucesso! ===")


# ---------------------------------------------------------------------------
# Gerenciamento de contas
# ---------------------------------------------------------------------------

def criar_conta(clientes, contas, db):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n=== Cliente não encontrado! ===")
        return

    numero = db.salvar_conta(cpf)
    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero)
    contas.append(conta)
    cliente.adicionar_conta(conta)
    print("\n=== Conta criada com sucesso! ===")


def listar_contas(contas):
    if not contas:
        print("\nNenhuma conta cadastrada!")
        return
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(f"""\
            Agência:\t{conta.agencia}
            C/C:\t\t{conta.numero}
            Titular:\t{conta.cliente.nome}
            CPF: \t\t{formatar_cpf(conta.cliente.cpf)}"""))
        print("=" * 100)


def excluir_conta(clientes, contas, db):
    cpf = input("Informe o CPF do titular: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n=== Cliente não encontrado! ===")
        return

    if not cliente.contas:
        print("\n=== Cliente não possui contas cadastradas! ===")
        return

    print("\nContas do cliente:")
    for conta in cliente.contas:
        print(f"  Nº {conta.numero} | Saldo: R$ {conta.saldo:.2f}")

    try:
        numero = int(input("\nInforme o número da conta a excluir: "))
    except ValueError:
        print("\nNúmero inválido.")
        return

    conta_alvo = next((c for c in cliente.contas if c.numero == numero), None)
    if not conta_alvo:
        print("\n=== Conta não encontrada para este cliente! ===")
        return

    confirmacao = input(f"\nConfirma exclusão da conta nº {numero}? (s/n): ")
    if confirmacao.lower() != "s":
        print("\nOperação cancelada.")
        return

    db.excluir_conta(numero)
    contas.remove(conta_alvo)
    cliente.contas.remove(conta_alvo)
    print(f"\n=== Conta nº {numero} excluída com sucesso! ===")


# ---------------------------------------------------------------------------
# Carga inicial e loop principal
# ---------------------------------------------------------------------------

def carregar_dados(db):
    """Reconstrói o estado em memória a partir do banco de dados

    Retorna (clientes, contas) com as associações e históricos
    já restaurados, permitindo que a sessão continue de onde parou
    """
    clientes, contas = [], []

    for row in db.listar_clientes():
        c = PessoaFisica(
            nome=row["nome"],
            cpf=row["cpf"],
            data_nascimento=row["data_nascimento"],
            endereco=row["endereco"]
        )
        clientes.append(c)

    for row in db.listar_contas():
        cliente = filtrar_cliente(row["cpf"], clientes)
        if not cliente:
            continue
        conta = ContaCorrente.nova_conta(cliente=cliente, numero=row["numero"])
        conta._saldo = row["saldo"]

        for t in db.buscar_transacoes(row["numero"]):
            conta.historico._transacoes.append({
                "tipo": t["tipo"],
                "valor": t["valor"],
                "data": t["data"]
            })

        contas.append(conta)
        cliente.adicionar_conta(conta)

    return clientes, contas


def main():
    db = Database()
    clientes, contas = carregar_dados(db)

    menu = """
╔══════════════════════════════════════╗
║           SISTEMA BANCÁRIO           ║
╠══════════════════════════════════════╣
║  TRANSAÇÕES                          ║
║  1  >  Depositar                     ║
║  2  >  Sacar                         ║
║  3  >  Visualizar Extrato            ║
╠══════════════════════════════════════╣
║  CLIENTES                            ║
║  4  >  Novo Cliente                  ║
║  5  >  Listar Clientes               ║
║  6  >  Excluir Cliente               ║
╠══════════════════════════════════════╣
║  CONTAS                              ║
║  7  >  Nova Conta                    ║
║  8  >  Listar Contas                 ║
║  9  >  Excluir Conta                 ║
╠══════════════════════════════════════╣
║  0  >  Sair                          ║
╚══════════════════════════════════════╝
>> """

    while True:
        opcao = input(menu)

        if opcao == "1":
            depositar(clientes, db)
        elif opcao == "2":
            sacar(clientes, db)
        elif opcao == "3":
            exibir_extrato(clientes)
        elif opcao == "4":
            criar_cliente(clientes, db)
        elif opcao == "5":
            listar_clientes(clientes)
        elif opcao == "6":
            excluir_cliente(clientes, contas, db)
        elif opcao == "7":
            criar_conta(clientes, contas, db)
        elif opcao == "8":
            listar_contas(contas)
        elif opcao == "9":
            excluir_conta(clientes, contas, db)
        elif opcao == "0":
            db.fechar()
            print("\nEncerrando o sistema. Obrigado por utilizar nossos serviços!")
            break
        else:
            print("\nOpção inválida. Tente novamente.")


main()