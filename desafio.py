import datetime

menu = """
=======Menu de Opções======
1. Depositar
2. Sacar
3. Visualizar Extrato
4. Novo Usuário
5. Nova Conta
6. Listar Usuários
7. Listar Contas
8. Sair
===========================
""" #O menu de opções é apresentado ao usuário para que ele possa escolher a ação desejada

def depositar(saldo, valor, extrato, /):
    if valor > 0:
        data_hora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        saldo += valor
        extrato += f"[{data_hora}] Depósito: R$ {valor:.2f}\n"
        print("\nDepósito realizado com sucesso!")
    else:
        print("\nValor inválido. O depósito deve ser maior que zero.")
    return saldo, extrato
    #A função depositar é responsável por realizar um depósito, verificando se o valor do depósito é válido (maior que zero). Ela atualiza o saldo e o extrato com a data e hora do depósito, além do valor depositado

def sacar(*, saldo, valor, extrato, limite, numero_saques, limite_saques, numero_transacoes, limite_transacoes_diarias):
    if valor > saldo:
        print("\nSaldo insuficiente para realizar o saque.")
    elif valor > limite:
        print("\nValor do saque excede o limite permitido.")
    elif numero_saques >= limite_saques:
        print("\nNúmero máximo de saques atingido.")
    elif numero_transacoes >= limite_transacoes_diarias:
        print("\nLimite diário de transações atingido. Por favor, tente novamente amanhã.")
    elif valor <= 0:
        print("\nValor inválido. O saque deve ser maior que zero.")
    else:
        saldo -= valor
        data_hora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        extrato += f"[{data_hora}] Saque: R$ {valor:.2f}\n"
        numero_saques += 1
        numero_transacoes += 1
        print("\nSaque realizado com sucesso!")
    return saldo, extrato, numero_saques, numero_transacoes
    #A função sacar é responsável por realizar um saque, verificando se o valor do saque é válido e se as condições para realizar o saque são atendidas. Ela atualiza o saldo, o extrato e os contadores de saques e transações

def exibir_extrato(saldo, /, *, extrato):
    print("\n======= Extrato =======")
    print("Não foram realizadas movimentações." if not extrato else extrato)
    print(f"Saldo: R$ {saldo:.2f}")
    print(f"Limite de Transações Diárias: {1
    numero_transacoes}/{LIMITE_TRANSACOES_DIARIAS}")
    print("========================")
    #A função exibir_extrato é responsável por exibir o extrato das transações realizadas, mostrando os depósitos e saques, além do saldo atual. Se nenhuma transação foi realizada, uma mensagem informando isso é exibida

def criar_usuario(usuarios):
    cpf = input("Digite o CPF do usuário (somente números): ")

    if any(usuario['cpf'] == cpf for usuario in usuarios):
        print("\nCPF já cadastrado. Por favor, tente novamente.")
        return

    nome = input("Digite o nome completo do usuário: ")
    data_nascimento = input("Digite a data de nascimento do usuário (DD/MM/AAAA): ")
    endereco = input("Digite o endereço do usuário (logradouro, número - bairro - cidade/sigla do estado): ")

    usuario = {
        "cpf": cpf,
        "nome": nome,
        "data_nascimento": data_nascimento,
        "endereço": endereco
    }
    usuarios.append(usuario)
    print("=== Usuário criado com sucesso! ===")
    #A função criar_usuario é responsável por criar um novo usuário, solicitando informações como CPF, nome, data de nascimento e endereço. Ela verifica se o CPF já está cadastrado para evitar duplicidade. Se o CPF for único, o usuário é criado e adicionado à lista de usuários

def criar_conta(agencia, numero_conta, usuarios):
    cpf = input("Digite o CPF do usuário para associar à conta: ")

    usuario = next((usuario for usuario in usuarios if usuario['cpf'] == cpf), None)

    if usuario is None:
        print("\nUsuário não encontrado. Por favor, crie um usuário antes de criar uma conta.")
        return None

    conta = {
        "agencia": agencia,
        "numero_conta": numero_conta,
        "usuario": usuario
    }
    print("=== Conta criada com sucesso! ===")
    return conta
    #A função criar_conta é responsável por criar uma nova conta bancária, associando-a a um usuário existente. Ela solicita o CPF do usuário para verificar se ele está cadastrado. Se o usuário for encontrado, a conta é criada com um número de agência, número de conta e as informações do usuário associadas. A conta é então adicionada à lista de contas

def listar_usuarios(usuarios):
    if not usuarios:
        print("Nenhum usuário cadastrado.")
        return

    print("\n======= Usuários Cadastrados =======")
    for usuario in usuarios:
        linha = f"""\
            CPF:\t\t{formatar_cpf(usuario['cpf'])}
            Nome:\t\t{usuario['nome']}
            Data de Nascimento:\t{formatar_data(usuario['data_nascimento'])}
            Endereço:\t{usuario['endereço']}
        """
        print(linha)
    print("====================================")
    #A função listar_usuarios é responsável por exibir a lista de usuários cadastrados, mostrando o CPF, nome, data de nascimento e endereço de cada usuário. Se não houver usuários cadastrados, uma mensagem informando isso é exibida

def listar_contas(contas):
    if not contas:
        print("Nenhuma conta cadastrada.")
        return

    print("\n======= Contas Cadastradas =======")
    for conta in contas:
        linha = f"""\
            Agência:\t{conta['agencia']}
            C/C:\t\t{conta['numero_conta']}
            Titular:\t{conta['usuario']['nome']}
        """
        print(linha)
    print("===================================")
    #A função listar_contas é responsável por exibir a lista de contas cadastradas, mostrando o número da agência, número da conta e o nome do titular associado a cada conta. Se não houver contas cadastradas, uma mensagem informando isso é exibida
 
def formatar_cpf(cpf):
    numeros = ''.join(filter(str.isdigit, cpf))
    if len(numeros) == 11:
        return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"
    return cpf

def formatar_data(data):
    numeros = ''.join(filter(str.isdigit, data))
    if len(numeros) == 8:
        return f"{numeros[:2]}/{numeros[2:4]}/{numeros[4:]}"
    return data
#A função auxiliar formatar_data é responsável por formatar uma string de data, extraindo apenas os números e organizando-os no formato DD/MM/AAAA. Se a string de data contiver exatamente 8 dígitos, ela é formatada corretamente. Caso contrário, a string original é retornada sem alterações

usuarios = []
contas = []
#O programa inicia com listas vazias para armazenar os usuários e as contas criadas. Essas listas serão utilizadas para gerenciar as informações dos usuários e das contas ao longo do programa

saldo = 0
limite = 500
extrato = ""
numero_saques = 0
numero_transacoes = 0

numero_conta = 1
LIMITE_SAQUES = 3
LIMITE_TRANSACOES_DIARIAS = 10 
AGENCIA = "0001"
#O programa define variáveis para gerenciar o saldo, limite de saque, extrato, número de saques realizados, número de transações realizadas, número da conta, limite de saques e limite diário de transações. Essas variáveis são utilizadas para controlar as operações bancárias e garantir que as regras estabelecidas sejam respeitadas

while True:
    opcao = input(menu)

    if opcao in ["1", "2"]:
        if numero_transacoes >= LIMITE_TRANSACOES_DIARIAS: #Antes de permitir que o usuário realize um depósito ou saque, o programa verifica se o número de transações realizadas no dia já atingiu o limite diário definido. Se o limite for atingido, uma mensagem é exibida informando que o limite diário de transações foi atingido e o usuário é solicitado a tentar novamente no dia seguinte. Isso garante que o usuário não possa realizar mais de 10 transações em um único dia
            print("Limite diário de 10 transações atingido. Por favor, tente novamente amanhã.") 
            continue

    if opcao == "1":
        valor = float(input("Digite o valor do depósito: "))
        saldo, extrato = depositar(saldo, valor, extrato) #chamada da função depositar para realizar um depósito, atualizando o saldo e o extrato com as informações do depósito realizado
        numero_transacoes += 1 #O contador de transações é incrementado a cada depósito ou saque realizado, para garantir que o limite diário de transações seja respeitado
            

    elif opcao == "2":
        valor = float(input("Digite o valor do saque: "))
        saldo, extrato, numero_saques, numero_transacoes = sacar(
            saldo=saldo,
            valor=valor,
            extrato=extrato,
            limite=limite,
            numero_saques=numero_saques,
            limite_saques=LIMITE_SAQUES,
            numero_transacoes=numero_transacoes,
            limite_transacoes_diarias=LIMITE_TRANSACOES_DIARIAS
        )

    elif opcao == "3":
        exibir_extrato(saldo, extrato=extrato)
        #O programa chama a função exibir_extrato para mostrar o extrato das transações realizadas

    elif opcao == "4":
        criar_usuario(usuarios)
        #O programa chama a função criar_usuario para permitir que o usuário crie um novo cadastro
        
    elif opcao == "5":
        conta = criar_conta(AGENCIA, numero_conta, usuarios)
        if conta:
            contas.append(conta)
            numero_conta += 1
        #O programa chama a função criar_conta para permitir que o usuário crie uma nova conta bancária associada a um usuário existente4
    elif opcao == "6":
        listar_usuarios(usuarios)

    elif opcao == "7":
        listar_contas(contas)

    elif opcao == "8":
        print("Encerrando o programa. Obrigado por usar nosso serviço!")
        break
        #O programa é encerrado quando o usuário escolhe a opção 4, exibindo uma mensagem de agradecimento

    else:
        print("Opção inválida. Por favor, escolha uma opção válida.")
        #Se o usuário escolher uma opção que não está no menu, uma mensagem de erro é exibida, solicitando que ele escolha uma opção válida