import textwrap
from abc import ABC, abstractmethod
from datetime import datetime


class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass

class Deposito(Transacao):
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
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes
    
    @property
    def transacoes_do_dia(self):
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
    LIMITE_TRANSACOES_DIARIAS = 10

    def __init__(self, endereco):
        self._endereco = endereco
        self._contas = []

    def realizar_transacao(self, conta, transacao):
        if len(conta.historico.transacoes_do_dia) >= self.LIMITE_TRANSACOES_DIARIAS:
            print("\nLimite diário de transações atingido. Tente novamente amanhã.")
            return
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self._contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, nome, cpf, data_nascimento, endereco):
        super().__init__(endereco)
        self._nome = nome
        self._cpf = cpf
        self._data_nascimento = data_nascimento

    @property
    def nome(self):
        return self._nome

class Conta: 
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
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
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
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
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len([transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__])
        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            print("\nValor do saque excede o limite permitido.")
        elif excedeu_saques:
            print("\nNúmero máximo de saques atingido.")
        else:
            return super().sacar(valor)
        return False

def recuperar_conta_cliente(cliente):
    if not cliente._contas:
        print("\nCliente não possui contas cadastradas")
        return None
    return cliente._contas[0]

def depositar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n=== Cliente não encontrado! ===")
        return

    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)

def sacar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n=== Cliente não encontrado! ===")
        return

    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)

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

    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}\n\tData: {transacao['data']}\n"

    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")

    realizadas_hoje=len(conta.historico.transacoes_do_dia)
    restantes = Cliente.LIMITE_TRANSACOES_DIARIAS - realizadas_hoje
    print(f"\nTransações realizadas: {realizadas_hoje}/{Cliente.LIMITE_TRANSACOES_DIARIAS}")
    print("==========================================")

def criar_cliente(clientes):
    cpf = input("Informe o CPF (somente números): ")
    if filtrar_cliente(cpf, clientes):
        print("\n=== Já existe cliente com esse CPF! ===")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd/mm/aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    cliente = PessoaFisica(nome=nome, cpf=cpf, data_nascimento=data_nascimento, endereco=endereco)
    clientes.append(cliente)
    print("\n=== Cliente criado com sucesso! ===")

def filtrar_cliente(cpf, clientes):
    cpf_digitado = ''.join(filter(str.isdigit, cpf))
    clientes_filtrados = [
        cliente for cliente in clientes 
        if ''.join(filter(str.isdigit, cliente._cpf)) == cpf_digitado
    ]
    return clientes_filtrados[0] if clientes_filtrados else None

def criar_conta(clientes, contas, numero_conta):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n=== Cliente não encontrado! ===")
        return

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.adicionar_conta(conta)
    print("\n=== Conta criada com sucesso! ===")

def formatar_cpf(cpf):
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) != 11:
        return cpf # Retorna o CPF sem formatação se não tiver 11 dígitos
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

def formatar_data(data_nascimento):
    digits = ''.join(filter(str.isdigit, data_nascimento))
    if len(digits) == 8:
        return f"{digits[:2]}/{digits[2:4]}/{digits[4:]}"
    for fmt in ("%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(data_nascimento, fmt).strftime("%d/%m/%Y")
        except ValueError:
            continue
    return data_nascimento  # retorna original se nenhum formato bater
    
def listar_clientes(clientes):
    if not clientes:
        print("\nNenhum cliente cadastrado!")
        return
    for cliente in clientes:
        print("=" * 100)
        print(textwrap.dedent(f"""\
            Nome:\t\t{cliente.nome}
            CPF:\t\t{formatar_cpf(cliente._cpf)}
            Data Nasc.:\t{formatar_data(cliente._data_nascimento)}
            Endereço:\t{cliente._endereco}"""))
        print("=" * 100)

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
            CPF: \t\t{formatar_cpf(conta.cliente._cpf)}""")) 
            print("=" * 100)

def main():
    clientes = []
    contas = []
    menu = """
=======Menu de Opções======
1. Depositar
2. Sacar
3. Visualizar Extrato
4. Novo Cliente
5. Nova Conta
6. Listar Clientes
7. Listar Contas
8. Sair
===========================
"""

    while True:
        opcao = input(menu)

        if opcao == "1":
            depositar(clientes)
        elif opcao == "2":
            sacar(clientes)
        elif opcao == "3":
            exibir_extrato(clientes)
        elif opcao == "4":
            criar_cliente(clientes)
        elif opcao == "5":
            numero_conta = len(contas) + 1
            criar_conta(clientes, contas, numero_conta)
        elif opcao == "6":
            listar_clientes(clientes)
        elif opcao == "7":
            listar_contas(contas)
        elif opcao == "8":
            print("Encerrando o programa. Obrigado por usar nosso sistema bancário!")
            break
        else:
            print("Opção inválida. Por favor, escolha uma opção válida.")

main()