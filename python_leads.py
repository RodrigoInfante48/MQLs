"""
python_leads.py — DentBot Lead Generation
==========================================
Genera leads de odontólogos desde Google Maps
por código de país o ciudad.

Uso:
    python python_leads.py <codigo> <carpeta_salida>
    python python_leads.py <codigo> <carpeta_salida> --max 300

Ejemplos:
    python python_leads.py de  C:\Users\rodri\OneDrive\Desktop\DentBot
    python python_leads.py mx  C:\Users\rodri\OneDrive\Desktop\DentBot
    python python_leads.py co  C:\Users\rodri\OneDrive\Desktop\DentBot
    python python_leads.py "Buenos Aires" C:\Users\rodri\OneDrive\Desktop\DentBot

Requisitos:
    pip install playwright pandas
    playwright install chromium
"""

import asyncio
import csv
import re
import argparse
import sys
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# ─── MAPEO DE CÓDIGOS → QUERIES ────────────────────────────────────────────────

LOCATION_MAP = {
    # Alemania
    "de": [
        "Zahnarzt Berlin Deutschland",
        "Zahnarzt München Deutschland",
        "Zahnarzt Hamburg Deutschland",
        "Zahnarzt Frankfurt Deutschland",
        "Zahnarzt Köln Deutschland",
    ],
    # México
    "mx": [
        "odontólogo Ciudad de México",
        "odontólogo Guadalajara México",
        "odontólogo Monterrey México",
        "dentista Puebla México",
    ],
    # Colombia
    "co": [
        "odontólogo Bogotá Colombia",
        "odontólogo Medellín Colombia",
        "odontólogo Cali Colombia",
        "odontólogo Barranquilla Colombia",
    ],
    # Argentina
    "ar": [
        "odontólogo Buenos Aires Argentina",
        "odontólogo Córdoba Argentina",
        "odontólogo Rosario Argentina",
    ],
    # Chile
    "cl": [
        "odontólogo Santiago Chile",
        "odontólogo Valparaíso Chile",
        "dentista Concepción Chile",
    ],
    # España
    "es": [
        "dentista Madrid España",
        "dentista Barcelona España",
        "dentista Valencia España",
        "dentista Sevilla España",
    ],
    # Perú
    "pe": [
        "odontólogo Lima Perú",
        "odontólogo Arequipa Perú",
        "dentista Trujillo Perú",
    ],
    # Venezuela
    "ve": [
        "odontólogo Caracas Venezuela",
        "odontólogo Maracaibo Venezuela",
        "dentista Valencia Venezuela",
    ],
    # Ecuador
    "ec": [
        "odontólogo Quito Ecuador",
        "odontólogo Guayaquil Ecuador",
    ],
    # Bolivia
    "bo": [
        "odontólogo La Paz Bolivia",
        "odontólogo Santa Cruz Bolivia",
    ],
    # Paraguay
    "py": [
        "odontólogo Asunción Paraguay",
    ],
    # Uruguay
    "uy": [
        "odontólogo Montevideo Uruguay",
    ],
    # Estados Unidos (hispano)
    "us": [
        "dentist Miami Florida",
        "dentist Los Angeles California",
        "dentist Houston Texas",
        "dentist New York USA",
    ],
}

# ─── HELPERS ───────────────────────────────────────────────────────────────────

def clean(text: str) -> str:
    return text.strip().replace("\n", " ") if text else ""

def extract_phone(text: str) -> str:
    match = re.search(r"[\+\d][\d\s\-\(\)]{7,}", text)
    return match.group(0).strip() if match else ""

def resolve_queries(code: str) -> list[str]:
    """Devuelve la lista de queries para el código dado."""
    key = code.strip().lower()
    if key in LOCATION_MAP:
        return LOCATION_MAP[key]
    # Si no es un código conocido, lo trata como búsqueda libre
    return [f"odontólogo {code}"]

# ─── SCRAPER (una query) ───────────────────────────────────────────────────────

SCROLL_PAUSES  = 60
SCROLL_DELAY   = 1.5
DETAIL_TIMEOUT = 8000

async def scrape_query(page, query: str, max_results: int) -> list[dict]:
    leads = []
    url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
    print(f"\n🔍 Buscando: {query}")
    await page.goto(url, wait_until="networkidle")
    await page.wait_for_timeout(3000)

    try:
        await page.click("button[aria-label='Aceptar todo']", timeout=3000)
    except:
        pass

    print("📜 Cargando resultados (scroll)...")
    results_panel = page.locator("div[role='feed']")

    for i in range(SCROLL_PAUSES):
        await results_panel.evaluate("el => el.scrollBy(0, 800)")
        await page.wait_for_timeout(int(SCROLL_DELAY * 1000))

        end_marker = page.locator("text=Llegaste al final de la lista")
        if await end_marker.count() == 0:
            end_marker = page.locator("text=You've reached the end of the list")
        if await end_marker.count() == 0:
            end_marker = page.locator("text=Das Ende der Liste wurde erreicht")
        if await end_marker.count() > 0:
            print(f"✅ Fin de lista en scroll #{i+1}")
            break

        current = await page.locator("a[href*='/maps/place/']").count()
        print(f"   Scroll {i+1}/{SCROLL_PAUSES} — {current} resultados", end="\r")
        if current >= max_results:
            print(f"\n✅ Límite de {max_results} alcanzado")
            break

    print()
    place_links = await page.locator("a[href*='/maps/place/']").all()
    urls = []
    for link in place_links:
        href = await link.get_attribute("href")
        if href and href not in urls:
            urls.append(href)

    print(f"📍 {len(urls)} lugares. Extrayendo detalles...\n")

    for i, place_url in enumerate(urls):
        try:
            await page.goto(place_url, wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)

            name = ""
            try:
                name = clean(await page.locator("h1").first.text_content(timeout=DETAIL_TIMEOUT))
            except:
                pass

            category = ""
            try:
                category = clean(await page.locator("button[jsaction*='category']").first.text_content(timeout=3000))
            except:
                pass

            address = ""
            try:
                addr_el = page.locator("button[data-item-id='address']")
                if await addr_el.count() > 0:
                    address = clean(await addr_el.first.text_content(timeout=3000))
            except:
                pass

            phone = ""
            try:
                phone_el = page.locator("button[data-item-id*='phone']")
                if await phone_el.count() > 0:
                    raw = clean(await phone_el.first.text_content(timeout=3000))
                    phone = extract_phone(raw)
            except:
                pass

            website = ""
            try:
                web_el = page.locator("a[data-item-id='authority']")
                if await web_el.count() > 0:
                    website = await web_el.first.get_attribute("href") or ""
            except:
                pass

            rating, reviews = "", ""
            try:
                rating_el = page.locator("div.F7nice span[aria-hidden='true']")
                if await rating_el.count() > 0:
                    rating = clean(await rating_el.first.text_content(timeout=2000))
                reviews_el = page.locator("div.F7nice span[aria-label*='reseñas'], div.F7nice span[aria-label*='reviews'], div.F7nice span[aria-label*='Bewertungen']")
                if await reviews_el.count() > 0:
                    raw_rev = await reviews_el.first.get_attribute("aria-label") or ""
                    reviews = re.sub(r"[^\d]", "", raw_rev)
            except:
                pass

            hours = ""
            try:
                hours_el = page.locator("div[data-hide-tooltip-on-mouse-move] span").first
                hours = clean(await hours_el.text_content(timeout=2000))
            except:
                pass

            lead = {
                "Nombre":    name,
                "Categoría": category,
                "Dirección": address,
                "Teléfono":  phone,
                "Sitio web": website,
                "Rating":    rating,
                "Reseñas":   reviews,
                "Horario":   hours,
                "URL Maps":  place_url,
                "Fecha":     datetime.today().strftime("%Y-%m-%d"),
                "Canal":     "Google Maps",
                "Estado":    "Nuevo",
            }
            leads.append(lead)
            print(f"  [{i+1}/{len(urls)}] ✅ {name} | {phone} | {address[:40]}...")

        except Exception as e:
            print(f"  [{i+1}/{len(urls)}] ⚠️  Error: {e}")

    return leads

# ─── MAIN RUNNER ───────────────────────────────────────────────────────────────

async def run(code: str, output_dir: str, max_results: int):
    queries = resolve_queries(code)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.today().strftime("%Y%m%d_%H%M")
    slug = code.strip().lower().replace(" ", "_")
    csv_file = output_path / f"leads_{slug}_{timestamp}.csv"

    all_leads = []
    seen_urls = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            locale="es-CO",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
        )
        page = await context.new_page()

        for query in queries:
            leads = await scrape_query(page, query, max_results)
            for lead in leads:
                if lead["URL Maps"] not in seen_urls:
                    seen_urls.add(lead["URL Maps"])
                    all_leads.append(lead)

        await browser.close()

    if all_leads:
        fieldnames = ["Nombre", "Categoría", "Dirección", "Teléfono", "Sitio web",
                      "Rating", "Reseñas", "Horario", "URL Maps", "Fecha", "Canal", "Estado"]
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_leads)
        print(f"\n✅ {len(all_leads)} leads únicos guardados en:\n   {csv_file.resolve()}")
    else:
        print("\n⚠️  No se encontraron leads.")

# ─── ENTRY POINT ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="DentBot Lead Generator — Google Maps",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Códigos disponibles:
  de  → Alemania (Berlín, Múnich, Hamburgo, Frankfurt, Colonia)
  mx  → México (CDMX, Guadalajara, Monterrey, Puebla)
  co  → Colombia (Bogotá, Medellín, Cali, Barranquilla)
  ar  → Argentina (Buenos Aires, Córdoba, Rosario)
  cl  → Chile (Santiago, Valparaíso, Concepción)
  es  → España (Madrid, Barcelona, Valencia, Sevilla)
  pe  → Perú (Lima, Arequipa, Trujillo)
  ve  → Venezuela (Caracas, Maracaibo, Valencia)
  ec  → Ecuador (Quito, Guayaquil)
  us  → EE.UU. hispano (Miami, LA, Houston, NY)

También puedes pasar cualquier ciudad directamente:
  python python_leads.py "Monterrey" C:\\ruta\\salida
        """
    )
    parser.add_argument("codigo",  help="Código de país (de, mx, co, ar...) o nombre de ciudad")
    parser.add_argument("carpeta", help="Carpeta donde guardar el CSV de leads")
    parser.add_argument("--max",   default=200, type=int, help="Máximo resultados por ciudad (default: 200)")

    if len(sys.argv) < 3:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    asyncio.run(run(args.codigo, args.carpeta, args.max))
