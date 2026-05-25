# 🏆 Sistema de Copas do Mundo FIFA

> **SCC0640 Bases de Dados** | USP / ICMC  
> Prof. Jose Fernando Rodrigues Junior

---

## 👥 Grupo

<!-- MEMBROS_START -->
| Nome | Nº USP | Responsabilidade na apresentação |
|------|--------|----------------------------------|
| João Marcelo Moreira Trovão Filho | 13676332 | DER + Modelo Relacional |
| André Luiz Santos Messias | 15493857 | DDL + DML + Triggers |
| Mateus Santos Messias | 12548000 | Implementação do Protótipo |
| Pedro Borges Gudin | 12547997 | Execução + Demonstração |
<!-- MEMBROS_END -->

---

## 📋 Descrição

Sistema de banco de dados para gerenciamento completo de edições da Copa do Mundo FIFA. Armazena e consulta informações sobre seleções, países, confederações, jogadores, técnicos, árbitros, estádios, cidades-sede, partidas, fases, grupos, convocações e eventos de jogo.

A carga de dados cobre as Copas de **1998, 2002, 2006, 2010, 2014, 2018 e 2022**,
período com 32 seleções por edição e máximo de 7 jogos por seleção. A Copa de
2026 foi excluída por ter outro formato.

---

## 📐 Diagramas

### Diagrama Entidade-Relacionamento (DER)

![DER](diagramas/exports/DER.png)

_[Abrir no draw.io viewer →](https://viewer.diagrams.net/?tags=%7B%7D&target=blank&highlight=0000ff&edit=https%3A%2F%2Fapp.diagrams.net%2F&layers=1&nav=1#Uhttps%3A%2F%2Fraw.githubusercontent.com%2FGUUDIN%2Fbd-copa-do-mundo%2Fmain%2Fdiagramas%2FDER.drawio)_

---

### Modelo Relacional (Crow's Foot)

![Modelo Relacional](diagramas/exports/MER.png)

_[Abrir no draw.io viewer →](https://viewer.diagrams.net/?tags=%7B%7D&target=blank&highlight=0000ff&edit=https%3A%2F%2Fapp.diagrams.net%2F&layers=1&nav=1#Uhttps%3A%2F%2Fraw.githubusercontent.com%2FGUUDIN%2Fbd-copa-do-mundo%2Fmain%2Fdiagramas%2FMER.drawio)_

---

## 🗄️ Esquema do Banco

O banco possui **17 tabelas** modeladas em PostgreSQL:

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
        integer     campea           FK
        integer     vice_campeao     FK
        integer     terceiro_colocado FK
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
        integer     gols_reg_sel1
        integer     gols_reg_sel2
        integer     gols_prorr_sel1
        integer     gols_prorr_sel2
        integer     gols_pen_sel1
        integer     gols_pen_sel2
        integer     id_vencedor      FK
    }
    ARBITRO {
        serial      id_arbitro       PK
    }
    ARBITRAGEM_PARTIDA {
        integer     id_partida       PK
        integer     id_arbitro       PK
        varchar50   funcao
    }
    EVENTO_DE_JOGO {
        serial      id_evento        PK
        integer     id_partida       FK
        integer     id_jogador       FK
        varchar50   tipo_evento
        time        tempo
    }

    CONFEDERACAO       ||--o{ PAIS                 : "tem"
    PAIS               ||--o{ SELECAO              : "representa"
    EDICAO_DA_COPA     ||--o{ FASE                 : "tem"
    EDICAO_DA_COPA     ||--o{ GRUPO                : "possui"
    EDICAO_DA_COPA     }o--o{ CIDADE_SEDE          : "via CSE"
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
    SELECAO            ||--o{ PARTIDA              : "disputa"
    PARTIDA            ||--o{ ARBITRAGEM_PARTIDA   : "tem árbitros"
    ARBITRO            ||--o{ ARBITRAGEM_PARTIDA   : "arbitra"
    PARTIDA            ||--o{ EVENTO_DE_JOGO       : "tem eventos"
    JOGADOR            |o--o{ EVENTO_DE_JOGO       : "realiza"
    SELECAO            |o--o| EDICAO_DA_COPA       : "campeã/vice/terceiro"
```

---

## ⚙️ Regras de Negócio (Triggers)

| # | Trigger | Regra |
|---|---------|-------|
| 1 | `trg_limite_convocacao` | Máximo de 26 jogadores convocados por seleção por edição |
| 2 | `trg_estadio_edicao` | O estádio da partida deve pertencer a uma cidade-sede daquela edição |
| 3 | `trg_jogador_partida` | O jogador de um evento deve estar convocado em uma das seleções da partida |
| 4 | `trg_gols_jogador` | Mantém `gols_marcados` em `convocacao` sincronizado automaticamente com os eventos |

---

## 📋 Consultas Suportadas

| # | Consulta |
|---|----------|
| 1 | Todas as edições: ano, país-sede e campeão |
| 2 | Seleções participantes de uma edição |
| 3 | Grupos de uma edição e suas seleções |
| 4 | Tabela de classificação de um grupo (pontos, saldo, gols) |
| 5 | Partidas de uma edição (fase, data, estádio, placar) |
| 6 | Caminho do mata-mata — classificados por fase |
| 7 | Elenco convocado de uma seleção numa edição |
| 8 | Eventos de uma partida (gols, cartões, substituições) |
| 9 | Artilheiros de uma edição (top 10) |
| 10 | Histórico de uma seleção (participações, títulos, J/V/E/D) |

---

## 🚀 Como Executar

### Pré-requisitos
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Python 3.10+

### 1. Subir o PostgreSQL

```bash
docker run -d \
  --name postgres-copa \
  -e POSTGRES_PASSWORD=copa123 \
  -e POSTGRES_DB=copa_mundo \
  -p 5432:5432 \
  postgres:16
```

### 2. Carregar o banco

```bash
docker cp sql/05.DDL.sql postgres-copa:/tmp/DDL.sql
docker cp sql/06.DML.sql postgres-copa:/tmp/DML.sql
docker exec -it postgres-copa psql -U postgres -d copa_mundo -f /tmp/DDL.sql
docker exec -it postgres-copa psql -U postgres -d copa_mundo -f /tmp/DML.sql
```

### 3. Subir o Ollama (IA local)

```bash
docker run -d \
  -v ollama:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  ollama/ollama

docker exec -it ollama ollama pull qwen2.5-coder:3b
```

### 4. Instalar dependências e rodar o protótipo

```bash
cd prototipo
pip install -r requirements.txt
python main.py
```

### 5. Credenciais de conexão

```
Host: localhost   Porta: 5432   Banco: copa_mundo
Usuário: postgres   Senha: copa123
```

---

## 📦 Arquivos de Entrega

| Arquivo | Origem |
|---------|--------|
| `01.ER.pdf` | Exportar `diagramas/DER.drawio` como PDF no draw.io |
| `02.ER.xml` | Renomear `diagramas/DER.drawio` |
| `03.Relacional.pdf` | Exportar `diagramas/MER.drawio` como PDF no draw.io |
| `04.Relacional.xml` | Renomear `diagramas/MER.drawio` |
| `05.DDL.sql` | `sql/05.DDL.sql` |
| `06.DML.sql` | `sql/06.DML.sql` |
| `07.Prototipo.zip` | Pasta `prototipo/` zipada |
| `08.Instrucoes.txt` | Raiz do repositório |
