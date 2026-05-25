from decimal import Decimal, InvalidOperation

from src.models.cliente import Cliente
from src.models.transacao import Deposito, Saque
from src.utils import filtrar_cliente, recuperar_conta_cliente


def depositar(clientes, db):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n=== Cliente não encontrado! ===")
        return

    try:
        valor = Decimal(input("Informe o valor do depósito: "))
    except InvalidOperation:
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
        valor = Decimal(input("Informe o valor do saque: "))
    except InvalidOperation:
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
