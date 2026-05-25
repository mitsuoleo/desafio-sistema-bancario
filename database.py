import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

class Database:
    def __init__(self):
        self.host = os.getenv("DB_HOST")
        self.database = os.getenv("DB_NAME")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.port = os.getenv("DB_PORT", "5432")

        if not self.password:
            raise ValueError("A senha do banco de dados não foi fornecida "
                "Por favor, defina a variável de ambiente DB_PASSWORD no seu arquivo .env")
        
        self._conectar()
        self._criar_tabelas()

    def _conectar(self):
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
        
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        except Exception as e:
            print(f"\nErro crítico ao conectar no banco da AWS: {e}")
            raise e

    def _criar_tabelas(self):
        
        tabela_clientes = """
        CREATE TABLE IF NOT EXISTS clientes (
            cpf             VARCHAR(14) PRIMARY KEY,
            nome            VARCHAR(100) NOT NULL,
            data_nascimento VARCHAR(10) NOT NULL,
            endereco        TEXT NOT NULL
        );
        """
        
        tabela_contas = """
        CREATE TABLE IF NOT EXISTS contas (
            numero        SERIAL PRIMARY KEY,
            agencia       VARCHAR(10) DEFAULT '0001',
            cpf_cliente   VARCHAR(14) NOT NULL,
            saldo         NUMERIC(15, 2) DEFAULT 0.00,
            limite        NUMERIC(15, 2) DEFAULT 500.00,
            limite_saques INTEGER DEFAULT 3,
            FOREIGN KEY (cpf_cliente) REFERENCES clientes(cpf)
        );
        """
        
        tabela_transacoes = """
        CREATE TABLE IF NOT EXISTS transacoes (
            id           SERIAL PRIMARY KEY,
            numero_conta INTEGER NOT NULL,
            tipo         VARCHAR(20) NOT NULL,
            valor        NUMERIC(15, 2) NOT NULL,
            data         VARCHAR(20) NOT NULL,
            FOREIGN KEY (numero_conta) REFERENCES contas(numero)
        );
        """
        
        self.cursor.execute(tabela_clientes)
        self.cursor.execute(tabela_contas)
        self.cursor.execute(tabela_transacoes)
        self.conn.commit()

    ## Clientes

    def salvar_cliente(self, cpf, nome, data_nascimento, endereco):
        comando = "INSERT INTO clientes (cpf, nome, data_nascimento, endereco) VALUES (%s, %s, %s, %s);"
        self.cursor.execute(comando, (cpf, nome, data_nascimento, endereco))
        self.conn.commit()

    def buscar_cliente(self, cpf):
        comando = "SELECT * FROM clientes WHERE cpf = %s;"
        self.cursor.execute(comando, (cpf,))
        return self.cursor.fetchone()
        
    def listar_clientes(self):
        self.cursor.execute("SELECT * FROM clientes;")
        return self.cursor.fetchall()
    
    def excluir_cliente(self, cpf):
        # Busca todas as contas do cliente
        self.cursor.execute("SELECT numero FROM contas WHERE cpf_cliente = %s;", (cpf,))
        contas = self.cursor.fetchall()

        # Remove as transações de cada conta antes
        for conta in contas:
            self.cursor.execute("DELETE FROM transacoes WHERE numero_conta = %s;", (conta["numero"],))

        self.cursor.execute("DELETE FROM contas WHERE cpf_cliente = %s;", (cpf,))
        self.cursor.execute("DELETE FROM clientes WHERE cpf = %s;", (cpf,))
        self.conn.commit()
        
    ## Contas
        
    def salvar_conta(self, cpf_cliente):
        comando = "INSERT INTO contas (cpf_cliente) VALUES (%s) RETURNING numero;"
        self.cursor.execute(comando, (cpf_cliente,))
        resultado = self.cursor.fetchone()
        self.conn.commit()
        return resultado["numero"]
        
    def buscar_contas_do_cliente(self, cpf):
        comando = "SELECT * FROM contas WHERE cpf_cliente = %s;"
        self.cursor.execute(comando, (cpf,))
        return self.cursor.fetchall()
        
    def listar_contas(self):
        comando = """
            SELECT c.numero, c.agencia, c.saldo, cl.nome, cl.cpf 
            FROM contas c
            JOIN clientes cl ON c.cpf_cliente = cl.cpf
        """
        self.cursor.execute(comando)
        return self.cursor.fetchall()
        
    def atualizar_saldo(self, numero_conta, novo_saldo):
        comando = "UPDATE contas SET saldo = %s WHERE numero = %s;"
        self.cursor.execute(comando, (novo_saldo, numero_conta))
        self.conn.commit()

    def excluir_conta(self, numero_conta):
        self.cursor.execute("DELETE FROM transacoes WHERE numero_conta = %s;", (numero_conta,))
        self.cursor.execute("DELETE FROM contas WHERE numero = %s;", (numero_conta,))
        self.conn.commit()

    ## Transações

    def salvar_transacao(self, numero_conta, tipo, valor):
        data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        comando = """
            INSERT INTO transacoes (numero_conta, tipo, valor, data) 
            VALUES (%s, %s, %s, %s);
        """
        self.cursor.execute(comando, (numero_conta, tipo, valor, data))
        self.conn.commit()

    def buscar_transacoes(self, numero_conta):
        comando = "SELECT * FROM transacoes WHERE numero_conta = %s ORDER BY id;"
        self.cursor.execute(comando, (numero_conta,))
        return self.cursor.fetchall()

    def contar_transacoes_hoje(self, numero_conta):
        hoje = datetime.now().strftime("%d/%m/%Y")
        comando = """
            SELECT COUNT(*) FROM transacoes 
            WHERE numero_conta = %s AND data LIKE %s;
        """
        self.cursor.execute(comando, (numero_conta, f"{hoje}%"))
        resultado = self.cursor.fetchone()
        return list(resultado.values())[0]

    def fechar(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()