import psycopg2


class Database:
    def __init__(self):
        self.conn = None

    def conectar(self, host, port, database, user, password):
        self.conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
        )

    def executar(self, query, params=None):
        if self.conn is None:
            raise RuntimeError("Conexão não estabelecida.")
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params or ())
                if cur.description is None:
                    self.conn.commit()
                    return [], []
                colunas = [desc[0] for desc in cur.description]
                linhas = cur.fetchall()
                self.conn.commit()
                return colunas, linhas
        except psycopg2.Error:
            try:
                self.conn.rollback()
            except Exception:
                pass
            raise

    def fechar(self):
        if self.conn is not None:
            try:
                self.conn.close()
            except Exception:
                pass
            self.conn = None
