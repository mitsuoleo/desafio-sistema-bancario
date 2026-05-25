# Sistema Bancário

Sistema bancário simples desenvolvido em Python como desafio da Trilha Python da Suzano na plataforma [DIO](https://www.dio.me/), com operações básicas de conta corrente via terminal.

## Funcionalidades

- Depositar
- Sacar (limite de R$ 500,00 por saque e 3 saques por dia)
- Visualizar extrato
- Cadastrar usuários
- Criar contas bancárias vinculadas a usuários
- Listar usuários e contas cadastradas

## Regras de negócio

- Limite de 10 transações diárias por conta
- Limite de 3 saques diários
- Limite de R$ 500,00 por operação de saque

## Como executar

Pré-requisito: Python 3.x instalado.

```bash
python desafio.py
```

### Variáveis de ambiente

Copie o arquivo de exemplo e preencha com suas configurações:

```bash
cp .env.example .env
```

As variáveis necessárias estão documentadas no `.env.example`.

### Com Docker

```bash
docker build -t sistema-bancario .
docker run --env-file .env sistema-bancario
```

> O container executa com usuário não-root (`appuser`) por padrão.

## Linguagens e Ferramentas Utilizadas

![Static Badge](https://img.shields.io/badge/Python-Python?style=plastic&logo=Python&logoSize=auto&labelColor=yellow&color=white)
![Static Badge](https://img.shields.io/badge/Git-Git?style=plastic&logo=Git&logoColor=white&logoSize=auto&labelColor=blue&color=white)
![Static Badge](https://img.shields.io/badge/GitHub-GitHub?style=plastic&logo=GitHub&logoColor=white&logoSize=auto&labelColor=grey&color=white)
![Static Badge](https://img.shields.io/badge/Docker-Docker?style=plastic&logo=Docker&logoColor=white&logoSize=auto&labelColor=2496ED&color=white)
![Static Badge](https://img.shields.io/badge/AWS-AWS?style=plastic&logo=amazonwebservices&logoColor=white&logoSize=auto&labelColor=FF9900&color=white)
![Static Badge](https://img.shields.io/badge/PostgreSQL-PostgreSQL?style=plastic&logo=postgresql&logoColor=white&logoSize=auto&labelColor=4169E1&color=white)
