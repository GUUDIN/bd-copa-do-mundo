-- =============================================================================
-- SCC0640 – Copa do Mundo FIFA
-- 05.DDL.sql – Definição relacional
-- =============================================================================

CREATE TABLE confederacao (
    id_confederacao   SERIAL NOT NULL,
    nome_confederacao VARCHAR(255) NOT NULL,

    CONSTRAINT pk_confederacao PRIMARY KEY (id_confederacao)
);

CREATE TABLE pais (
    sigla_pais      VARCHAR(3)   NOT NULL,
    nome_pais       VARCHAR(255),
    id_confederacao INTEGER      NOT NULL,

    CONSTRAINT pk_pais             PRIMARY KEY (sigla_pais),
    CONSTRAINT fk_pais_confederacao FOREIGN KEY (id_confederacao)
        REFERENCES confederacao(id_confederacao)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE edicao_da_copa (
    ano                INTEGER     NOT NULL,
    pais_sede          VARCHAR(3)  NOT NULL,
    data_inicio        DATE        NOT NULL,
    data_fim           DATE        NOT NULL,
    campea             INTEGER,
    vice_campeao       INTEGER,
    terceiro_colocado  INTEGER,

    CONSTRAINT pk_edicao_da_copa PRIMARY KEY (ano),
    CONSTRAINT ck_campea_vice_campeao_diferentes        CHECK (campea       <> vice_campeao),
    CONSTRAINT ck_campea_terceiro_colocado_diferentes   CHECK (campea       <> terceiro_colocado),
    CONSTRAINT ck_vice_campeao_terceiro_colocado_diferentes CHECK (vice_campeao <> terceiro_colocado)
);

CREATE TABLE cidade_sede (
    cidade VARCHAR(255) NOT NULL,
    estado VARCHAR(2)   NOT NULL,

    CONSTRAINT pk_cidade_sede PRIMARY KEY (cidade, estado)
);

CREATE TABLE cidade_sedia_edicao (
    cidade     VARCHAR(255) NOT NULL,
    estado     VARCHAR(2)   NOT NULL,
    ano_edicao INTEGER      NOT NULL,

    CONSTRAINT pk_cidade_sedia_edicao PRIMARY KEY (cidade, estado, ano_edicao),
    CONSTRAINT fk_cidade_sedia_edicao_cidade_sede FOREIGN KEY (cidade, estado)
        REFERENCES cidade_sede(cidade, estado)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_cidade_sedia_edicao_edicao_da_copa FOREIGN KEY (ano_edicao)
        REFERENCES edicao_da_copa(ano)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE estadio (
    id_estadio SERIAL       NOT NULL,
    cidade     VARCHAR(255) NOT NULL,
    estado     VARCHAR(2)   NOT NULL,

    CONSTRAINT pk_estadio              PRIMARY KEY (id_estadio),
    CONSTRAINT fk_estadio_cidade_sede  FOREIGN KEY (cidade, estado)
        REFERENCES cidade_sede(cidade, estado)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE fase (
    tipo_de_fase VARCHAR(50) NOT NULL,
    ano          INTEGER     NOT NULL,

    CONSTRAINT pk_fase                 PRIMARY KEY (tipo_de_fase, ano),
    CONSTRAINT fk_fase_edicao_da_copa  FOREIGN KEY (ano) REFERENCES edicao_da_copa(ano)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT ck_fase_tipo_de_fase    CHECK (tipo_de_fase IN
        ('Fase de Grupos', 'Oitavas de Final', 'Quartas de Final',
         'Semifinais', 'Disputa de Terceiro Lugar', 'Final'))
);

CREATE TABLE grupo (
    letra_grupo CHAR(1)  NOT NULL,
    ano         INTEGER  NOT NULL,

    CONSTRAINT pk_grupo                PRIMARY KEY (letra_grupo, ano),
    CONSTRAINT fk_grupo_edicao_da_copa FOREIGN KEY (ano) REFERENCES edicao_da_copa(ano)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE tecnico (
    id_tecnico    SERIAL       NOT NULL,
    nome_tecnico  VARCHAR(255) NOT NULL,

    CONSTRAINT pk_tecnico PRIMARY KEY (id_tecnico)
);

CREATE TABLE selecao (
    id_selecao   SERIAL     NOT NULL,
    ano          INTEGER    NOT NULL,
    letra_grupo  CHAR(1)    NOT NULL,
    id_tecnico   INTEGER    NOT NULL,
    sigla_pais   VARCHAR(3) NOT NULL,

    CONSTRAINT pk_selecao         PRIMARY KEY (id_selecao, ano),
    CONSTRAINT un_selecao_por_ano UNIQUE      (sigla_pais, ano),
    CONSTRAINT fk_selecao_tecnico FOREIGN KEY (id_tecnico)
        REFERENCES tecnico(id_tecnico)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_selecao_grupo   FOREIGN KEY (letra_grupo, ano)
        REFERENCES grupo(letra_grupo, ano)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_selecao_pais    FOREIGN KEY (sigla_pais)
        REFERENCES pais(sigla_pais)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE selecao_grupo (
    id_selecao  INTEGER NOT NULL,
    ano         INTEGER NOT NULL,
    letra_grupo CHAR(1) NOT NULL,
    pontos      INTEGER NOT NULL,
    gols_pro    INTEGER,
    gols_contra INTEGER,
    saldo_gols  INTEGER GENERATED ALWAYS AS (gols_pro - gols_contra) STORED,

    CONSTRAINT pk_selecao_grupo         PRIMARY KEY (id_selecao, letra_grupo, ano),
    CONSTRAINT fk_selecao_grupo_selecao FOREIGN KEY (id_selecao, ano)
        REFERENCES selecao(id_selecao, ano)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_selecao_grupo_grupo   FOREIGN KEY (letra_grupo, ano)
        REFERENCES grupo(letra_grupo, ano)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT ck_selecao_grupo_pontos       CHECK (pontos      >= 0),
    CONSTRAINT ck_selecao_grupo_gols_pro     CHECK (gols_pro    >= 0),
    CONSTRAINT ck_selecao_grupo_gols_contra  CHECK (gols_contra >= 0)
);

CREATE TABLE jogador (
    id_jogador   SERIAL       NOT NULL,
    nome_jogador VARCHAR(255) NOT NULL,

    CONSTRAINT pk_jogador PRIMARY KEY (id_jogador)
);

CREATE TABLE convocacao (
    ano            INTEGER NOT NULL,
    id_selecao     INTEGER NOT NULL,
    id_jogador     INTEGER NOT NULL,
    numero_camisa  INTEGER NOT NULL,
    gols_marcados  INTEGER,

    CONSTRAINT pk_convocacao         PRIMARY KEY (id_jogador, ano),
    CONSTRAINT fk_convocacao_selecao FOREIGN KEY (id_selecao, ano)
        REFERENCES selecao(id_selecao, ano)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_convocacao_jogador FOREIGN KEY (id_jogador)
        REFERENCES jogador(id_jogador)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE partida (
    id_partida                    SERIAL    NOT NULL,
    tipo_de_fase                  VARCHAR(50) NOT NULL,
    ano                           INTEGER   NOT NULL,
    id_estadio                    INTEGER   NOT NULL,
    data_hora                     TIMESTAMP NOT NULL,
    selecao1                      INTEGER   NOT NULL,
    selecao2                      INTEGER   NOT NULL,
    gols_regulamentares_selecao1  INTEGER,
    gols_regulamentares_selecao2  INTEGER,
    gols_prorrogacao_selecao1     INTEGER,
    gols_prorrogacao_selecao2     INTEGER,
    gols_penaltis_selecao1        INTEGER,
    gols_penaltis_selecao2        INTEGER,
    id_vencedor                   INTEGER,

    CONSTRAINT pk_partida           PRIMARY KEY (id_partida),
    CONSTRAINT fk_partida_fase      FOREIGN KEY (tipo_de_fase, ano)
        REFERENCES fase(tipo_de_fase, ano)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_partida_estadio   FOREIGN KEY (id_estadio)
        REFERENCES estadio(id_estadio)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_partida_selecao1  FOREIGN KEY (selecao1, ano)
        REFERENCES selecao(id_selecao, ano)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_partida_selecao2  FOREIGN KEY (selecao2, ano)
        REFERENCES selecao(id_selecao, ano)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_partida_vencedor  FOREIGN KEY (id_vencedor, ano)
        REFERENCES selecao(id_selecao, ano)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT ck_partida_selecao_diferente CHECK (selecao1 <> selecao2),
    CONSTRAINT ck_fase_eliminatoria CHECK (
        tipo_de_fase = 'Fase de Grupos'
        OR id_vencedor IS NOT NULL
        OR gols_regulamentares_selecao1 IS NULL
    ),
    CONSTRAINT ck_vencedor_valido CHECK (
        id_vencedor IS NULL
        OR id_vencedor = selecao1
        OR id_vencedor = selecao2
    )
);

CREATE TABLE arbitro (
    id_arbitro SERIAL NOT NULL,

    CONSTRAINT pk_arbitro PRIMARY KEY (id_arbitro)
);

CREATE TABLE arbitragem_partida (
    id_partida INTEGER     NOT NULL,
    id_arbitro INTEGER     NOT NULL,
    funcao     VARCHAR(50) NOT NULL,

    CONSTRAINT pk_equipe_arbitragem         PRIMARY KEY (id_partida, id_arbitro),
    CONSTRAINT fk_equipe_arbitragem_partida FOREIGN KEY (id_partida)
        REFERENCES partida(id_partida)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_equipe_arbitragem_arbitro FOREIGN KEY (id_arbitro)
        REFERENCES arbitro(id_arbitro)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE evento_de_jogo (
    id_evento    SERIAL      NOT NULL,
    id_jogador   INTEGER,
    id_partida   INTEGER     NOT NULL,
    tipo_evento  VARCHAR(50) NOT NULL,
    tempo        TIME        NOT NULL,

    CONSTRAINT pk_evento_de_jogo         PRIMARY KEY (id_evento, id_partida),
    CONSTRAINT fk_evento_de_jogo_partida FOREIGN KEY (id_partida)
        REFERENCES partida(id_partida)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_evento_de_jogo_jogador FOREIGN KEY (id_jogador)
        REFERENCES jogador(id_jogador)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT ck_tipo_evento CHECK (tipo_evento IN
        ('Gol', 'Gol Contra', 'Pênalti Convertido',
         'Cartão Amarelo', 'Cartão Vermelho', 'Substituição'))
);

ALTER TABLE edicao_da_copa
    ADD CONSTRAINT fk_edicao_da_copa_campea            FOREIGN KEY (campea, ano)
        REFERENCES selecao(id_selecao, ano)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    ADD CONSTRAINT fk_edicao_da_copa_vice_campeao      FOREIGN KEY (vice_campeao, ano)
        REFERENCES selecao(id_selecao, ano)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    ADD CONSTRAINT fk_edicao_da_copa_terceiro_colocado FOREIGN KEY (terceiro_colocado, ano)
        REFERENCES selecao(id_selecao, ano)
        ON UPDATE CASCADE ON DELETE SET NULL;

-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- 1. Limita o número máximo de jogadores convocados por seleção (26)
CREATE OR REPLACE FUNCTION fn_limite_convocacao()
RETURNS TRIGGER AS $$
DECLARE
    total_jogadores INT;
BEGIN
    SELECT COUNT(*) INTO total_jogadores
    FROM convocacao
    WHERE id_selecao = NEW.id_selecao AND ano = NEW.ano;

    IF total_jogadores >= 26 THEN
        RAISE EXCEPTION 'Regra de Negócio: Uma seleção não pode ter mais de 26 jogadores convocados na edição de %.', NEW.ano;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_limite_convocacao
BEFORE INSERT ON convocacao
FOR EACH ROW EXECUTE FUNCTION fn_limite_convocacao();

-- 2. Garante que o estádio da partida pertença a uma cidade-sede daquela edição
CREATE OR REPLACE FUNCTION fn_estadio_cidade_sede()
RETURNS TRIGGER AS $$
DECLARE
    estadio_valido BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1
        FROM estadio e
        JOIN cidade_sedia_edicao cse ON e.cidade = cse.cidade AND e.estado = cse.estado
        WHERE e.id_estadio = NEW.id_estadio AND cse.ano_edicao = NEW.ano
    ) INTO estadio_valido;

    IF NOT estadio_valido THEN
        RAISE EXCEPTION 'Regra de Negócio: O estádio % não pertence a uma cidade-sede associada à edição da copa de %.', NEW.id_estadio, NEW.ano;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_estadio_edicao
BEFORE INSERT OR UPDATE ON partida
FOR EACH ROW EXECUTE FUNCTION fn_estadio_cidade_sede();

-- 3. Garante que o jogador de um evento esteja convocado em uma das seleções da partida
CREATE OR REPLACE FUNCTION fn_jogador_pertence_partida()
RETURNS TRIGGER AS $$
DECLARE
    jogador_valido BOOLEAN;
    v_ano  INTEGER;
    v_sel1 INTEGER;
    v_sel2 INTEGER;
BEGIN
    IF NEW.id_jogador IS NULL THEN
        RETURN NEW;
    END IF;

    SELECT ano, selecao1, selecao2 INTO v_ano, v_sel1, v_sel2
    FROM partida WHERE id_partida = NEW.id_partida;

    SELECT EXISTS (
        SELECT 1 FROM convocacao
        WHERE id_jogador = NEW.id_jogador
          AND ano        = v_ano
          AND id_selecao IN (v_sel1, v_sel2)
    ) INTO jogador_valido;

    IF NOT jogador_valido THEN
        RAISE EXCEPTION 'Regra de Negócio: O jogador associado ao evento não está convocado para nenhuma das seleções que disputam esta partida.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_jogador_partida
BEFORE INSERT OR UPDATE ON evento_de_jogo
FOR EACH ROW EXECUTE FUNCTION fn_jogador_pertence_partida();

-- 4. Atualiza automaticamente convocacao.gols_marcados a partir dos eventos
CREATE OR REPLACE FUNCTION fn_atualiza_gols_jogador()
RETURNS TRIGGER AS $$
DECLARE
    v_ano INTEGER;
BEGIN
    IF (TG_OP = 'INSERT' OR TG_OP = 'UPDATE') THEN
        IF NEW.id_jogador IS NOT NULL AND NEW.tipo_evento IN ('Gol', 'Pênalti Convertido') THEN
            SELECT ano INTO v_ano FROM partida WHERE id_partida = NEW.id_partida;

            UPDATE convocacao
            SET gols_marcados = COALESCE(gols_marcados, 0) + 1
            WHERE id_jogador = NEW.id_jogador AND ano = v_ano;
        END IF;
    END IF;

    IF (TG_OP = 'DELETE' OR TG_OP = 'UPDATE') THEN
        IF OLD.id_jogador IS NOT NULL AND OLD.tipo_evento IN ('Gol', 'Pênalti Convertido') THEN
            SELECT ano INTO v_ano FROM partida WHERE id_partida = OLD.id_partida;

            UPDATE convocacao
            SET gols_marcados = GREATEST(COALESCE(gols_marcados, 0) - 1, 0)
            WHERE id_jogador = OLD.id_jogador AND ano = v_ano;
        END IF;
    END IF;

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_gols_jogador
AFTER INSERT OR UPDATE OR DELETE ON evento_de_jogo
FOR EACH ROW EXECUTE FUNCTION fn_atualiza_gols_jogador();
