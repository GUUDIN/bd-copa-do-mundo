"""Ponto de entrada do protótipo CLI do sistema de Copas do Mundo da FIFA."""
import sys
import getpass

import psycopg2

from db import Database
from display import exibir_resultado
import queries
import ollama_client


# ============================================================
# Login e inicialização
# ============================================================

def fazer_login():
    """Solicita credenciais e retorna uma instância de Database conectada."""
    print("=" * 60)
    print("  SISTEMA DE COPAS DO MUNDO DA FIFA - PROTÓTIPO CLI")
    print("=" * 60)
    print("\nConexão ao PostgreSQL")
    print("-" * 60)

    while True:
        try:
            host = input("Host [localhost]: ").strip() or "localhost"
            port = input("Porta [5432]: ").strip() or "5432"
            database = input("Banco [copa_mundo]: ").strip() or "copa_mundo"
            user = input("Usuário: ").strip()
            if not user:
                print("Usuário é obrigatório.")
                continue
            password = getpass.getpass("Senha: ")

            db = Database()
            db.conectar(host, port, database, user, password)
            print(f"\n[OK] Conectado a {database}@{host}:{port} como {user}.")
            return db
        except psycopg2.Error as e:
            print(f"\n[ERRO] Falha ao conectar: {e}")
            tentar = input("Tentar novamente? [s/N]: ").strip().lower()
            if tentar != "s":
                sys.exit(1)
        except KeyboardInterrupt:
            print("\nOperação cancelada pelo usuário.")
            sys.exit(0)


# ============================================================
# Helpers de input
# ============================================================

def ler_int(msg):
    """Lê um inteiro do usuário, com tratamento de erro."""
    while True:
        try:
            valor = input(msg).strip()
            return int(valor)
        except ValueError:
            print("Entrada inválida. Digite um número inteiro.")


def ler_str(msg):
    """Lê uma string não-vazia do usuário."""
    while True:
        valor = input(msg).strip()
        if valor:
            return valor
        print("Entrada vazia. Tente novamente.")


# ============================================================
# Execução de queries
# ============================================================

def executar_e_exibir(db, sql, params=()):
    """Executa uma query no banco e exibe o resultado."""
    try:
        colunas, linhas = db.executar(sql, params)
        exibir_resultado(colunas, linhas)
    except psycopg2.Error as e:
        print(f"\n[ERRO SQL] {e}")


# ============================================================
# Menu
# ============================================================

MENU = """
============================================================
                    MENU PRINCIPAL
============================================================
 0. Sair
 1. Listar edições da Copa do Mundo
 2. Listar seleções de uma edição
 3. Grupos e seleções de uma edição
 4. Tabela de classificação de um grupo
 5. Partidas de uma edição
 6. Caminho do mata-mata
 7. Elenco de uma seleção em uma edição
 8. Eventos de uma partida
 9. Artilheiros de uma edição
10. Histórico de uma seleção
11. [IA] Consulta em linguagem natural -> SQL via Ollama
12. [IA] Digitar SQL diretamente
============================================================
"""


def menu_principal(db):
    """Loop do menu principal."""
    while True:
        print(MENU)
        try:
            opcao = input("Escolha uma opção: ").strip()
        except KeyboardInterrupt:
            print("\nEncerrando...")
            break

        try:
            if opcao == "0":
                print("Encerrando o sistema. Até logo!")
                break

            elif opcao == "1":
                sql, params = queries.q1_edicoes()
                executar_e_exibir(db, sql, params)

            elif opcao == "2":
                ano = ler_int("Ano da edição: ")
                sql, params = queries.q2_selecoes_edicao(ano)
                executar_e_exibir(db, sql, params)

            elif opcao == "3":
                ano = ler_int("Ano da edição: ")
                sql, params = queries.q3_grupos_edicao(ano)
                executar_e_exibir(db, sql, params)

            elif opcao == "4":
                ano = ler_int("Ano da edição: ")
                letra = ler_str("Letra do grupo (A, B, C...): ")
                sql, params = queries.q4_classificacao_grupo(ano, letra)
                executar_e_exibir(db, sql, params)

            elif opcao == "5":
                ano = ler_int("Ano da edição: ")
                sql, params = queries.q5_partidas_edicao(ano)
                executar_e_exibir(db, sql, params)

            elif opcao == "6":
                ano = ler_int("Ano da edição: ")
                sql, params = queries.q6_mata_mata(ano)
                executar_e_exibir(db, sql, params)

            elif opcao == "7":
                sigla = ler_str("Sigla do país (ex.: BRA): ")
                ano = ler_int("Ano da edição: ")
                sql, params = queries.q7_elenco(sigla, ano)
                executar_e_exibir(db, sql, params)

            elif opcao == "8":
                id_partida = ler_int("ID da partida: ")
                sql, params = queries.q8_eventos_partida(id_partida)
                executar_e_exibir(db, sql, params)

            elif opcao == "9":
                ano = ler_int("Ano da edição: ")
                sql, params = queries.q9_artilheiros(ano)
                executar_e_exibir(db, sql, params)

            elif opcao == "10":
                sigla = ler_str("Sigla do país (ex.: BRA): ")
                sql, params = queries.q10_historico_selecao(sigla)
                executar_e_exibir(db, sql, params)

            elif opcao == "11":
                consulta_ia(db)

            elif opcao == "12":
                consulta_sql_livre(db)

            else:
                print("Opção inválida. Tente novamente.")

        except KeyboardInterrupt:
            print("\n[Operação interrompida pelo usuário]")
            continue
        except Exception as e:
            print(f"\n[ERRO inesperado] {type(e).__name__}: {e}")


# ============================================================
# Modos com IA / SQL livre
# ============================================================

def consulta_ia(db):
    """Pergunta em linguagem natural, gera SQL via Ollama e executa."""
    try:
        pergunta = ler_str("Digite sua pergunta em linguagem natural: ")
    except KeyboardInterrupt:
        return

    print("\n[INFO] Consultando Ollama...")
    try:
        sql_gerado = ollama_client.gerar_sql(pergunta)
    except ConnectionError as e:
        print(f"\n[ERRO Ollama] {e}")
        return
    except Exception as e:
        print(f"\n[ERRO inesperado ao chamar Ollama] {e}")
        return

    print("\n--- SQL gerado ---")
    print(sql_gerado)
    print("------------------")

    confirma = input("\nExecutar este SQL? [S/n]: ").strip().lower()
    if confirma == "n":
        print("Execução cancelada.")
        return

    try:
        colunas, linhas = db.executar(sql_gerado)
        exibir_resultado(colunas, linhas)
    except psycopg2.Error as e:
        print(f"\n[ERRO SQL] O SQL gerado é inválido ou inseguro:")
        print(f"   {e}")


def consulta_sql_livre(db):
    """Permite ao usuário digitar SQL diretamente."""
    print("\nDigite o SQL (linha em branco para confirmar):")
    linhas_sql = []
    try:
        while True:
            linha = input("> ")
            if linha.strip() == "":
                break
            linhas_sql.append(linha)
    except KeyboardInterrupt:
        print("\nOperação cancelada.")
        return

    sql_texto = "\n".join(linhas_sql).strip()
    if not sql_texto:
        print("Nenhum SQL fornecido.")
        return

    try:
        colunas, linhas = db.executar(sql_texto)
        exibir_resultado(colunas, linhas)
    except psycopg2.Error as e:
        print(f"\n[ERRO SQL] {e}")


# ============================================================
# Main
# ============================================================

def main():
    db = None
    try:
        db = fazer_login()
        menu_principal(db)
    except KeyboardInterrupt:
        print("\n\nEncerrando graciosamente (Ctrl+C).")
    finally:
        if db is not None:
            db.fechar()
            print("Conexão encerrada.")


if __name__ == "__main__":
    main()
