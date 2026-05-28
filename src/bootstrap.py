from src.models.cliente import PessoaFisica
from src.models.conta import ContaCorrente
from src.utils import filtrar_cliente


def carregar_dados(db):
    """Reconstrói o estado em memória a partir do banco de dados."""
    clientes, contas = [], []

    for row in db.listar_clientes():
        c = PessoaFisica(
            nome=row["nome"],
            cpf=row["cpf"],
            data_nascimento=row["data_nascimento"],
            endereco=row["endereco"],
        )
        clientes.append(c)

    for row in db.listar_contas():
        cliente = filtrar_cliente(row["cpf"], clientes)
        if not cliente:
            continue

        conta = ContaCorrente.nova_conta(
            cliente=cliente,
            numero=row["numero"],
            limite=row["limite"],
            limite_saques=row["limite_saques"],
        )
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
