from src.database import Database
from src.models.cliente import PessoaFisica
from src.models.conta import ContaCorrente
from src.services.operacoes import depositar, sacar, exibir_extrato
from src.services.cadastro import (
    criar_cliente, listar_clientes, excluir_cliente,
    criar_conta, listar_contas, excluir_conta,
)
from src.utils import filtrar_cliente


def carregar_dados(db):
    """Reconstrói o estado em memória a partir do banco de dados.

    Retorna (clientes, contas) com as associações e históricos
    já restaurados, permitindo que a sessão continue de onde parou.
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
        conta.restaurar_saldo(row["saldo"])

        for t in db.buscar_transacoes(row["numero"]):
            data_str = (
                t["data"].strftime("%d/%m/%Y %H:%M:%S")
                if hasattr(t["data"], "strftime")
                else t["data"]
            )
            conta.historico.restaurar_transacao(t["tipo"], t["valor"], data_str)

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


if __name__ == "__main__":
    main()
