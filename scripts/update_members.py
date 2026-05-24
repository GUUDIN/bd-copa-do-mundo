#!/usr/bin/env python3
"""
Lê 08.Instrucoes.txt, extrai os membros do grupo na ordem em que aparecem
e atualiza a tabela de membros no README.md.

Mapeamento fixo de responsabilidades (aluno 1 → parte 1, etc.):
  1 → DER + Modelo Relacional
  2 → DDL + DML + Triggers
  3 → Implementação do Protótipo
  4 → Execução + Demonstração
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TXT  = ROOT / "08.Instrucoes.txt"
README = ROOT / "README.md"

RESPONSIBILITIES = [
    "DER + Modelo Relacional",
    "DDL + DML + Triggers",
    "Implementação do Protótipo",
    "Execução + Demonstração",
]


def parse_members(path: Path) -> list[tuple[str, str]]:
    """Retorna lista de (nome, nusp) na ordem do arquivo."""
    text = path.read_text(encoding="utf-8")
    # Captura o bloco entre 'MEMBROS DO GRUPO:' e a próxima seção em maiúsculas
    m = re.search(r"MEMBROS DO GRUPO:(.*?)(?:\n[A-ZÁÉÍÓÚÂÊÔÃÕÇ]{2,}|\Z)", text, re.DOTALL)
    if not m:
        print("⚠️  Seção 'MEMBROS DO GRUPO:' não encontrada no .txt", file=sys.stderr)
        return []

    members = []
    for line in m.group(1).splitlines():
        # Formato: - [Nome Completo] – NUSP_ou_número
        match = re.match(r"\s*[-•]\s*\[(.+?)\]\s*[–\-]\s*(.+)", line)
        if not match:
            continue
        name = match.group(1).strip()
        nusp = match.group(2).strip()
        # Placheholder ainda não preenchido
        if nusp.upper() in ("NUSP", "—", "-", ""):
            nusp = "—"
        members.append((name, nusp))
    return members


def update_readme(members: list[tuple[str, str]]) -> None:
    content = README.read_text(encoding="utf-8")

    # Constrói nova tabela
    header = (
        "| Nome | Nº USP | Responsabilidade na apresentação |\n"
        "|------|--------|----------------------------------|"
    )
    rows = []
    for i, (name, nusp) in enumerate(members[:4]):
        resp = RESPONSIBILITIES[i] if i < len(RESPONSIBILITIES) else "—"
        rows.append(f"| {name} | {nusp} | {resp} |")

    new_block = "\n".join([header] + rows)

    # Substitui o bloco entre os marcadores
    pattern = r"(<!-- MEMBROS_START -->).*?(<!-- MEMBROS_END -->)"
    replacement = rf"\1\n{new_block}\n\2"
    updated, n = re.subn(pattern, replacement, content, flags=re.DOTALL)

    if n == 0:
        print("⚠️  Marcadores <!-- MEMBROS_START/END --> não encontrados no README.", file=sys.stderr)
        sys.exit(1)

    README.write_text(updated, encoding="utf-8")
    print(f"✅  README atualizado com {len(rows)} membro(s).")
    for i, (name, nusp) in enumerate(members[:4], 1):
        print(f"   {i}. {name} ({nusp}) → {RESPONSIBILITIES[i-1]}")


if __name__ == "__main__":
    members = parse_members(TXT)
    if not members:
        print("Nenhum membro encontrado. Verifique o formato do 08.Instrucoes.txt.")
        sys.exit(1)
    update_readme(members)
