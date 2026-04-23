# MQLs — Marketing Qualified Leads con Python + Claude + Google Maps

> Genera cientos de leads reales con teléfono, dirección y web en minutos.  
> Sin pagar publicidad. Sin herramientas de pago. Solo Python y Claude.

---

## ¿Qué es esto?

Este repositorio documenta un sistema de generación de MQLs (Marketing Qualified Leads) usando:

- **Python + Playwright** para hacer scraping de Google Maps
- **Claude (Anthropic)** como copiloto para filtrar, enriquecer y cargar los leads
- **Airtable** como CRM centralizado
- **Páginas Amarillas** como fuente alternativa de leads por directorio

El resultado: una base de datos de prospectos calificados con nombre, teléfono, dirección, sitio web, rating y reseñas, lista para importar a cualquier CRM o trabajar directamente en Airtable.

---

## ¿Para quién es esto?

Para emprendedores digitales y freelancers que:

- Venden un producto o servicio a negocios locales (B2B)
- Quieren construir su propio pipeline de ventas sin depender de publicidad
- Tienen un nicho definido (odontólogos, veterinarios, restaurantes, gimnasios, etc.)
- Prefieren automatizar antes que pagar por herramientas

---

## Stack

| Herramienta | Rol | Costo |
|---|---|---|
| Python 3.x | Ejecutar el scraper | Gratis |
| Playwright | Controlar el browser | Gratis |
| Google Maps | Fuente de leads | Gratis |
| Claude (claude.ai) | Filtrar leads + cargar a Airtable | Gratis / Pro |
| Airtable | CRM de leads | Gratis |
| Páginas Amarillas | Fuente alternativa de leads | Gratis |

---

## Instalación

### 1. Requisitos previos

- Python 3.8 o superior instalado
- Una cuenta en [Airtable](https://airtable.com) con el conector de Claude activado
- Una cuenta en [Claude.ai](https://claude.ai)

### 2. Clonar el repositorio

```bash
git clone https://github.com/RodrigoInfante48/MQLs.git
cd MQLs
```

### 3. Instalar dependencias

```bash
pip install playwright pandas
python -m playwright install chromium
```

> **Windows (PowerShell):** Corre cada línea por separado, PowerShell no soporta `&&`.

---

## Uso

### Scraping básico — Bogotá

```bash
python gmaps_scraper.py
```

Esto busca `"odontólogo Bogotá Colombia"` en Google Maps, hace scroll automático y guarda los resultados en `leads_bogota.csv`.

### Otras ciudades

```bash
python gmaps_scraper.py --query "odontólogo Medellín Colombia" --output leads_medellin.csv
python gmaps_scraper.py --query "odontólogo Cali Colombia" --output leads_cali.csv
python gmaps_scraper.py --query "odontólogo Barranquilla Colombia" --output leads_barranquilla.csv
```

### Otros países

```bash
python gmaps_scraper.py --query "odontologo Ciudad de Mexico" --output leads_cdmx.csv
python gmaps_scraper.py --query "odontologo Buenos Aires" --output leads_buenosaires.csv
python gmaps_scraper.py --query "dentist Lima Peru" --output leads_lima.csv
```

### Otros nichos

```bash
python gmaps_scraper.py --query "veterinaria Bogotá Colombia" --output leads_vets_bogota.csv
python gmaps_scraper.py --query "gimnasio Bogotá Colombia" --output leads_gyms_bogota.csv
python gmaps_scraper.py --query "restaurante vegano Bogotá" --output leads_restaurantes.csv
```

### Parámetros disponibles

| Parámetro | Descripción | Default |
|---|---|---|
| `--query` | Búsqueda en Google Maps | `"odontólogo Bogotá Colombia"` |
| `--output` | Nombre del archivo CSV de salida | `leads_bogota.csv` |
| `--max` | Máximo de resultados a extraer | `200` |

---

## Qué extrae el scraper

Por cada lugar encontrado en Google Maps:

| Campo | Descripción |
|---|---|
| Nombre | Nombre del negocio o profesional |
| Categoría | Tipo de negocio según Google |
| Dirección | Dirección física completa |
| Teléfono | Número de contacto |
| Sitio web | URL del sitio web |
| Rating | Calificación (1.0 a 5.0) |
| Reseñas | Número total de reseñas |
| Horario | Estado actual (abierto/cerrado) |
| URL Maps | Link directo al perfil en Google Maps |
| Fecha | Fecha de extracción |
| Canal | Fuente (Google Maps) |
| Estado | Estado inicial en el CRM (Nuevo) |

---

## Flujo completo con Claude + Airtable

Una vez que tienes el CSV, el flujo recomendado es:

```
Google Maps → CSV → Claude → Airtable CRM
```

### Paso 1 — Scraping

Corre el script y obtén tu `leads_bogota.csv`.

### Paso 2 — Filtrado con Claude

Abre Claude en claude.ai con el conector de Airtable activado y pégale el contenido del CSV o páginas de directorios como Páginas Amarillas. Claude filtra automáticamente los leads que hacen fit con tu producto (excluye laboratorios, depósitos, centros de radiología, etc.) y sube directamente los válidos a tu tabla de Airtable.

Ejemplo de prompt:

```
Acá te paso los resultados del scraper de Google Maps para odontólogos en Bogotá.
Filtra únicamente los que tengan consultorio propio y atención a pacientes directos.
Excluye laboratorios dentales, centros de radiología y distribuidores de materiales.
Sube los válidos a mi tabla LEADS en Airtable con canal = "Google Maps" y estado = "Nuevo".
```

### Paso 3 — CRM en Airtable

Los leads quedan en tu tabla con todos los campos listos para trabajar: llamadas frías, secuencias de WhatsApp, seguimiento y cierre.

---

## Estructura del repositorio

```
MQLs/
├── gmaps_scraper.py       # Script principal de scraping
├── claude.md              # Esta guía
└── README.md              # Descripción general del repo
```

---

## Tips y buenas prácticas

**Google Maps limita a ~120 resultados por búsqueda.** Para cubrir una ciudad grande como Bogotá, divide por zonas:

```bash
python gmaps_scraper.py --query "odontólogo Chapinero Bogotá" --output leads_chapinero.csv
python gmaps_scraper.py --query "odontólogo Suba Bogotá" --output leads_suba.csv
python gmaps_scraper.py --query "odontólogo Usaquén Bogotá" --output leads_usaquen.csv
python gmaps_scraper.py --query "odontólogo Kennedy Bogotá" --output leads_kennedy.csv
```

**El scraper corre en modo headless** (sin ventana visible). Si quieres ver el browser en acción para debug, cambia `headless=True` a `headless=False` en el script.

**El CSV sale listo para importar a Airtable** usando la función de importación nativa. O puedes usar Claude directamente para subir los registros uno a uno con filtrado inteligente.

**Para escalar a otros países**, simplemente cambia la query. El scraper funciona con cualquier búsqueda válida de Google Maps en cualquier idioma.

---

## Fuentes alternativas de leads

Además de Google Maps, puedes alimentar tu CRM con:

| Fuente | Cómo usarla |
|---|---|
| Páginas Amarillas | Copia el texto de cada página y pégaselo a Claude |
| LinkedIn (búsqueda manual) | Perfiles individuales → Claude extrae y sube a Airtable |
| Apollo.io | Plan gratuito: 50 leads/mes con email verificado |
| Outscraper.com | Alternativa sin código a este script, ~$10 por 1,000 leads |

---

## Casos de uso

Este sistema funciona para cualquier nicho B2B local:

- Odontólogos → vender automatizaciones de historia clínica (DentBot)
- Veterinarias → vender automatizaciones de citas y fichas de mascotas
- Gimnasios → vender sistemas de seguimiento de clientes
- Restaurantes → vender sistemas de reservas o menú digital
- Cualquier profesional independiente → vender servicios digitales

---

## Licencia

MIT — libre para usar, modificar y distribuir.

---

## Autor

**Rodrigo Infante** — [Daily Duty Institute](https://linktr.ee/DailyDuty)  
Data Analyst · Analytics Engineer · Builder de herramientas digitales para negocios locales

> Si este repo te fue útil, dale una ⭐ y compártelo.
