#!/usr/bin/env python3
"""Generate sql/06.DML.sql from public Wikipedia World Cup pages.

The target schema models the 32-team era well, so this script loads the seven
World Cups from 1998 through 2022. It intentionally excludes 2026 because that
edition has a different competition format.

Development dependency:
    python -m pip install beautifulsoup4
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
import sys
import time
import unicodedata
from urllib.error import URLError
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = Path("/tmp") / "bd-copa-do-mundo-wiki"
OUTPUT = ROOT / "sql" / "06.DML.sql"

YEARS = [1998, 2002, 2006, 2010, 2014, 2018, 2022]
GROUPS = list("ABCDEFGH")
PHASES = [
    "Fase de Grupos",
    "Oitavas de Final",
    "Quartas de Final",
    "Semifinais",
    "Disputa de Terceiro Lugar",
    "Final",
]

CONFEDERATIONS = {
    1: "CONMEBOL",
    2: "UEFA",
    3: "CONCACAF",
    4: "CAF",
    5: "AFC",
    6: "OFC",
}

TEAM_INFO = {
    "Algeria": ("ALG", "Argélia", 4),
    "Angola": ("ANG", "Angola", 4),
    "Argentina": ("ARG", "Argentina", 1),
    "Australia": ("AUS", "Austrália", 5),
    "Austria": ("AUT", "Áustria", 2),
    "Belgium": ("BEL", "Bélgica", 2),
    "Bosnia and Herzegovina": ("BIH", "Bósnia e Herzegovina", 2),
    "Brazil": ("BRA", "Brasil", 1),
    "Bulgaria": ("BUL", "Bulgária", 2),
    "Cameroon": ("CMR", "Camarões", 4),
    "Canada": ("CAN", "Canadá", 3),
    "Chile": ("CHI", "Chile", 1),
    "China": ("CHN", "China", 5),
    "Colombia": ("COL", "Colômbia", 1),
    "Costa Rica": ("CRC", "Costa Rica", 3),
    "Croatia": ("CRO", "Croácia", 2),
    "Czech Republic": ("CZE", "República Tcheca", 2),
    "Denmark": ("DEN", "Dinamarca", 2),
    "Ecuador": ("ECU", "Equador", 1),
    "Egypt": ("EGY", "Egito", 4),
    "England": ("ENG", "Inglaterra", 2),
    "FR Yugoslavia": ("YUG", "Iugoslávia", 2),
    "France": ("FRA", "França", 2),
    "Germany": ("GER", "Alemanha", 2),
    "Ghana": ("GHA", "Gana", 4),
    "Greece": ("GRE", "Grécia", 2),
    "Honduras": ("HON", "Honduras", 3),
    "Iceland": ("ISL", "Islândia", 2),
    "Iran": ("IRN", "Irã", 5),
    "Italy": ("ITA", "Itália", 2),
    "Ivory Coast": ("CIV", "Costa do Marfim", 4),
    "Jamaica": ("JAM", "Jamaica", 3),
    "Japan": ("JPN", "Japão", 5),
    "Mexico": ("MEX", "México", 3),
    "Morocco": ("MAR", "Marrocos", 4),
    "Netherlands": ("NED", "Holanda", 2),
    "New Zealand": ("NZL", "Nova Zelândia", 6),
    "Nigeria": ("NGA", "Nigéria", 4),
    "North Korea": ("PRK", "Coreia do Norte", 5),
    "Norway": ("NOR", "Noruega", 2),
    "Panama": ("PAN", "Panamá", 3),
    "Paraguay": ("PAR", "Paraguai", 1),
    "Peru": ("PER", "Peru", 1),
    "Poland": ("POL", "Polônia", 2),
    "Portugal": ("POR", "Portugal", 2),
    "Qatar": ("QAT", "Catar", 5),
    "Republic of Ireland": ("IRL", "Irlanda", 2),
    "Romania": ("ROU", "Romênia", 2),
    "Russia": ("RUS", "Rússia", 2),
    "Saudi Arabia": ("KSA", "Arábia Saudita", 5),
    "Scotland": ("SCO", "Escócia", 2),
    "Senegal": ("SEN", "Senegal", 4),
    "Serbia": ("SRB", "Sérvia", 2),
    "Serbia and Montenegro": ("SCG", "Sérvia e Montenegro", 2),
    "Slovakia": ("SVK", "Eslováquia", 2),
    "Slovenia": ("SVN", "Eslovênia", 2),
    "South Africa": ("RSA", "África do Sul", 4),
    "South Korea": ("KOR", "Coreia do Sul", 5),
    "Spain": ("ESP", "Espanha", 2),
    "Sweden": ("SWE", "Suécia", 2),
    "Switzerland": ("SUI", "Suíça", 2),
    "Togo": ("TOG", "Togo", 4),
    "Trinidad and Tobago": ("TRI", "Trinidad e Tobago", 3),
    "Tunisia": ("TUN", "Tunísia", 4),
    "Turkey": ("TUR", "Turquia", 2),
    "Ukraine": ("UKR", "Ucrânia", 2),
    "United States": ("USA", "Estados Unidos", 3),
    "Uruguay": ("URU", "Uruguai", 1),
    "Wales": ("WAL", "País de Gales", 2),
}

# Pseudo-country used only because the schema has one host-country column.
HOST_ONLY_COUNTRIES = {"JKS": ("Japão/Coreia do Sul", 5)}

HOSTS = {
    1998: ("FRA", "FR", "1998-06-10", "1998-07-12"),
    2002: ("JKS", "JK", "2002-05-31", "2002-06-30"),
    2006: ("GER", "DE", "2006-06-09", "2006-07-09"),
    2010: ("RSA", "ZA", "2010-06-11", "2010-07-11"),
    2014: ("BRA", "BR", "2014-06-12", "2014-07-13"),
    2018: ("RUS", "RU", "2018-06-14", "2018-07-15"),
    2022: ("QAT", "QA", "2022-11-20", "2022-12-18"),
}

PODIUM = {
    1998: ("France", "Brazil", "Croatia"),
    2002: ("Brazil", "Germany", "Turkey"),
    2006: ("Italy", "France", "Germany"),
    2010: ("Spain", "Netherlands", "Germany"),
    2014: ("Germany", "Argentina", "Netherlands"),
    2018: ("France", "Croatia", "Belgium"),
    2022: ("Argentina", "France", "Croatia"),
}

SQUAD_HEADING_ALIASES = {
    "China": "China PR",
}


@dataclass
class GoalEvent:
    player_key: str
    player_name: str
    player_label: str
    minute_base: int
    minute_total: int
    event_type: str
    credited_side: str
    own_goal: bool


@dataclass
class Match:
    year: int
    phase: str
    group: str | None
    home: str
    away: str
    final_home: int
    final_away: int
    date: str
    time: str
    stadium: str
    city: str
    reg_home: int
    reg_away: int
    extra_home: int | None
    extra_away: int | None
    pen_home: int | None
    pen_away: int | None
    winner: str | None
    goals: list[GoalEvent] = field(default_factory=list)


def fetch(url: str) -> str:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / re.sub(r"[^A-Za-z0-9]+", "_", url).strip("_")
    if cache_file.exists():
        return cache_file.read_text(encoding="utf-8")

    last_error: Exception | None = None
    for attempt in range(4):
        try:
            req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            data = urlopen(req, timeout=60).read().decode("utf-8", "ignore")
            cache_file.write_text(data, encoding="utf-8")
            return data
        except URLError as exc:
            last_error = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Could not fetch {url}: {last_error}")


def soup(url: str) -> BeautifulSoup:
    return BeautifulSoup(fetch(url), "html.parser")


def norm(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\xa0", " ")).strip()


def sql(value: object) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, int):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def ascii_key(value: str) -> str:
    value = re.sub(r"\([^)]*\)", " ", value)
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"[^A-Za-z0-9]+", " ", value).lower()
    return norm(value)


def clean_player_name(value: str) -> str:
    value = norm(value)
    value = re.sub(r"\s*\(captain\)\s*", " ", value, flags=re.IGNORECASE)
    return norm(value)


def parse_player_cell(cell) -> tuple[str, str]:
    link = cell.find("a")
    if link:
        key = link.get("href") or link.get("title") or link.get_text(" ", strip=True)
        name = link.get("title") or link.get_text(" ", strip=True)
        return key, clean_player_name(name)
    text = cell.get_text(" ", strip=True)
    return text, clean_player_name(text)


def parse_squads(year: int) -> dict[str, list[tuple[int, str, str]]]:
    page = soup(f"https://en.wikipedia.org/wiki/{year}_FIFA_World_Cup_squads")
    squads: dict[str, list[tuple[int, str, str]]] = {}

    for team in TEAM_INFO:
        heading_name = SQUAD_HEADING_ALIASES.get(team, team)
        heading = page.find(id=heading_name.replace(" ", "_"))
        if not heading:
            continue
        table = heading.find_next("table")
        if not table:
            continue

        players: list[tuple[int, str, str]] = []
        for row in table.select("tr"):
            cells = row.find_all(["th", "td"])
            if len(cells) < 3:
                continue
            number_text = norm(cells[0].get_text(" ", strip=True))
            if not number_text.isdigit():
                continue
            player_key, player_name = parse_player_cell(cells[2])
            players.append((int(number_text), player_key, player_name))

        if players:
            squads[team] = players

    return squads


def parse_minute(text: str) -> tuple[int, int]:
    match = re.search(r"(\d{1,3})(?:\+(\d+))?'", text)
    if not match:
        return 0, 0
    base = int(match.group(1))
    added = int(match.group(2) or 0)
    return base, base + added


def parse_goal_li(item, credited_side: str) -> list[GoalEvent]:
    link = item.find("a")
    if link:
        player_key = link.get("href") or link.get("title") or link.get_text(" ", strip=True)
        player_name = clean_player_name(link.get("title") or link.get_text(" ", strip=True))
        player_label = clean_player_name(link.get_text(" ", strip=True))
    else:
        text = item.get_text(" ", strip=True)
        player_key = text
        player_name = clean_player_name(text.split("'")[0])
        player_label = player_name

    events: list[GoalEvent] = []
    for span in item.find_all("span"):
        text = norm(span.get_text(" ", strip=True))
        if "'" not in text:
            continue
        if any("'" in norm(child.get_text(" ", strip=True)) for child in span.find_all("span")):
            continue

        minute_base, minute_total = parse_minute(text)
        lower_text = text.lower()
        own_goal = "o.g." in lower_text
        penalty = "pen." in lower_text
        if own_goal:
            event_type = "Gol Contra"
        elif penalty:
            event_type = "Pênalti Convertido"
        else:
            event_type = "Gol"

        events.append(
            GoalEvent(
                player_key=player_key,
                player_name=player_name,
                player_label=player_label,
                minute_base=minute_base,
                minute_total=minute_total,
                event_type=event_type,
                credited_side=credited_side,
                own_goal=own_goal,
            )
        )
    return events


def parse_penalty_score(rows, penalty_header_index: int) -> tuple[int | None, int | None]:
    if penalty_header_index + 1 >= len(rows):
        return None, None
    cells = rows[penalty_header_index + 1].find_all(["td", "th"], recursive=False)
    if len(cells) < 3:
        return None, None
    match = re.search(r"(\d+)\s*[–-]\s*(\d+)", norm(cells[1].get_text(" ", strip=True)))
    if not match:
        return None, None
    return int(match.group(1)), int(match.group(2))


def parse_venue(box) -> tuple[str, str]:
    right = box.select_one(".fright")
    if not right:
        return "Estádio não informado", "Cidade não informada"
    lines = [norm(line) for line in right.get_text("\n", strip=True).split("\n")]
    lines = [line for line in lines if line and line != ","]
    stadium = lines[0] if lines else "Estádio não informado"
    city = "Cidade não informada"
    if len(lines) > 1 and not lines[1].startswith(("Attendance", "Referee")):
        city = lines[1]
    return stadium, city


def parse_match_box(box, year: int, phase: str, group: str | None = None) -> Match:
    home = norm(box.select_one(".fhome").get_text(" ", strip=True))
    away = norm(box.select_one(".faway").get_text(" ", strip=True))
    score = norm(box.select_one(".fscore").get_text(" ", strip=True))
    score_match = re.search(r"(\d+)\s*[–-]\s*(\d+)", score)
    if not score_match:
        raise ValueError(f"Could not parse score: {year} {home} x {away}: {score}")
    final_home, final_away = int(score_match.group(1)), int(score_match.group(2))

    date = box.select_one(".bday").get_text(strip=True)
    time_text = "00:00"
    time_el = box.select_one(".ftime")
    if time_el:
        time_match = re.search(r"\d{1,2}:\d{2}", time_el.get_text(" ", strip=True))
        if time_match:
            time_text = time_match.group(0)

    stadium, city = parse_venue(box)

    rows = box.select("table.fevent tr")
    goal_row = next((row for row in rows if "fgoals" in (row.get("class") or [])), None)
    goals: list[GoalEvent] = []
    if goal_row:
        for credited_side, selector in (("home", ".fhgoal"), ("away", ".fagoal")):
            cell = goal_row.select_one(selector)
            if not cell:
                continue
            for item in cell.select("li"):
                goals.extend(parse_goal_li(item, credited_side))

    reg_home = reg_away = extra_home = extra_away = 0
    for event in goals:
        is_extra_time = event.minute_base > 90
        if event.credited_side == "home":
            if is_extra_time:
                extra_home += 1
            else:
                reg_home += 1
        else:
            if is_extra_time:
                extra_away += 1
            else:
                reg_away += 1

    aet = "a.e.t." in score or "g.g." in score
    if reg_home + extra_home != final_home or reg_away + extra_away != final_away:
        raise ValueError(
            f"Goal count mismatch: {year} {phase} {home} {score} {away} "
            f"events={reg_home + extra_home}-{reg_away + extra_away}"
        )

    pen_home = pen_away = None
    for index, row in enumerate(rows):
        if norm(row.get_text(" ", strip=True)).lower() == "penalties":
            pen_home, pen_away = parse_penalty_score(rows, index)
            break

    winner = None
    if phase != "Fase de Grupos":
        if final_home > final_away:
            winner = home
        elif final_away > final_home:
            winner = away
        elif pen_home is not None and pen_away is not None:
            winner = home if pen_home > pen_away else away
        else:
            raise ValueError(f"Knockout match without winner: {year} {home} x {away}")

    return Match(
        year=year,
        phase=phase,
        group=group,
        home=home,
        away=away,
        final_home=final_home,
        final_away=final_away,
        date=date,
        time=time_text,
        stadium=stadium,
        city=city,
        reg_home=reg_home,
        reg_away=reg_away,
        extra_home=extra_home if aet else None,
        extra_away=extra_away if aet else None,
        pen_home=pen_home,
        pen_away=pen_away,
        winner=winner,
        goals=goals,
    )


def parse_matches() -> tuple[dict[tuple[int, str], list[str]], list[Match]]:
    groups: dict[tuple[int, str], list[str]] = {}
    matches: list[Match] = []

    for year in YEARS:
        for group in GROUPS:
            page = soup(f"https://en.wikipedia.org/wiki/{year}_FIFA_World_Cup_Group_{group}")
            teams: list[str] = []
            for box in page.select("div.footballbox"):
                home = norm(box.select_one(".fhome").get_text(" ", strip=True))
                away = norm(box.select_one(".faway").get_text(" ", strip=True))
                for team in (home, away):
                    if team not in teams:
                        teams.append(team)
                matches.append(parse_match_box(box, year, "Fase de Grupos", group))
            if len(teams) != 4:
                raise ValueError(f"Expected 4 teams in group {group}/{year}, found {teams}")
            groups[(year, group)] = teams

        page = soup(f"https://en.wikipedia.org/wiki/{year}_FIFA_World_Cup_knockout_stage")
        for index, box in enumerate(page.select("div.footballbox"), start=1):
            if index <= 8:
                phase = "Oitavas de Final"
            elif index <= 12:
                phase = "Quartas de Final"
            elif index <= 14:
                phase = "Semifinais"
            elif index == 15:
                phase = "Disputa de Terceiro Lugar"
            elif index == 16:
                phase = "Final"
            else:
                raise ValueError(f"Unexpected knockout match index {index} in {year}")
            matches.append(parse_match_box(box, year, phase))

    return groups, matches


def compute_group_table(
    groups: dict[tuple[int, str], list[str]], matches: list[Match]
) -> dict[tuple[int, str], dict[str, int]]:
    standings: dict[tuple[int, str], dict[str, int]] = {}
    for (year, group), teams in groups.items():
        for team in teams:
            standings[(year, team)] = {
                "group": group,
                "pontos": 0,
                "gols_pro": 0,
                "gols_contra": 0,
            }

    for match in matches:
        if match.phase != "Fase de Grupos":
            continue
        home_stats = standings[(match.year, match.home)]
        away_stats = standings[(match.year, match.away)]
        home_stats["gols_pro"] += match.final_home
        home_stats["gols_contra"] += match.final_away
        away_stats["gols_pro"] += match.final_away
        away_stats["gols_contra"] += match.final_home
        if match.final_home > match.final_away:
            home_stats["pontos"] += 3
        elif match.final_away > match.final_home:
            away_stats["pontos"] += 3
        else:
            home_stats["pontos"] += 1
            away_stats["pontos"] += 1

    return standings


def phase_insert_values(year: int) -> str:
    return ",\n    ".join(f"({sql(phase)}, {year})" for phase in PHASES)


def minute_to_time(minute: int) -> str:
    return f"{minute // 60:02d}:{minute % 60:02d}:00"


def resolve_player(
    year: int,
    team: str,
    event: GoalEvent,
    squad_index: dict[tuple[int, str], dict[str, tuple[int, str, str]]],
    squad_name_index: dict[tuple[int, str], dict[str, tuple[int, str, str]]],
    player_ids: dict[str, int],
    player_names: dict[str, str],
    convocations: dict[tuple[int, int], tuple[int, int]],
) -> int:
    squad_key = (year, team)
    by_key = squad_index.get(squad_key, {})
    by_name = squad_name_index.get(squad_key, {})

    row = by_key.get(event.player_key)
    if row is None:
        for candidate in (event.player_name, event.player_label):
            candidate_key = ascii_key(candidate)
            row = by_name.get(candidate_key)
            if row is not None:
                break
        if row is None:
            label_key = ascii_key(event.player_label)
            matches = [
                squad_row
                for name_key, squad_row in by_name.items()
                if label_key and (label_key == name_key.split()[-1] or label_key in name_key.split())
            ]
            if len(matches) == 1:
                row = matches[0]

    if row is None:
        raise ValueError(f"Scorer not found in squad: {year} {team}: {event.player_name}")

    number, player_key, player_name = row
    if player_key not in player_ids:
        player_ids[player_key] = len(player_ids) + 1
        player_names[player_key] = player_name
    player_id = player_ids[player_key]
    convocations[(year, player_id)] = (selection_ids[(year, team)], number)
    return player_id


selection_ids: dict[tuple[int, str], int] = {}


def build_sql() -> str:
    groups, matches = parse_matches()
    squads_by_year = {year: parse_squads(year) for year in YEARS}

    teams = sorted({team for match in matches for team in (match.home, match.away)})
    missing_codes = [team for team in teams if team not in TEAM_INFO]
    if missing_codes:
        raise ValueError(f"Missing team codes: {missing_codes}")

    missing_squads = [
        (year, team)
        for year in YEARS
        for team in teams
        if any(team in groups[(year, group)] for group in GROUPS)
        and team not in squads_by_year[year]
    ]
    if missing_squads:
        raise ValueError(f"Missing squads: {missing_squads}")

    global selection_ids
    selection_ids = {}
    next_selection_id = 1
    for year in YEARS:
        for group in GROUPS:
            for team in groups[(year, group)]:
                selection_ids[(year, team)] = next_selection_id
                next_selection_id += 1

    squad_index: dict[tuple[int, str], dict[str, tuple[int, str, str]]] = {}
    squad_name_index: dict[tuple[int, str], dict[str, tuple[int, str, str]]] = {}
    player_ids: dict[str, int] = {}
    player_names: dict[str, str] = {}
    convocations: dict[tuple[int, int], tuple[int, int]] = {}

    for year, squads in squads_by_year.items():
        for team, players in squads.items():
            if (year, team) not in selection_ids:
                continue
            for number, player_key, player_name in players:
                if player_key not in player_ids:
                    player_ids[player_key] = len(player_ids) + 1
                    player_names[player_key] = player_name
                player_id = player_ids[player_key]
                convocations[(year, player_id)] = (selection_ids[(year, team)], number)
                squad_index.setdefault((year, team), {})[player_key] = (number, player_key, player_name)
                squad_name_index.setdefault((year, team), {})[ascii_key(player_name)] = (
                    number,
                    player_key,
                    player_name,
                )

    # Validate scorer resolution against squads before emitting SQL.
    event_rows: list[tuple[int, int | None, str, str]] = []
    for match_id, match in enumerate(matches, start=1):
        for event in match.goals:
            actual_side = (
                "home" if event.credited_side == "away" else "away"
            ) if event.own_goal else event.credited_side
            team = match.home if actual_side == "home" else match.away
            player_id = resolve_player(
                match.year,
                team,
                event,
                squad_index,
                squad_name_index,
                player_ids,
                player_names,
                convocations,
            )
            event_rows.append((player_id, match_id, event.event_type, minute_to_time(event.minute_total)))

    standings = compute_group_table(groups, matches)

    venue_ids: dict[tuple[int, str, str], int] = {}
    city_states: set[tuple[str, str]] = set()
    for match in matches:
        state = HOSTS[match.year][1]
        city_states.add((match.city, state))
        venue_key = (match.year, match.stadium, match.city)
        if venue_key not in venue_ids:
            venue_ids[venue_key] = len(venue_ids) + 1

    lines: list[str] = [
        "-- =============================================================================",
        "-- SCC0640 – Copa do Mundo FIFA",
        "-- 06.DML.sql – Dados reais das Copas de 1998 a 2022",
        "-- Gerado por scripts/generate_real_dml.py a partir de páginas da Wikipedia.",
        "-- Edições cobertas: 1998, 2002, 2006, 2010, 2014, 2018 e 2022.",
        "-- Todas usam a estrutura de 32 seleções e máximo de 7 jogos por seleção.",
        "-- 2026 foi excluída por ter formato diferente.",
        "-- =============================================================================",
        "",
        "BEGIN;",
        "",
        "-- 1. CONFEDERAÇÕES",
        "INSERT INTO confederacao (id_confederacao, nome_confederacao) VALUES",
        ",\n".join(
            f"    ({conf_id}, {sql(name)})" for conf_id, name in CONFEDERATIONS.items()
        )
        + ";",
        "",
        "-- 2. PAÍSES / SELEÇÕES",
        "INSERT INTO pais (sigla_pais, nome_pais, id_confederacao) VALUES",
    ]

    country_rows = []
    for team in sorted(TEAM_INFO):
        code, country_name, conf_id = TEAM_INFO[team]
        country_rows.append((code, country_name, conf_id))
    for code, (country_name, conf_id) in HOST_ONLY_COUNTRIES.items():
        country_rows.append((code, country_name, conf_id))
    lines.append(
        ",\n".join(
            f"    ({sql(code)}, {sql(country_name)}, {conf_id})"
            for code, country_name, conf_id in sorted(country_rows)
        )
        + ";"
    )

    lines.extend(
        [
            "",
            "-- 3. TÉCNICO GENÉRICO (o schema exige técnico, mas o protótipo não consulta esse atributo)",
            "INSERT INTO tecnico (id_tecnico, nome_tecnico) VALUES",
            f"    (1, {sql('Não informado')});",
            "",
            "-- 4. EDIÇÕES DA COPA",
            "INSERT INTO edicao_da_copa (ano, pais_sede, data_inicio, data_fim) VALUES",
        ]
    )
    lines.append(
        ",\n".join(
            f"    ({year}, {sql(HOSTS[year][0])}, {sql(HOSTS[year][2])}, {sql(HOSTS[year][3])})"
            for year in YEARS
        )
        + ";"
    )

    lines.extend(["", "-- 5. CIDADES-SEDE", "INSERT INTO cidade_sede (cidade, estado) VALUES"])
    lines.append(
        ",\n".join(f"    ({sql(city)}, {sql(state)})" for city, state in sorted(city_states))
        + ";"
    )

    lines.extend(
        [
            "",
            "-- 6. CIDADES ASSOCIADAS A CADA EDIÇÃO",
            "INSERT INTO cidade_sedia_edicao (cidade, estado, ano_edicao) VALUES",
        ]
    )
    city_year_rows = sorted({(match.city, HOSTS[match.year][1], match.year) for match in matches})
    lines.append(
        ",\n".join(
            f"    ({sql(city)}, {sql(state)}, {year})" for city, state, year in city_year_rows
        )
        + ";"
    )

    lines.extend(["", "-- 7. ESTÁDIOS (schema guarda cidade/estado; nome do estádio fica documentado no gerador)", "INSERT INTO estadio (id_estadio, cidade, estado) VALUES"])
    venue_rows = sorted(venue_ids.items(), key=lambda item: item[1])
    lines.append(
        ",\n".join(
            f"    ({venue_id}, {sql(city)}, {sql(HOSTS[year][1])})"
            for (year, _stadium, city), venue_id in venue_rows
        )
        + ";"
    )

    lines.extend(["", "-- 8. FASES", "INSERT INTO fase (tipo_de_fase, ano) VALUES"])
    lines.append(",\n".join(phase_insert_values(year) for year in YEARS) + ";")

    lines.extend(["", "-- 9. GRUPOS", "INSERT INTO grupo (letra_grupo, ano) VALUES"])
    lines.append(
        ",\n".join(f"    ({sql(group)}, {year})" for year in YEARS for group in GROUPS)
        + ";"
    )

    lines.extend(["", "-- 10. SELEÇÕES", "INSERT INTO selecao (id_selecao, ano, letra_grupo, id_tecnico, sigla_pais) VALUES"])
    selection_rows = []
    for year in YEARS:
        for group in GROUPS:
            for team in groups[(year, group)]:
                code = TEAM_INFO[team][0]
                selection_rows.append((selection_ids[(year, team)], year, group, code))
    lines.append(
        ",\n".join(
            f"    ({sel_id}, {year}, {sql(group)}, 1, {sql(code)})"
            for sel_id, year, group, code in selection_rows
        )
        + ";"
    )

    lines.extend(["", "-- 11. CLASSIFICAÇÃO DA FASE DE GRUPOS", "INSERT INTO selecao_grupo (id_selecao, ano, letra_grupo, pontos, gols_pro, gols_contra) VALUES"])
    table_rows = []
    for year in YEARS:
        for group in GROUPS:
            for team in groups[(year, group)]:
                stats = standings[(year, team)]
                table_rows.append(
                    (
                        selection_ids[(year, team)],
                        year,
                        group,
                        stats["pontos"],
                        stats["gols_pro"],
                        stats["gols_contra"],
                    )
                )
    lines.append(
        ",\n".join(
            f"    ({sel_id}, {year}, {sql(group)}, {points}, {gf}, {ga})"
            for sel_id, year, group, points, gf, ga in table_rows
        )
        + ";"
    )

    lines.extend(["", "-- 12. JOGADORES DOS ELENCOS", "INSERT INTO jogador (id_jogador, nome_jogador) VALUES"])
    player_rows = sorted(((pid, player_names[key]) for key, pid in player_ids.items()), key=lambda row: row[0])
    lines.append(
        ",\n".join(f"    ({player_id}, {sql(player_name)})" for player_id, player_name in player_rows)
        + ";"
    )

    lines.extend(["", "-- 13. CONVOCAÇÕES", "INSERT INTO convocacao (ano, id_selecao, id_jogador, numero_camisa) VALUES"])
    convocation_rows = sorted((year, sel_id, player_id, number) for (year, player_id), (sel_id, number) in convocations.items())
    lines.append(
        ",\n".join(
            f"    ({year}, {sel_id}, {player_id}, {number})"
            for year, sel_id, player_id, number in convocation_rows
        )
        + ";"
    )

    lines.extend(["", "-- 14. PARTIDAS", "INSERT INTO partida (id_partida, tipo_de_fase, ano, id_estadio, data_hora, selecao1, selecao2, gols_regulamentares_selecao1, gols_regulamentares_selecao2, gols_prorrogacao_selecao1, gols_prorrogacao_selecao2, gols_penaltis_selecao1, gols_penaltis_selecao2, id_vencedor) VALUES"])
    match_rows = []
    for match_id, match in enumerate(matches, start=1):
        home_id = selection_ids[(match.year, match.home)]
        away_id = selection_ids[(match.year, match.away)]
        winner_id = selection_ids[(match.year, match.winner)] if match.winner else None
        venue_id = venue_ids[(match.year, match.stadium, match.city)]
        match_rows.append(
            (
                match_id,
                match.phase,
                match.year,
                venue_id,
                f"{match.date} {match.time}:00",
                home_id,
                away_id,
                match.reg_home,
                match.reg_away,
                match.extra_home,
                match.extra_away,
                match.pen_home,
                match.pen_away,
                winner_id,
            )
        )
    lines.append(
        ",\n".join(
            "    ("
            + ", ".join(sql(value) for value in row)
            + ")"
            for row in match_rows
        )
        + ";"
    )

    lines.extend(["", "-- 15. ÁRBITROS (estrutura mantida para compatibilidade)", "INSERT INTO arbitro (id_arbitro) VALUES", "    (1);"])

    lines.extend(["", "-- 16. EVENTOS DE GOL", "INSERT INTO evento_de_jogo (id_jogador, id_partida, tipo_evento, tempo) VALUES"])
    lines.append(
        ",\n".join(
            f"    ({player_id}, {match_id}, {sql(event_type)}, {sql(event_time)})"
            for player_id, match_id, event_type, event_time in event_rows
        )
        + ";"
    )

    lines.extend(["", "-- 17. CAMPEÕES, VICES E TERCEIROS COLOCADOS"])
    for year, (champion, runner_up, third) in PODIUM.items():
        lines.append(
            "UPDATE edicao_da_copa "
            f"SET campea = {selection_ids[(year, champion)]}, "
            f"vice_campeao = {selection_ids[(year, runner_up)]}, "
            f"terceiro_colocado = {selection_ids[(year, third)]} "
            f"WHERE ano = {year};"
        )

    lines.extend(
        [
            "",
            "-- 18. AJUSTE DAS SEQUÊNCIAS APÓS INSERTS COM IDs EXPLÍCITOS",
            "SELECT setval(pg_get_serial_sequence('confederacao', 'id_confederacao'), (SELECT MAX(id_confederacao) FROM confederacao), true);",
            "SELECT setval(pg_get_serial_sequence('tecnico', 'id_tecnico'), (SELECT MAX(id_tecnico) FROM tecnico), true);",
            "SELECT setval(pg_get_serial_sequence('estadio', 'id_estadio'), (SELECT MAX(id_estadio) FROM estadio), true);",
            "SELECT setval(pg_get_serial_sequence('selecao', 'id_selecao'), (SELECT MAX(id_selecao) FROM selecao), true);",
            "SELECT setval(pg_get_serial_sequence('jogador', 'id_jogador'), (SELECT MAX(id_jogador) FROM jogador), true);",
            "SELECT setval(pg_get_serial_sequence('arbitro', 'id_arbitro'), (SELECT MAX(id_arbitro) FROM arbitro), true);",
            "SELECT setval(pg_get_serial_sequence('partida', 'id_partida'), (SELECT MAX(id_partida) FROM partida), true);",
            "SELECT setval(pg_get_serial_sequence('evento_de_jogo', 'id_evento'), (SELECT MAX(id_evento) FROM evento_de_jogo), true);",
            "",
            "COMMIT;",
            "",
            f"-- Totais gerados: {len(YEARS)} edições, {len(selection_rows)} seleções, {len(match_rows)} partidas, {len(player_rows)} jogadores, {len(convocation_rows)} convocações, {len(event_rows)} eventos de gol.",
        ]
    )

    return "\n".join(lines) + "\n"


def main() -> int:
    try:
        OUTPUT.write_text(build_sql(), encoding="utf-8")
    except Exception as exc:
        print(f"[ERRO] {exc}", file=sys.stderr)
        return 1
    print(f"[OK] DML gerado em {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
