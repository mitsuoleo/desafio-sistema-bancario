from src.bootstrap import carregar_dados
from src.database import Database
from src.env import carregar_env

carregar_env()
from src.services.operacoes import depositar, sacar, exibir_extrato
from src.services.cadastro import (
    criar_cliente, listar_clientes, excluir_cliente,
    criar_conta, listar_contas, excluir_conta,
)


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


if __name__ == "__main__":
    main()
