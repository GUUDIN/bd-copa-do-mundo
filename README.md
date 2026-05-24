# 🏆 SCC0640 – Sistema de Copas do Mundo FIFA

> **Projeto de Curso** | SCC0640 Bases de Dados  
> USP / ICMC – Prof. Jose Fernando Rodrigues Junior  
> Entrega: 24/05 · Apresentação: 25, 26/05 e 01/06

---

## 👥 Membros do Grupo

| Nome | Nº USP | Responsabilidade na apresentação |
|------|--------|----------------------------------|
| ...  | ...    | MER + Mapeamento Relacional      |
| ...  | ...    | DDL + DML + Triggers             |
| ...  | ...    | Implementação do Protótipo       |
| ...  | ...    | Execução + Demonstração          |

---

## 🗂️ Estrutura do Repositório

```
bd-copa-do-mundo/
├── diagramas/
│   ├── 01.ER.drawio          ← MER (edite aqui no draw.io)
│   ├── 02.Relacional.drawio  ← Modelo Relacional
│   └── exports/              ← PNGs gerados automaticamente pelo CI (fundo branco)
├── sql/
│   ├── 05.DDL.sql            ← Criação das tabelas + triggers
│   ├── 06.DML.sql            ← Dados de teste
│   └── consultas.sql         ← As 10 consultas requeridas
├── prototipo/                ← Código Python do protótipo
├── .github/workflows/
│   └── export-diagrams.yml   ← CI: drawio → PNG (fundo branco)
└── 08.Instrucoes.txt
```

> **Como atualizar os diagramas:**  
> 1. Abra `diagramas/01.ER.drawio` ou `02.Relacional.drawio` no [draw.io](https://app.diagrams.net)  
> 2. Edite e salve  
> 3. Faça commit + push  
> 4. O GitHub Action exporta automaticamente os PNGs — o README é atualizado 🎉

---

## 📐 Diagramas

### MER (Entidade-Relacionamento)

> 🔄 Atualizado automaticamente via CI quando o `.drawio` é modificado

![MER](diagramas/exports/01.ER.png)

_Caso a imagem não carregue, [abra o diagrama no viewer →](https://viewer.diagrams.net/?tags=%7B%7D&target=blank&highlight=0000ff&edit=https%3A%2F%2Fapp.diagrams.net%2F&layers=1&nav=1#Uhttps%3A%2F%2Fraw.githubusercontent.com%2FSEU_USUARIO%2Fbd-copa-do-mundo%2Fmain%2Fdiagramas%2F01.ER.drawio)_

---

### Modelo Relacional

![Relacional](diagramas/exports/02.Relacional.png)

_Caso a imagem não carregue, [abra no viewer →](https://viewer.diagrams.net/?tags=%7B%7D&target=blank&highlight=0000ff&edit=https%3A%2F%2Fapp.diagrams.net%2F&layers=1&nav=1#Uhttps%3A%2F%2Fraw.githubusercontent.com%2FSEU_USUARIO%2Fbd-copa-do-mundo%2Fmain%2Fdiagramas%2F02.Relacional.drawio)_

---

## 🗄️ Esquema do Banco (Mermaid ERD)

> Gerado a partir do DDL — sempre em sincronia com o código.

```mermaid
erDiagram
    CONFEDERACAO {
        serial      id_confederacao  PK
        varchar     nome_confederacao
    }
    PAIS {
        varchar3    sigla_pais       PK
        varchar     nome_pais
        integer     id_confederacao  FK
    }
    EDICAO_DA_COPA {
        integer     ano              PK
        varchar3    pais_sede
        date        data_inicio
        date        data_fim
        integer     campea           FK  "nullable"
        integer     vice_campeao     FK  "nullable"
        integer     terceiro_colocado FK "nullable"
    }
    CIDADE_SEDE {
        varchar     cidade           PK
        varchar2    estado           PK
    }
    CIDADE_SEDIA_EDICAO {
        varchar     cidade           PK
        varchar2    estado           PK
        integer     ano_edicao       PK
    }
    ESTADIO {
        serial      id_estadio       PK
        varchar     cidade           FK
        varchar2    estado           FK
    }
    FASE {
        varchar50   tipo_de_fase     PK
        integer     ano              PK
    }
    GRUPO {
        char1       letra_grupo      PK
        integer     ano              PK
    }
    TECNICO {
        serial      id_tecnico       PK
        varchar     nome_tecnico
    }
    SELECAO {
        serial      id_selecao       PK
        integer     ano              PK
        char1       letra_grupo      FK
        integer     id_tecnico       FK
        varchar3    sigla_pais       FK
    }
    SELECAO_GRUPO {
        integer     id_selecao       PK
        integer     ano              PK
        char1       letra_grupo      PK
        integer     pontos
        integer     gols_pro
        integer     gols_contra
        integer     saldo_gols       "gerado"
    }
    JOGADOR {
        serial      id_jogador       PK
        varchar     nome_jogador
    }
    CONVOCACAO {
        integer     id_jogador       PK
        integer     ano              PK
        integer     id_selecao       FK
        integer     numero_camisa
        integer     gols_marcados
    }
    PARTIDA {
        serial      id_partida       PK
        varchar50   tipo_de_fase     FK
        integer     ano              FK
        integer     id_estadio       FK
        timestamp   data_hora
        integer     selecao1         FK
        integer     selecao2         FK
        integer     gols_reg_sel1    "nullable"
        integer     gols_reg_sel2    "nullable"
        integer     gols_prorr_sel1  "nullable"
        integer     gols_prorr_sel2  "nullable"
        integer     gols_pen_sel1    "nullable"
        integer     gols_pen_sel2    "nullable"
        integer     id_vencedor      FK "nullable"
    }
    ARBITRO {
        serial      id_arbitro       PK
        varchar     nome_arbitro
    }
    ARBITRAGEM_PARTIDA {
        integer     id_partida       PK
        integer     id_arbitro       PK
        varchar50   funcao
    }
    EVENTO_DE_JOGO {
        serial      id_evento        PK
        integer     id_partida       PK
        integer     id_jogador       FK "nullable"
        varchar50   tipo_evento
        time        tempo
    }

    CONFEDERACAO       ||--o{ PAIS                 : "tem"
    PAIS               ||--o{ SELECAO              : "representa"
    EDICAO_DA_COPA     ||--o{ FASE                 : "tem"
    EDICAO_DA_COPA     ||--o{ GRUPO                : "possui"
    EDICAO_DA_COPA     }o--o{ CIDADE_SEDE          : "sediada em (via CSE)"
    CIDADE_SEDE        ||--o{ CIDADE_SEDIA_EDICAO  : "é sede"
    EDICAO_DA_COPA     ||--o{ CIDADE_SEDIA_EDICAO  : "sediada em"
    CIDADE_SEDE        ||--o{ ESTADIO              : "possui"
    GRUPO              ||--o{ SELECAO              : "classifica"
    TECNICO            ||--o{ SELECAO              : "treina"
    SELECAO            ||--o{ SELECAO_GRUPO        : "tabela do grupo"
    GRUPO              ||--o{ SELECAO_GRUPO        : "tabela do grupo"
    SELECAO            ||--o{ CONVOCACAO           : "convoca"
    JOGADOR            ||--o{ CONVOCACAO           : "é convocado"
    FASE               ||--o{ PARTIDA              : "contém"
    ESTADIO            ||--o{ PARTIDA              : "sedia"
    SELECAO            ||--o{ PARTIDA              : "disputa (sel1/sel2/vencedor)"
    PARTIDA            ||--o{ ARBITRAGEM_PARTIDA   : "tem árbitros"
    ARBITRO            ||--o{ ARBITRAGEM_PARTIDA   : "arbitra"
    PARTIDA            ||--o{ EVENTO_DE_JOGO       : "tem eventos"
    JOGADOR            |o--o{ EVENTO_DE_JOGO       : "realiza"
    SELECAO            |o--o| EDICAO_DA_COPA       : "campeã/vice/terceiro"
```

---

## ⚙️ Triggers implementadas

| # | Trigger | Tabela | Evento | Regra de negócio |
|---|---------|--------|--------|-----------------|
| 1 | `trg_limite_convocacao` | `convocacao` | `BEFORE INSERT` | Máximo 26 jogadores por seleção por edição |
| 2 | `trg_estadio_edicao` | `partida` | `BEFORE INSERT/UPDATE` | Estádio deve pertencer a cidade-sede da edição |
| 3 | `trg_jogador_partida` | `evento_de_jogo` | `BEFORE INSERT/UPDATE` | Jogador deve estar convocado para uma das seleções da partida |
| 4 | `trg_gols_jogador` | `evento_de_jogo` | `AFTER INSERT/UPDATE/DELETE` | Mantém `gols_marcados` em `convocacao` sincronizado |

---

## 📋 Consultas suportadas

| # | Consulta |
|---|----------|
| 1 | Todas as edições com ano, país-sede e campeão |
| 2 | Seleções participantes de uma edição |
| 3 | Grupos de uma edição e suas seleções |
| 4 | Classificação de um grupo |
| 5 | Partidas de uma edição (fase, data, estádio, placar) |
| 6 | Caminho do mata-mata (classificados por fase) |
| 7 | Elenco convocado de uma seleção numa edição |
| 8 | Eventos de uma partida (gols, cartões, substituições) |
| 9 | Artilheiros de uma edição |
| 10 | Histórico de uma seleção (participações, posições, J/V/E/D) |

Ver implementação completa em [`sql/consultas.sql`](sql/consultas.sql).

---

## 🚀 Como executar o protótipo

```bash
# 1. Instalar dependências
pip install psycopg2-binary requests

# 2. Executar
cd prototipo
python main.py

# 3. Na tela de login informe:
#    Host, Porta, Banco, Usuário, Senha do PostgreSQL
#    (o ollama deve estar rodando localmente na porta 11434)
```

Ver instruções completas em [`prototipo/README.md`](prototipo/README.md).

---

## 📦 Arquivos para entrega

| Arquivo | Fonte no repositório | Status |
|---------|----------------------|--------|
| `01.ER.pdf` | exportar de `diagramas/01.ER.drawio` | ✅ |
| `02.ER.xml` | `diagramas/01.ER.drawio` | ✅ |
| `03.Relacional.pdf` | exportar de `diagramas/02.Relacional.drawio` | ✅ |
| `04.Relacional.xml` | `diagramas/02.Relacional.drawio` | ✅ |
| `05.DDL.sql` | `sql/05.DDL.sql` | ✅ |
| `06.DML.sql` | `sql/06.DML.sql` | 🔄 preencher |
| `07.Prototipo.zip` | `prototipo/` | 🔄 em andamento |
| `08.Instrucoes.txt` | `08.Instrucoes.txt` | 🔄 preencher |

---

## 🔧 Setup rápido do banco local

```sql
-- No psql:
CREATE DATABASE copa_do_mundo;
\c copa_do_mundo
\i sql/05.DDL.sql
\i sql/06.DML.sql
```
