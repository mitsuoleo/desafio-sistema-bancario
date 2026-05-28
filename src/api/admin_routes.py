import hmac

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from src.api.auth import ADMIN_SENHA, ADMIN_TOKEN, ADMIN_USUARIO
from src.models.cliente import PessoaFisica
from src.utils import filtrar_cliente, formatar_cpf, formatar_data

router = APIRouter(prefix="/api/admin", tags=["Painel Administrativo"])


class AdminLogin(BaseModel):
    usuario: str
    senha: str


def _get_state():
    from src.api.server import state

    return state


def verificar_admin(x_admin_token: str = Header(..., alias="X-Admin-Token")):
    if not hmac.compare_digest(x_admin_token, ADMIN_TOKEN):
        raise HTTPException(401, "Acesso não autorizado. Faça login como administrador.")


def _serializar_conta_admin(conta):
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
        "numero": conta.numero,
        "agencia": conta.agencia,
        "saldo": float(conta.saldo),
        "limite_saque": float(conta._limite),
        "limite_saques_dia": conta._limite_saques,
        "transacoes_hoje": realizadas,
        "limite_transacoes_dia": PessoaFisica.LIMITE_TRANSACOES_DIARIAS,
        "transacoes": transacoes,
    }


@router.post("/login")
def admin_login(payload: AdminLogin):
    usuario_ok = hmac.compare_digest(payload.usuario, ADMIN_USUARIO)
    senha_ok = hmac.compare_digest(payload.senha, ADMIN_SENHA)
    if not (usuario_ok and senha_ok):
        raise HTTPException(401, "Usuário ou senha incorretos.")
    return {
        "token": ADMIN_TOKEN,
        "usuario": ADMIN_USUARIO,
        "mensagem": "Login realizado com sucesso.",
    }


@router.get("/resumo", dependencies=[Depends(verificar_admin)])
def resumo_geral():
    state = _get_state()
    contas_resumo = []
    for conta in state.contas:
        contas_resumo.append({
            "numero": conta.numero,
            "agencia": conta.agencia,
            "saldo": float(conta.saldo),
            "titular": conta.cliente.nome,
            "cpf_formatado": formatar_cpf(conta.cliente.cpf),
            "transacoes_hoje": len(conta.historico.transacoes_do_dia),
        })

    return {
        "total_clientes": len(state.clientes),
        "total_contas": len(state.contas),
        "saldo_total": sum(float(c.saldo) for c in state.contas),
        "contas": contas_resumo,
    }


@router.get("/clientes/{cpf}", dependencies=[Depends(verificar_admin)])
def detalhes_cliente(cpf: str):
    cpf_digitos = "".join(filter(str.isdigit, cpf))
    if len(cpf_digitos) != 11:
        raise HTTPException(400, "CPF inválido.")

    cliente = filtrar_cliente(cpf_digitos, _get_state().clientes)
    if not cliente:
        raise HTTPException(404, "Cliente não encontrado.")

    return {
        "nome": cliente.nome,
        "cpf": cliente.cpf,
        "cpf_formatado": formatar_cpf(cliente.cpf),
        "data_nascimento": formatar_data(cliente.data_nascimento),
        "endereco": cliente.endereco,
        "contas": [_serializar_conta_admin(c) for c in cliente.contas],
    }


@router.delete("/clientes/{cpf}", dependencies=[Depends(verificar_admin)])
def admin_excluir_cliente(cpf: str):
    state = _get_state()
    cpf_digitos = "".join(filter(str.isdigit, cpf))
    cliente = filtrar_cliente(cpf_digitos, state.clientes)
    if not cliente:
        raise HTTPException(404, "Cliente não encontrado.")

    # Remove all client's accounts from the global list
    for conta in list(cliente.contas):
        if conta in state.contas:
            state.contas.remove(conta)

    state.db.excluir_cliente(cliente.cpf)
    state.clientes.remove(cliente)
    return {"mensagem": f"Cliente {cliente.nome} e suas contas foram excluídos com sucesso."}


@router.delete("/contas/{numero}", dependencies=[Depends(verificar_admin)])
def admin_excluir_conta(numero: int):
    state = _get_state()
    
    # Find the account in global state
    conta = next((c for c in state.contas if c.numero == numero), None)
    if not conta:
        raise HTTPException(404, "Conta não encontrada.")

    cliente = conta.cliente
    state.db.excluir_conta(numero)
    state.contas.remove(conta)
    if conta in cliente.contas:
        cliente.contas.remove(conta)
        
    return {"mensagem": f"Conta nº {numero} excluída com sucesso."}

