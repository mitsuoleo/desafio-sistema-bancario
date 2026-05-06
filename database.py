import sqlite3
from datetime import datetime

class Database:
    def __init__(self, caminho="banco_sistema.db"):
        self.conn = sqlite3.connect(caminho)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._criar_tabelas()

    def _criar_tabelas(self):
        self.conn.execute("""
         CREATE TABLE IF NOT EXISTS clientes (
            cpf             TEXT PRIMARY KEY,
            nome            TEXT NOT NULL,
            data_nascimento TEXT NOT NULL,
            endereco        TEXT NOT NULL
        )
    """)
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS contas (
            numero        INTEGER PRIMARY KEY AUTOINCREMENT,
            agencia       TEXT    DEFAULT '0001',
            cpf_cliente   TEXT    NOT NULL,
            saldo         REAL    DEFAULT 0,
            limite        REAL    DEFAULT 500,
            limite_saques INTEGER DEFAULT 3,
            FOREIGN KEY (cpf_cliente) REFERENCES clientes(cpf)
        )
    """)
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS transacoes (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_conta INTEGER NOT NULL,
            tipo         TEXT    NOT NULL,
            valor        REAL    NOT NULL,
            data         TEXT    NOT NULL,
            FOREIGN KEY (numero_conta) REFERENCES contas(numero)
        )
    """)
        self.conn.commit()

        ## Clientes

    def salvar_cliente(self, cpf, nome, data_nascimento, endereco):
            self.conn.execute("""
                INSERT INTO clientes VALUES (?, ?, ?, ?)
            """, (cpf, nome, data_nascimento, endereco))
            self.conn.commit()

    def buscar_cliente(self, cpf):
            return self.conn.execute(
                "SELECT * FROM clientes WHERE cpf = ?", (cpf,)
            ).fetchone()
        
    def listar_clientes(self):
            return self.conn.execute("SELECT * FROM clientes").fetchall()
    
    def excluir_cliente(self, cpf):
        contas = self.conn.execute(
            "SELECT numero FROM contas WHERE cpf_cliente = ?", (cpf,)
        ).fetchall()

        for conta in contas:
            self.conn.execute(
                "DELETE FROM transacoes WHERE numero_conta = ?", (conta["numero"],)
            )

        self.conn.execute("DELETE FROM contas WHERE cpf_cliente = ?", (cpf,))
        self.conn.execute("DELETE FROM clientes WHERE cpf = ?", (cpf,))
        self.conn.commit()
        
    ## Contas
        
    def salvar_conta(self, cpf_cliente):
            cursor = self.conn.execute(
                "INSERT INTO contas (cpf_cliente) VALUES (?)", (cpf_cliente,)
            )
            self.conn.commit()
            return cursor.lastrowid
        
    def buscar_contas_do_cliente(self, cpf):
            return self.conn.execute(
                "SELECT * FROM contas WHERE cpf_cliente = ?", (cpf,)
            ).fetchall()
        
    def listar_contas(self):
            return self.conn.execute("""
                SELECT c.numero, c.agencia, c.saldo, cl.nome, cl.cpf 
                FROM contas c
                JOIN clientes cl ON c.cpf_cliente = cl.cpf
            """).fetchall()
        
    def atualizar_saldo(self, numero_conta, novo_saldo):
            self.conn.execute(
                "UPDATE contas SET saldo = ? WHERE numero = ?", (novo_saldo, numero_conta)
            )
            self.conn.commit()

    def excluir_conta(self, numero_conta):
            self.conn.execute(
                "DELETE FROM transacoes WHERE numero_conta = ?", (numero_conta,)
            )
            self.conn.execute(
                "DELETE FROM contas WHERE numero = ?", (numero_conta,)
            )
            self.conn.commit()


## Transações

    def salvar_transacao(self, numero_conta, tipo, valor):
        data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.conn.execute("""
        INSERT INTO transacoes (numero_conta, tipo, valor, data) 
        VALUES (?, ?, ?, ?)
        """, (numero_conta, tipo, valor, data))
        self.conn.commit()

    def buscar_transacoes(self, numero_conta):
        return self.conn.execute(
        "SELECT * FROM transacoes WHERE numero_conta = ? ORDER BY id", (numero_conta,)
    ).fetchall()

    def contar_transacoes_hoje(self, numero_conta):
        hoje = datetime.now().strftime("%d/%m/%Y")
        return self.conn.execute("""
        SELECT COUNT(*) FROM transacoes 
        WHERE numero_conta = ? AND data LIKE ?""", (numero_conta, f"{hoje}%")
        ).fetchone()[0]

    def fechar(self):
        self.conn.close()