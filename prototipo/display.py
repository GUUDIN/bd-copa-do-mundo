"""Formatação e paginação de resultados no terminal."""
from tabulate import tabulate

PAGINA = 50


def exibir_resultado(colunas, linhas):
    """Exibe linhas como tabela, paginando a cada 50 registros."""
    total = len(linhas)
    if total == 0:
        print("\nNenhum resultado encontrado.")
        return

    inicio = 0
    while inicio < total:
        fim = min(inicio + PAGINA, total)
        bloco = linhas[inicio:fim]
        print()
        print(tabulate(bloco, headers=colunas, tablefmt="grid", showindex=False))
        print(f"\nMostrando {inicio + 1}-{fim} de {total} linha(s).")
        inicio = fim
        if inicio < total:
            try:
                input("Pressione ENTER para continuar (ou Ctrl+C para interromper)...")
            except KeyboardInterrupt:
                print("\nPaginação interrompida.")
                break

    print(f"\nTotal de linhas retornadas: {total}")
