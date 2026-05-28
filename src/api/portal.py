from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, Field

from src.api.auth import criar_token_portal, validar_token_portal
from src.models.cliente import PessoaFisica
from src.models.conta import ContaCorrente
from src.models.transacao import Deposito, Saque
from src.utils import filtrar_cliente, formatar_cpf, formatar_data, obter_conta

router = APIRouter(prefix="/api/portal", tags=["Portal do Cliente"])


class CadastroClienteConta(BaseModel):
    cpf: str
    nome: str
    data_nascimento: str
    endereco: str


class TransacaoPortal(BaseModel):
    cpf: str
    valor: float = Field(gt=0)
    numero_conta: int


def _cpf_digitos(cpf: str) -> str:
    return "".join(filter(str.isdigit, cpf))


def _get_state():
    from src.api.server import state

    return state


def _resposta_sessao(cliente):
    cpf = cliente.cpf
    return {
        "token": criar_token_portal(cpf),
        "sessao": _serializar_sessao(cliente),
    }


def _cliente_por_cpf(cpf: str):
    cliente = filtrar_cliente(cpf, _get_state().clientes)
    if not cliente:
        raise HTTPException(404, "CPF não cadastrado.")
    return cliente


def _conta_do_cpf(cliente, numero_conta: int):
    conta = obter_conta(cliente, numero_conta)
    if not conta:
        raise HTTPException(404, "Conta não encontrada para este CPF.")
    return conta


def _cpf_da_sessao(x_portal_token: str = Header(..., alias="X-Portal-Token")) -> str:
    cpf = validar_token_portal(x_portal_token)
    if not cpf:
        raise HTTPException(
            401,
            "Sessão inválida ou expirada. Entre novamente com seu CPF.",
        )
    return cpf


def _exigir_cpf_da_sessao(cpf_informado: str, cpf_sessao: str) -> str:
    cpf_body = _cpf_digitos(cpf_informado)
    if cpf_body != cpf_sessao:
        raise HTTPException(403, "Operação permitida apenas para o CPF autenticado.")
    return cpf_body


def _serializar_conta(conta):
    realizadas = len(conta.historico.transacoes_do_dia)
    return {
        "numero": conta.numero,
        "agencia": conta.agencia,
        "saldo": float(conta.saldo),
        "limite_saque": float(conta._limite),
        "limite_saques_dia": conta._limite_saques,
        "transacoes_hoje": realizadas,
        "limite_transacoes_dia": PessoaFisica.LIMITE_TRANSACOES_DIARIAS,
    }


def _serializar_sessao(cliente):
    return {
        "nome": cliente.nome,
        "cpf": cliente.cpf,
        "cpf_formatado": formatar_cpf(cliente.cpf),
        "data_nascimento": formatar_data(cliente.data_nascimento),
        "endereco": cliente.endereco,
        "contas": [_serializar_conta(c) for c in cliente.contas],
    }


@router.get("/sessao/{cpf}")
def sessao_cliente(cpf: str):
    cpf = _cpf_digitos(cpf)
    if len(cpf) != 11:
        raise HTTPException(400, "CPF inválido. Informe 11 dígitos.")
    cliente = filtrar_cliente(cpf, _get_state().clientes)
    if not cliente:
        raise HTTPException(404, "CPF não cadastrado. Realize o cadastro para continuar.")
    return _resposta_sessao(cliente)


@router.get("/me")
def minha_sessao(cpf_sessao: str = Depends(_cpf_da_sessao)):
    cliente = _cliente_por_cpf(cpf_sessao)
    return _resposta_sessao(cliente)


@router.post("/cadastro", status_code=201)
def cadastro_cliente_e_conta(payload: CadastroClienteConta):
    state = _get_state()
    cpf = _cpf_digitos(payload.cpf)
    if len(cpf) != 11:
        raise HTTPException(400, "CPF inválido. Informe 11 dígitos.")
    if filtrar_cliente(cpf, state.clientes):
        raise HTTPException(409, "CPF já cadastrado. Faça login com seu CPF.")

    cliente = PessoaFisica(
        nome=payload.nome.strip(),
        cpf=cpf,
        data_nascimento=payload.data_nascimento.strip(),
        endereco=payload.endereco.strip(),
    )
    state.clientes.append(cliente)
    state.db.salvar_cliente(
        cpf, cliente.nome, cliente.data_nascimento, cliente.endereco
    )

    numero = state.db.salvar_conta(cpf)
    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero)
    state.contas.append(conta)
    cliente.adicionar_conta(conta)

    resposta = _resposta_sessao(cliente)
    resposta["mensagem"] = "Cadastro e conta criados com sucesso."
    return resposta


@router.post("/contas", status_code=201)
def nova_conta_portal(cpf_sessao: str = Depends(_cpf_da_sessao)):
    state = _get_state()
    cliente = _cliente_por_cpf(cpf_sessao)

    numero = state.db.salvar_conta(cliente.cpf)
    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero)
    state.contas.append(conta)
    cliente.adicionar_conta(conta)

    resposta = _resposta_sessao(cliente)
    resposta["mensagem"] = "Nova conta aberta com sucesso."
    return resposta


@router.post("/depositos")
def depositar_portal(
    payload: TransacaoPortal,
    cpf_sessao: str = Depends(_cpf_da_sessao),
):
    state = _get_state()
    cpf = _exigir_cpf_da_sessao(payload.cpf, cpf_sessao)

    try:
        valor = Decimal(str(payload.valor))
    except InvalidOperation:
        raise HTTPException(400, "Valor inválido.")

    cliente = _cliente_por_cpf(cpf)
    conta = _conta_do_cpf(cliente, payload.numero_conta)
    sucesso = cliente.realizar_transacao(conta, Deposito(valor))

    if not sucesso:
        raise HTTPException(400, "Não foi possível realizar o depósito.")

    state.db.salvar_operacao(conta.numero, "Depósito", valor, conta.saldo)
    resposta = _resposta_sessao(cliente)
    resposta["mensagem"] = "Depósito realizado com sucesso."
    return resposta


@router.post("/saques")
def sacar_portal(
    payload: TransacaoPortal,
    cpf_sessao: str = Depends(_cpf_da_sessao),
):
    state = _get_state()
    cpf = _exigir_cpf_da_sessao(payload.cpf, cpf_sessao)

    try:
        valor = Decimal(str(payload.valor))
    except InvalidOperation:
        raise HTTPException(400, "Valor inválido.")

    cliente = _cliente_por_cpf(cpf)
    conta = _conta_do_cpf(cliente, payload.numero_conta)
    sucesso = cliente.realizar_transacao(conta, Saque(valor))

    if not sucesso:
        raise HTTPException(
            400,
            "Não foi possível realizar o saque. Verifique saldo, limite de R$ 500 "
            "por saque e o máximo de 3 saques por dia.",
        )

    state.db.salvar_operacao(conta.numero, "Saque", valor, conta.saldo)
    resposta = _resposta_sessao(cliente)
    resposta["mensagem"] = "Saque realizado com sucesso."
    return resposta


@router.get("/extrato")
def extrato_portal(
    numero_conta: int,
    cpf_sessao: str = Depends(_cpf_da_sessao),
):
    cliente = _cliente_por_cpf(cpf_sessao)
    conta = _conta_do_cpf(cliente, numero_conta)
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
        "cpf_formatado": formatar_cpf(cliente.cpf),
        "conta": conta.numero,
        "agencia": conta.agencia,
        "saldo": float(conta.saldo),
        "transacoes": transacoes,
        "transacoes_hoje": realizadas,
        "limite_transacoes_dia": PessoaFisica.LIMITE_TRANSACOES_DIARIAS,
    }
