"""Módulo de conexão e execução de queries no PostgreSQL."""
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor


class Database:
    """Encapsula a conexão ativa com o banco de dados PostgreSQL."""

    def __init__(self):
        self.conn = None
        self.params = {}

    def conectar(self, host, port, database, user, password):
        """Estabelece conexão com o banco. Lança psycopg2.Error em caso de falha."""
        self.params = {
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "password": password,
        }
        self.conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
        )
        # Define o search_path padrão para o schema do projeto
        with self.conn.cursor() as cur:
            cur.execute("SET search_path TO copa_mundo, public;")
        self.conn.commit()

    def executar(self, query, params=None):
        """Executa uma query e retorna (colunas, linhas).

        Em caso de erro, executa rollback e relança a exceção.
        """
        if self.conn is None:
            raise RuntimeError("Conexão não estabelecida.")
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params or ())
                # Algumas queries (DDL/DML) podem não retornar linhas
                if cur.description is None:
                    self.conn.commit()
                    return [], []
                colunas = [desc[0] for desc in cur.description]
                linhas = cur.fetchall()
                self.conn.commit()
                return colunas, linhas
        except psycopg2.Error:
            # Faz rollback para deixar a transação em estado consistente
            try:
                self.conn.rollback()
            except Exception:
                pass
            raise

    def fechar(self):
        """Encerra a conexão se estiver aberta."""
        if self.conn is not None:
            try:
                self.conn.close()
            except Exception:
                pass
            self.conn = None
