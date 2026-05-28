"""API legada sem autenticação — desabilitada por padrão (ENABLE_LEGACY_API=true)."""

from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel, Field

from src.models.cliente import PessoaFisica
from src.models.conta import ContaCorrente
from src.models.transacao import Deposito, Saque
from src.utils import filtrar_cliente, formatar_cpf, formatar_data, obter_conta

router = APIRouter(prefix="/api", tags=["API legada (sem auth)"])


class ClienteCreate(BaseModel):
    cpf: str
    nome: str
    data_nascimento: str
    endereco: str


class ContaCreate(BaseModel):
    cpf: str


class TransacaoRequest(BaseModel):
    cpf: str
    valor: float = Field(gt=0)
    numero_conta: int | None = None


class ExcluirContaRequest(BaseModel):
    cpf: str


def _get_state():
    from src.api.server import state

    return state


def _serializar_cliente(cliente):
    return {
        "nome": cliente.nome,
        "cpf": cliente.cpf,
        "cpf_formatado": formatar_cpf(cliente.cpf),
        "data_nascimento": formatar_data(cliente.data_nascimento),
        "endereco": cliente.endereco,
        "contas": [c.numero for c in cliente.contas],
    }


def _serializar_conta(conta):
    realizadas = len(conta.historico.transacoes_do_dia)
    return {
        "numero": conta.numero,
        "agencia": conta.agencia,
        "saldo": float(conta.saldo),
        "limite_saque": float(conta._limite),
        "limite_saques_dia": conta._limite_saques,
        "titular": conta.cliente.nome,
        "cpf": conta.cliente.cpf,
        "cpf_formatado": formatar_cpf(conta.cliente.cpf),
        "transacoes_hoje": realizadas,
        "limite_transacoes_dia": PessoaFisica.LIMITE_TRANSACOES_DIARIAS,
    }


def _resolver_conta(cpf: str, numero_conta: int | None):
    state = _get_state()
    cliente = filtrar_cliente(cpf, state.clientes)
    if not cliente:
        raise HTTPException(404, "Cliente não encontrado.")

    conta = obter_conta(cliente, numero_conta)
    if conta:
        return cliente, conta

    if not cliente.contas:
        raise HTTPException(400, "Cliente não possui contas cadastradas.")

    raise HTTPException(
        400,
        "Cliente possui mais de uma conta. Informe o número da conta.",
    )


@router.get("/clientes")
def listar_clientes():
    return [_serializar_cliente(c) for c in _get_state().clientes]


@router.post("/clientes", status_code=201)
def criar_cliente(payload: ClienteCreate):
    state = _get_state()
    cpf_digitos = "".join(filter(str.isdigit, payload.cpf))
    if len(cpf_digitos) != 11:
        raise HTTPException(400, "CPF inválido. Informe 11 dígitos.")
    if filtrar_cliente(cpf_digitos, state.clientes):
        raise HTTPException(409, "Já existe cliente com esse CPF.")

    cliente = PessoaFisica(
        nome=payload.nome.strip(),
        cpf=cpf_digitos,
        data_nascimento=payload.data_nascimento.strip(),
        endereco=payload.endereco.strip(),
    )
    state.clientes.append(cliente)
    state.db.salvar_cliente(
        cpf_digitos,
        cliente.nome,
        cliente.data_nascimento,
        cliente.endereco,
    )
    return _serializar_cliente(cliente)


@router.delete("/clientes/{cpf}")
def excluir_cliente(cpf: str):
    state = _get_state()
    cliente = filtrar_cliente(cpf, state.clientes)
    if not cliente:
        raise HTTPException(404, "Cliente não encontrado.")

    for conta in list(cliente.contas):
        if conta in state.contas:
            state.contas.remove(conta)

    state.db.excluir_cliente(cliente.cpf)
    state.clientes.remove(cliente)
    return {"mensagem": f"Cliente {cliente.nome} excluído com sucesso."}


@router.get("/contas")
def listar_contas():
    return [_serializar_conta(c) for c in _get_state().contas]


@router.post("/contas", status_code=201)
def criar_conta(payload: ContaCreate):
    state = _get_state()
    cliente = filtrar_cliente(payload.cpf, state.clientes)
    if not cliente:
        raise HTTPException(404, "Cliente não encontrado.")

    numero = state.db.salvar_conta(cliente.cpf)
    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero)
    state.contas.append(conta)
    cliente.adicionar_conta(conta)
    return _serializar_conta(conta)


@router.delete("/contas/{numero}")
def excluir_conta(numero: int, payload: ExcluirContaRequest = Body(...)):
    state = _get_state()
    cliente = filtrar_cliente(payload.cpf, state.clientes)
    if not cliente:
        raise HTTPException(404, "Cliente não encontrado.")

    conta = obter_conta(cliente, numero)
    if not conta:
        raise HTTPException(404, "Conta não encontrada para este cliente.")

    state.db.excluir_conta(numero)
    state.contas.remove(conta)
    cliente.contas.remove(conta)
    return {"mensagem": f"Conta nº {numero} excluída com sucesso."}


@router.post("/depositos")
def depositar(payload: TransacaoRequest):
    state = _get_state()
    try:
        valor = Decimal(str(payload.valor))
    except InvalidOperation:
        raise HTTPException(400, "Valor inválido.")

    cliente, conta = _resolver_conta(payload.cpf, payload.numero_conta)
    sucesso = cliente.realizar_transacao(conta, Deposito(valor))

    if not sucesso:
        raise HTTPException(400, "Não foi possível realizar o depósito.")

    state.db.salvar_operacao(conta.numero, "Depósito", valor, conta.saldo)
    return {
        "mensagem": "Depósito realizado com sucesso.",
        "conta": _serializar_conta(conta),
    }


@router.post("/saques")
def sacar(payload: TransacaoRequest):
    state = _get_state()
    try:
        valor = Decimal(str(payload.valor))
    except InvalidOperation:
        raise HTTPException(400, "Valor inválido.")

    cliente, conta = _resolver_conta(payload.cpf, payload.numero_conta)
    sucesso = cliente.realizar_transacao(conta, Saque(valor))

    if not sucesso:
        raise HTTPException(
            400,
            "Não foi possível realizar o saque. Verifique saldo, limite de R$ 500 "
            "por saque e o máximo de 3 saques por dia.",
        )

    state.db.salvar_operacao(conta.numero, "Saque", valor, conta.saldo)
    return {
        "mensagem": "Saque realizado com sucesso.",
        "conta": _serializar_conta(conta),
    }


@router.get("/extrato")
def extrato(cpf: str, numero_conta: int | None = None):
    cliente, conta = _resolver_conta(cpf, numero_conta)
    transacoes = [
        {
            "tipo": t["tipo"],
            "valor": float(t["valor"]),
            "data": t["data"],
        }
        for t in conta.historico.transacoes
    ]
    realizadas = len(conta.historico.transacoes_do_dia)
    return {
        "titular": cliente.nome,
        "conta": conta.numero,
        "agencia": conta.agencia,
        "saldo": float(conta.saldo),
        "transacoes": transacoes,
        "transacoes_hoje": realizadas,
        "limite_transacoes_dia": PessoaFisica.LIMITE_TRANSACOES_DIARIAS,
    }
