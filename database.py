import os
import time
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

class Database:
    def __init__(self):
        self.host     = os.getenv("DB_HOST")
        self.database = os.getenv("DB_NAME")
        self.user     = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.port     = os.getenv("DB_PORT", "5432")

        missing = [v for v in ("DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD") if not os.getenv(v)]
        if missing:
            raise ValueError(f"Variáveis de ambiente faltando: {', '.join(missing)}")

        self._conectar()
        self._criar_tabelas()

    def _conectar(self, tentativas=3, espera=2):
        """Abre a conexão com o banco, com retentativas em caso de falha

        Tenta conectar até `tentativas` vezes antes de desistir,
        aguardando `espera` segundos entre cada tentativa
        """
        for i in range(1, tentativas + 1):
            try:
                self.conn = psycopg2.connect(
                    host=self.host,
                    database=self.database,
                    user=self.user,
                    password=self.password,
                    port=self.port
                )
                self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
                return  # conexão ok, sai do loop
            except Exception as e:
                print(f"\nTentativa {i}/{tentativas} falhou: {e}")
                if i < tentativas:
                    time.sleep(espera)
        raise ConnectionError("Não foi possível conectar ao banco de dados")

    def _reconectar(self):
        """Fecha a conexão atual e reabre

        Chamado automaticamente quando um execute() falha por
        conexão perdida (OperationalError)
        """
        try:
            self.cursor.close()
            self.conn.close()
        except Exception:
            pass  # ignora erros ao fechar conexão já quebrada
        self._conectar()

    def _executar(self, comando, params=None):
        """Executa um comando SQL com reconexão automática em caso de queda

        Em OperationalError (conexão perdida), tenta reconectar uma vez
        e reexecuta. Qualquer outro erro é relançado para o chamador tratar
        """
        try:
            self.cursor.execute(comando, params)
        except psycopg2.OperationalError:
            print("\nConexão perdida. Reconectando...")
            self._reconectar()
            self.cursor.execute(comando, params)  # segunda tentativa

    def _criar_tabelas(self):
        try:
            self._executar("""
                CREATE TABLE IF NOT EXISTS clientes (
                    cpf             VARCHAR(14) PRIMARY KEY,
                    nome            VARCHAR(100) NOT NULL,
                    data_nascimento VARCHAR(10) NOT NULL,
                    endereco        TEXT NOT NULL
                );
            """)
            self._executar("""
                CREATE TABLE IF NOT EXISTS contas (
                    numero        SERIAL PRIMARY KEY,
                    agencia       VARCHAR(10) DEFAULT '0001',
                    cpf_cliente   VARCHAR(14) NOT NULL,
                    saldo         NUMERIC(15, 2) DEFAULT 0.00,
                    limite        NUMERIC(15, 2) DEFAULT 500.00,
                    limite_saques INTEGER DEFAULT 3,
                    FOREIGN KEY (cpf_cliente) REFERENCES clientes(cpf)
                );
            """)
            self._executar("""
                CREATE TABLE IF NOT EXISTS transacoes (
                    id           SERIAL PRIMARY KEY,
                    numero_conta INTEGER NOT NULL,
                    tipo         VARCHAR(20) NOT NULL,
                    valor        NUMERIC(15, 2) NOT NULL,
                    data         VARCHAR(20) NOT NULL,
                    FOREIGN KEY (numero_conta) REFERENCES contas(numero)
                );
            """)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"Erro ao criar tabelas: {e}")

    ## Clientes

    def salvar_cliente(self, cpf, nome, data_nascimento, endereco):
        try:
            self._executar(
                "INSERT INTO clientes (cpf, nome, data_nascimento, endereco) VALUES (%s, %s, %s, %s);",
                (cpf, nome, data_nascimento, endereco)
            )
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"Erro ao salvar cliente: {e}")

    def buscar_cliente(self, cpf):
        self._executar("SELECT * FROM clientes WHERE cpf = %s;", (cpf,))
        return self.cursor.fetchone()

    def listar_clientes(self):
        self._executar("SELECT * FROM clientes;")
        return self.cursor.fetchall()

    def excluir_cliente(self, cpf):
        """Remove cliente e todas as suas contas e transações em cascata.

        Operação multi-step — o rollback garante que não fique
        cliente sem contas ou contas sem transações em caso de falha.
        """
        try:
            self._executar("SELECT numero FROM contas WHERE cpf_cliente = %s;", (cpf,))
            contas = self.cursor.fetchall()

            for conta in contas:
                self._executar("DELETE FROM transacoes WHERE numero_conta = %s;", (conta["numero"],))

            self._executar("DELETE FROM contas WHERE cpf_cliente = %s;", (cpf,))
            self._executar("DELETE FROM clientes WHERE cpf = %s;", (cpf,))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"Erro ao excluir cliente: {e}")

    ## Contas

    def salvar_conta(self, cpf_cliente):
        try:
            self._executar(
                "INSERT INTO contas (cpf_cliente) VALUES (%s) RETURNING numero;",
                (cpf_cliente,)
            )
            resultado = self.cursor.fetchone()
            self.conn.commit()
            return resultado["numero"]
        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"Erro ao salvar conta: {e}")

    def buscar_contas_do_cliente(self, cpf):
        self._executar("SELECT * FROM contas WHERE cpf_cliente = %s;", (cpf,))
        return self.cursor.fetchall()

    def listar_contas(self):
        self._executar("""
            SELECT c.numero, c.agencia, c.saldo, cl.nome, cl.cpf
            FROM contas c
            JOIN clientes cl ON c.cpf_cliente = cl.cpf
        """)
        return self.cursor.fetchall()

    def atualizar_saldo(self, numero_conta, novo_saldo):
        try:
            self._executar(
                "UPDATE contas SET saldo = %s WHERE numero = %s;",
                (novo_saldo, numero_conta)
            )
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"Erro ao atualizar saldo: {e}")

    def excluir_conta(self, numero_conta):
        try:
            self._executar("DELETE FROM transacoes WHERE numero_conta = %s;", (numero_conta,))
            self._executar("DELETE FROM contas WHERE numero = %s;", (numero_conta,))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"Erro ao excluir conta: {e}")

    ## Transações

    def salvar_transacao(self, numero_conta, tipo, valor):
        try:
            data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            self._executar(
                "INSERT INTO transacoes (numero_conta, tipo, valor, data) VALUES (%s, %s, %s, %s);",
                (numero_conta, tipo, valor, data)
            )
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"Erro ao salvar transação: {e}")

    def buscar_transacoes(self, numero_conta):
        self._executar(
            "SELECT * FROM transacoes WHERE numero_conta = %s ORDER BY id;",
            (numero_conta,)
        )
        return self.cursor.fetchall()

    def fechar(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()