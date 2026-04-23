# MQLs — Marketing Qualified Leads con Python + Google Maps

> Genera cientos de leads reales con teléfono, dirección y web en minutos.
> Sin pagar publicidad. Sin herramientas de pago. Solo Python y Claude.

---

## ¿Qué es esto?

Sistema de generación de MQLs (Marketing Qualified Leads) usando:

- **Python + Playwright** para scraping de Google Maps
- **Claude (Anthropic)** como copiloto para filtrar, enriquecer y cargar los leads
- **Airtable** como CRM centralizado

El resultado: una base de datos de prospectos calificados con nombre, teléfono, dirección, sitio web, rating y reseñas — lista para importar a cualquier CRM.

---

## Stack

| Herramienta | Rol | Costo |
|---|---|---|
| Python 3.x | Ejecutar el scraper | Gratis |
| Playwright | Controlar el browser | Gratis |
| Google Maps | Fuente de leads | Gratis |
| Claude (claude.ai) | Filtrar leads + cargar a Airtable | Gratis / Pro |
| Airtable | CRM de leads | Gratis |

---

## Inicio rápido

\`\`\`bash
# Instalar dependencias
pip install playwright pandas
python -m playwright install chromium

# Scraping básico — odontólogos en Bogotá
python gmaps_scraper.py

# Con parámetros
python gmaps_scraper.py --query "odontólogo Medellín Colombia" --output leads_medellin.csv

# Por código de país (multi-ciudad automático)
python python_leads.py co C:\ruta\salida
python python_leads.py mx C:\ruta\salida
python python_leads.py de C:\ruta\salida
\`\`\`

**Países disponibles:** co mx ar cl es pe ve ec bo py uy us de

---

## Flujo

\`\`\`
Google Maps → CSV → Claude → Airtable CRM
\`\`\`

1. Corre el scraper → obtén el CSV
2. Pégale el CSV a Claude con el conector de Airtable activado
3. Claude filtra los leads relevantes y los sube directamente a tu tabla

---

## Estructura

\`\`\`
MQLs/
├── gmaps_scraper.py   # Scraper principal (una búsqueda)
├── python_leads.py    # Scraper multi-ciudad por código de país
├── claude.md          # Guía completa de uso con Claude + Airtable
└── README.md
\`\`\`

Para la guía completa con ejemplos, prompts y buenas prácticas → [claude.md](claude.md)

---

## Casos de uso

Funciona para cualquier nicho B2B local: odontólogos, veterinarias, gimnasios, restaurantes, profesionales independientes.

---

## Licencia

MIT — libre para usar, modificar y distribuir.

---

**Autor:** Rodrigo Infante — [Daily Duty Institute](https://linktr.ee/DailyDuty)

> Si este repo te fue útil, dale una ⭐ y compártelo.
