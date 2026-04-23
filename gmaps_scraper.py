"""
Google Maps Scraper — Odontólogos
DDI / DentBot Lead Generation
================================
Uso:
    python gmaps_scraper.py
    python gmaps_scraper.py --query "odontólogo Medellín" --output leads_medellin.csv
    python gmaps_scraper.py --query "dentist Buenos Aires" --output leads_buenosaires.csv

Requisitos:
    pip install playwright pandas
    playwright install chromium
"""

import asyncio
import csv
import re
import argparse
import time
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# ─── CONFIG ────────────────────────────────────────────────────────────────────

DEFAULT_QUERY  = "odontólogo Bogotá Colombia"
DEFAULT_OUTPUT = "leads_bogota.csv"
SCROLL_PAUSES  = 60          # cuántas veces hace scroll en la lista (más = más resultados)
SCROLL_DELAY   = 1.5         # segundos entre scrolls
DETAIL_TIMEOUT = 8000        # ms para esperar cada panel de detalle

# ─── HELPERS ───────────────────────────────────────────────────────────────────

def clean(text: str) -> str:
    return text.strip().replace("\n", " ") if text else ""

def extract_phone(text: str) -> str:
    """Extrae el primer número de teléfono del texto."""
    match = re.search(r"[\+\d][\d\s\-\(\)]{7,}", text)
    return match.group(0).strip() if match else ""

# ─── SCRAPER ───────────────────────────────────────────────────────────────────

async def scrape_google_maps(query: str, output_file: str, max_results: int = 200):
    leads = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            locale="es-CO",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
        )
        page = await context.new_page()

        # 1. Ir a Google Maps con la búsqueda
        url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
        print(f"\n🔍 Buscando: {query}")
        print(f"🌐 URL: {url}\n")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(4000)

        # 2. Cerrar popups de cookies si aparecen
        try:
            await page.click("button[aria-label='Aceptar todo']", timeout=3000)
        except:
            pass

        # 3. Scroll en el panel de resultados para cargar más
        print("📜 Cargando resultados (scroll)...")
        results_panel = page.locator("div[role='feed']")

        for i in range(SCROLL_PAUSES):
            await results_panel.evaluate("el => el.scrollBy(0, 800)")
            await page.wait_for_timeout(int(SCROLL_DELAY * 1000))

            # Detectar si llegó al final
            end_marker = page.locator("text=Llegaste al final de la lista")
            if await end_marker.count() > 0:
                print(f"✅ Fin de lista alcanzado en scroll #{i+1}")
                break

            # Contar resultados actuales
            current = await page.locator("a[href*='/maps/place/']").count()
            print(f"   Scroll {i+1}/{SCROLL_PAUSES} — {current} resultados visibles", end="\r")

            if current >= max_results:
                print(f"\n✅ Límite de {max_results} resultados alcanzado")
                break

        print()

        # 4. Recopilar todos los links de lugares
        place_links = await page.locator("a[href*='/maps/place/']").all()
        urls = []
        for link in place_links:
            href = await link.get_attribute("href")
            if href and href not in urls:
                urls.append(href)

        print(f"📍 {len(urls)} lugares encontrados. Extrayendo detalles...\n")

        # 5. Visitar cada lugar y extraer datos
        for i, place_url in enumerate(urls):
            try:
                await page.goto(place_url, wait_until="domcontentloaded")
                await page.wait_for_timeout(2000)

                # Nombre
                name = ""
                try:
                    name = clean(await page.locator("h1").first.text_content(timeout=DETAIL_TIMEOUT))
                except:
                    pass

                # Categoría
                category = ""
                try:
                    category = clean(await page.locator("button[jsaction*='category']").first.text_content(timeout=3000))
                except:
                    pass

                # Dirección
                address = ""
                try:
                    addr_el = page.locator("button[data-item-id='address']")
                    if await addr_el.count() > 0:
                        address = clean(await addr_el.first.text_content(timeout=3000))
                except:
                    pass

                # Teléfono
                phone = ""
                try:
                    phone_el = page.locator("button[data-item-id*='phone']")
                    if await phone_el.count() > 0:
                        raw = clean(await phone_el.first.text_content(timeout=3000))
                        phone = extract_phone(raw)
                except:
                    pass

                # Sitio web
                website = ""
                try:
                    web_el = page.locator("a[data-item-id='authority']")
                    if await web_el.count() > 0:
                        website = await web_el.first.get_attribute("href") or ""
                except:
                    pass

                # Rating y reseñas
                rating = ""
                reviews = ""
                try:
                    rating_el = page.locator("div.F7nice span[aria-hidden='true']")
                    if await rating_el.count() > 0:
                        rating = clean(await rating_el.first.text_content(timeout=2000))
                    reviews_el = page.locator("div.F7nice span[aria-label*='reseñas']")
                    if await reviews_el.count() > 0:
                        raw_rev = await reviews_el.first.get_attribute("aria-label") or ""
                        reviews = re.sub(r"[^\d]", "", raw_rev)
                except:
                    pass

                # Horario (abierto/cerrado)
                hours = ""
                try:
                    hours_el = page.locator("div[data-hide-tooltip-on-mouse-move] span").first
                    hours = clean(await hours_el.text_content(timeout=2000))
                except:
                    pass

                lead = {
                    "Nombre":     name,
                    "Categoría":  category,
                    "Dirección":  address,
                    "Teléfono":   phone,
                    "Sitio web":  website,
                    "Rating":     rating,
                    "Reseñas":    reviews,
                    "Horario":    hours,
                    "URL Maps":   place_url,
                    "Fecha":      datetime.today().strftime("%Y-%m-%d"),
                    "Canal":      "Google Maps",
                    "Estado":     "Nuevo",
                }

                leads.append(lead)
                print(f"  [{i+1}/{len(urls)}] ✅ {name} | {phone} | {address[:40]}...")

            except Exception as e:
                print(f"  [{i+1}/{len(urls)}] ⚠️  Error en {place_url[:60]}: {e}")
                continue

        await browser.close()

    # 6. Guardar CSV
    if leads:
        output_path = Path(output_file)
        fieldnames = ["Nombre", "Categoría", "Dirección", "Teléfono", "Sitio web",
                      "Rating", "Reseñas", "Horario", "URL Maps", "Fecha", "Canal", "Estado"]

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(leads)

        print(f"\n✅ {len(leads)} leads guardados en: {output_path.resolve()}")
    else:
        print("\n⚠️  No se encontraron leads.")

    return leads

# ─── MAIN ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Google Maps Scraper — Odontólogos DentBot")
    parser.add_argument("--query",   default=DEFAULT_QUERY,  help="Búsqueda en Google Maps")
    parser.add_argument("--output",  default=DEFAULT_OUTPUT, help="Archivo CSV de salida")
    parser.add_argument("--max",     default=200, type=int,  help="Máximo de resultados (default: 200)")
    args = parser.parse_args()

    asyncio.run(scrape_google_maps(
        query=args.query,
        output_file=args.output,
        max_results=args.max
    ))
