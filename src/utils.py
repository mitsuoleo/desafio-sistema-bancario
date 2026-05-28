from datetime import datetime


def formatar_cpf(cpf):
    """Converte qualquer entrada de CPF para o formato xxx.xxx.xxx-xx.

    Aceita CPF com ou sem pontuação. Retorna sem formatação se
    a quantidade de dígitos for diferente de 11.
    """
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) != 11:
        return cpf
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def formatar_data(data_nascimento):
    """Normaliza datas de nascimento para o formato dd/mm/aaaa.

    Aceita sequências de 8 dígitos e os formatos dd/mm/YYYY e dd-mm-YYYY.
    Retorna a string original quando nenhum formato é reconhecido.
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


def filtrar_cliente(cpf, clientes):
    """Busca um cliente pelo CPF, ignorando pontuação na comparação."""
    cpf_digitado = ''.join(filter(str.isdigit, cpf))
    clientes_filtrados = [
        cliente for cliente in clientes
        if ''.join(filter(str.isdigit, cliente.cpf)) == cpf_digitado
    ]
    return clientes_filtrados[0] if clientes_filtrados else None


def obter_conta(cliente, numero_conta=None):
    """Retorna a conta do cliente. Com várias contas, exige numero_conta."""
    if not cliente.contas:
        return None
    if numero_conta is not None:
        return next((c for c in cliente.contas if c.numero == numero_conta), None)
    if len(cliente.contas) == 1:
        return cliente.contas[0]
    return None


def recuperar_conta_cliente(cliente):
    """Retorna a conta do cliente.

    Se o cliente tiver mais de uma conta, exibe a lista e pede
    que o usuário escolha pelo número. Retorna None se não houver
    contas ou se a escolha for inválida.
    """
    if not cliente.contas:
        print("\nCliente não possui contas cadastradas.")
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
