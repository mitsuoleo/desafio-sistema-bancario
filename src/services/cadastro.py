import textwrap

from src.models.cliente import PessoaFisica
from src.models.conta import ContaCorrente
from src.utils import filtrar_cliente, formatar_cpf, formatar_data, recuperar_conta_cliente


def criar_cliente(clientes, db):
    cpf = input("Informe o CPF (somente números): ")
    cpf_digitos = "".join(filter(str.isdigit, cpf))
    if len(cpf_digitos) != 11:
        print("\nCPF inválido. Informe 11 dígitos.")
        return
    cpf = cpf_digitos
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
