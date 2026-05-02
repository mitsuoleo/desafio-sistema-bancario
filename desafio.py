import datetime

menu = """
=======Menu de Opções======
1. Depositar
2. Sacar
3. Visualizar Extrato
4. Sair
===========================
""" #O menu de opções é apresentado ao usuário para que ele possa escolher a ação desejada. 

saldo = 0
limite = 500
extrato = ""
numero_saques = 0
numero_transacoes = 0
LIMITE_SAQUES = 3
LIMITE_TRANSACOES_DIARIAS = 10 
#O programa inicia com um saldo de 0, um limite de saque de 500, um extrato vazio e um contador de saques e transações igual a 0. O limite de saques é definido como 3. O limite de transações diárias é definido como 10, o que significa que o usuário pode realizar no máximo 10 transações (depósitos e saques) em um dia.

while True:
    opcao = input(menu)

    if opcao in ["1", "2"]:
        if numero_transacoes >= LIMITE_TRANSACOES_DIARIAS:
            print("Limite diário de 10 transações atingido. Por favor, tente novamente amanhã.")
            continue

    if opcao == "1":
        valor = float(input("Digite o valor do depósito: "))

        if valor > 0:
            data_hora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            saldo += valor
            extrato += f"[{data_hora}] Depósito: R$ {valor:.2f}\n"
            numero_transacoes += 1
            print("Depósito realizado com sucesso!")
        else:
            print("Valor inválido. O depósito deve ser maior que zero.")

    elif opcao == "2":
        valor = float(input("Digite o valor do saque: "))

        if valor > saldo:
            print("Saldo insuficiente para realizar o saque.")
        elif valor > limite:
            print("Valor do saque excede o limite permitido.")
        elif numero_saques >= LIMITE_SAQUES:
            print("Número máximo de saques atingido.")
        elif valor <= 0:
            print("Valor inválido. O saque deve ser maior que zero.")
        else:
            saldo -= valor
            data_hora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            extrato += f"[{data_hora}] Saque: R$ {valor:.2f}\n"
            numero_saques += 1
            numero_transacoes += 1
            print("Saque realizado com sucesso!")
            #O programa verifica se o valor do saque é maior que o saldo disponível, se excede o limite permitido, se o número máximo de saques foi atingido ou se o valor é inválido. Se todas as condições forem atendidas, o saque é realizado, o saldo é atualizado, o extrato é registrado e o contador de saques é incrementado.

    elif opcao == "3":
        print("\n=======Extrato:=======")
        print(extrato if extrato else "Nenhuma transação realizada.")
        print(f"Saldo atual: R$ {saldo:.2f}")
        print(f"Transações realizadas hoje: {numero_transacoes}/{LIMITE_TRANSACOES_DIARIAS}")
        print("======================\n")
        #O programa exibe o extrato das transações realizadas, mostrando os depósitos e saques, além do saldo atual. Se nenhuma transação foi realizada, uma mensagem informando isso é exibida.

    elif opcao == "4":
        print("Encerrando o programa. Obrigado por usar nosso serviço!")
        break
        #O programa é encerrado quando o usuário escolhe a opção 4, exibindo uma mensagem de agradecimento.

    else:
        print("Opção inválida. Por favor, escolha uma opção válida.")
        #Se o usuário escolher uma opção que não está no menu, uma mensagem de erro é exibida, solicitando que ele escolha uma opção válida.