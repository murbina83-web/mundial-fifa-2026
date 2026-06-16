"""
Scraper para la Copa Mundial de la FIFA 2026
Extrae calendario y resultados directamente de fifa.com
"""
import asyncio
import json
from pathlib import Path

MATCHES_FILE = Path(__file__).parent / "matches.json"
FIFA_URL = "https://www.fifa.com/es/tournaments/mens/worldcup/canadamexicousa2026/scores-fixtures?wtw-filter=ALL"

EXTRACT_JS = """
() => {
    const result = [];
    let currentDate = '';
    const allElements = document.querySelectorAll(
        '[class*="matches-container_title"], a[href*="/match-centre/match/"]'
    );
    [...allElements].forEach(el => {
        if ([...el.classList].some(c => c.includes('title'))) {
            currentDate = el.innerText.trim();
        } else {
            const lines = el.innerText.trim()
                .split('\\n')
                .map(l => l.trim())
                .filter(l => l && l !== '·');
            if (lines.length < 5) return;
            const home      = lines[0];
            const scoreHome = lines[1];
            const status    = lines[2];
            const scoreAway = lines[3];
            const away      = lines[4];
            const rest      = lines.slice(5);
            const phase     = rest[0] || '';
            const group     = rest.find(r => r.startsWith('Grupo'))
                           || rest.find(r => /final|cuartos|semi/i.test(r))
                           || '';
            const stadium   = rest.find(r => r.startsWith('Estadio')) || '';
            const city      = rest.find(r => r.startsWith('(')) || '';
            result.push({
                date: currentDate,
                home, scoreHome, status, scoreAway, away,
                phase, group, stadium, city,
                href: el.href
            });
        }
    });
    return result;
}
"""


async def scrape_fifa() -> list[dict]:
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        raise RuntimeError(
            "Playwright no está instalado. Ejecuta:\n"
            "  pip install playwright\n"
            "  playwright install chromium"
        )
    print("Iniciando navegador…")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(FIFA_URL, wait_until="networkidle", timeout=60_000)
        # Esperar a que carguen los partidos
        await page.wait_for_selector('a[href*="/match-centre/match/"]', timeout=30_000)
        matches = await page.evaluate(EXTRACT_JS)
        await browser.close()
    print(f"  {len(matches)} partidos extraídos.")
    return matches


def run_scrape() -> list[dict]:
    matches = asyncio.run(scrape_fifa())
    MATCHES_FILE.write_text(json.dumps(matches, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Guardado en {MATCHES_FILE}")
    return matches


def load_matches() -> list[dict]:
    if MATCHES_FILE.exists():
        return json.loads(MATCHES_FILE.read_text(encoding="utf-8"))
    return []


if __name__ == "__main__":
    run_scrape()
