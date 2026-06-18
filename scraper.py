"""
Scraper Copa Mundial FIFA 2026
Usa la API de ESPN — no requiere navegador ni Playwright.
"""
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

MATCHES_FILE = Path(__file__).parent / "matches.json"

ESPN_URL = (
    "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard"
    "?limit=150&dates=20260611-20260719"
)

# Traducción de nombres de equipos ESPN → español
TEAM_ES = {
    "Mexico": "México", "South Africa": "Sudáfrica", "Korea Republic": "República de Corea",
    "Czech Republic": "Chequia", "Canada": "Canadá", "Bosnia and Herzegovina": "Bosnia y Herzegovina",
    "United States": "EE. UU.", "Paraguay": "Paraguay", "Qatar": "Catar",
    "Switzerland": "Suiza", "Brazil": "Brasil", "Morocco": "Marruecos",
    "Haiti": "Haití", "Scotland": "Escocia", "Australia": "Australia",
    "Turkey": "Turquía", "Germany": "Alemania", "Curacao": "Curazao",
    "Netherlands": "Países Bajos", "Japan": "Japón", "Uruguay": "Uruguay",
    "Poland": "Polonia", "Spain": "España", "Ghana": "Ghana",
    "Senegal": "Senegal", "Serbia": "Serbia", "Portugal": "Portugal",
    "Algeria": "Argelia", "France": "Francia", "New Zealand": "Nueva Zelanda",
    "England": "Inglaterra", "Croatia": "Croacia", "Panama": "Panamá",
    "Colombia": "Colombia", "DR Congo": "RD Congo", "Uzbekistan": "Uzbekistán",
    "Argentina": "Argentina", "Iraq": "Irak", "Norway": "Noruega",
    "Austria": "Austria", "Jordan": "Jordania", "IR Iran": "RI de Irán",
    "Honduras": "Honduras", "Slovenia": "Eslovenia", "Chile": "Chile",
    "Ecuador": "Ecuador", "Ivory Coast": "Costa de Marfil", "Nigeria": "Nigeria",
    "Saudi Arabia": "Arabia Saudí", "Venezuela": "Venezuela", "Italy": "Italia",
    "Romania": "Rumanía", "Belgium": "Bélgica", "Egypt": "Egipto",
    "Denmark": "Dinamarca", "Tunisia": "Túnez", "Sweden": "Suecia",
    "Slovakia": "Eslovaquia", "Mali": "Mali", "Greece": "Grecia",
    "Cape Verde": "Islas de Cabo Verde", "Costa Rica": "Costa Rica",
    "Guadeloupe": "Guadalupe",
}

DAYS_ES = {
    "Monday": "lunes", "Tuesday": "martes", "Wednesday": "miércoles",
    "Thursday": "jueves", "Friday": "viernes", "Saturday": "sábado", "Sunday": "domingo",
}
MONTHS_ES = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
    7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre",
}

# Tipos de ronda ESPN → español
ROUND_ES = {
    "Group Stage": "Primera fase",
    "Round of 32": "Dieciseisavos de final",
    "Round of 16": "Octavos de final",
    "Quarterfinals": "Cuartos de final",
    "Semifinals": "Semifinal",
    "Third Place": "Partido por el tercer puesto",
    "Final": "Final",
}


def _date_es(iso: str) -> str:
    """Convierte '2026-06-11T20:00Z' → 'jueves 11 junio 2026'"""
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone()
        day_name = DAYS_ES.get(dt.strftime("%A"), dt.strftime("%A"))
        month_name = MONTHS_ES.get(dt.month, str(dt.month))
        return f"{day_name} {dt.day} {month_name} {dt.year}"
    except Exception:
        return iso[:10]


def _time_local(iso: str) -> str:
    """Convierte ISO → hora local 'HH:MM'"""
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone()
        return dt.strftime("%H:%M")
    except Exception:
        return ""


def fetch_matches() -> list[dict]:
    req = urllib.request.Request(ESPN_URL, headers={"User-Agent": "Mozilla/5.0"})
    raw = json.loads(urllib.request.urlopen(req, timeout=20).read())
    events = raw.get("events", [])

    matches = []
    for event in events:
        comp = event.get("competitions", [{}])[0]
        teams = comp.get("competitors", [])
        if len(teams) < 2:
            continue

        # Identificar local/visitante
        home = next((t for t in teams if t.get("homeAway") == "home"), teams[0])
        away = next((t for t in teams if t.get("homeAway") == "away"), teams[1])

        home_name = TEAM_ES.get(home["team"]["displayName"], home["team"]["displayName"])
        away_name = TEAM_ES.get(away["team"]["displayName"], away["team"]["displayName"])

        status_type = comp.get("status", {}).get("type", {})
        state = status_type.get("state", "pre")       # pre | in | post
        completed = status_type.get("completed", False)
        clock = comp.get("status", {}).get("displayClock", "")

        if completed or state == "post":
            status = "FINAL"
            score_home = home.get("score", "0")
            score_away = away.get("score", "0")
        elif state == "in":
            status = clock or "EN DIRECTO"
            score_home = home.get("score", "0")
            score_away = away.get("score", "0")
        else:
            status = "PENDIENTE"
            score_home = _time_local(event.get("date", ""))
            score_away = ""

        # Ronda
        notes = comp.get("notes", [])
        round_raw = notes[0].get("headline", "") if notes else ""
        round_es = ROUND_ES.get(round_raw, round_raw)

        # Grupo
        season_type = comp.get("season", {}).get("slug", "")
        group_raw = comp.get("groups", {}).get("name", "")
        if "Group" in group_raw:
            letter = group_raw.replace("Group ", "")
            group = f"Grupo {letter}"
        elif round_es in ("Primera fase", ""):
            group = ""
        else:
            group = round_es

        # Estadio / ciudad
        venue = comp.get("venue", {})
        stadium = venue.get("fullName", "")
        city_obj = venue.get("address", {})
        city = city_obj.get("city", "")
        city_str = f"({city})" if city else ""

        # Fecha en español
        date_es = _date_es(event.get("date", ""))

        # Link a FIFA (construido desde el href del partido si está disponible)
        match_id = comp.get("id", event.get("id", ""))
        href = f"https://www.fifa.com/es/match-centre/match/{match_id}"

        matches.append(dict(
            date=date_es,
            home=home_name,
            scoreHome=score_home,
            status=status,
            scoreAway=score_away,
            away=away_name,
            phase=round_es or "Primera fase",
            group=group,
            stadium=stadium,
            city=city_str,
            href=href,
        ))

    # Ordenar por fecha del evento original (ya vienen ordenados por ESPN)
    return matches


def run_scrape() -> list[dict]:
    print("Consultando API ESPN…")
    matches = fetch_matches()
    MATCHES_FILE.write_text(
        json.dumps(matches, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    finales = sum(1 for m in matches if m["status"] == "FINAL")
    print(f"  {len(matches)} partidos guardados ({finales} finales)")
    return matches


def load_matches() -> list[dict]:
    if MATCHES_FILE.exists():
        return json.loads(MATCHES_FILE.read_text(encoding="utf-8"))
    return []


if __name__ == "__main__":
    run_scrape()
