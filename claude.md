# MQLs — Guía Completa de Arquitectura y Uso

> Python + Google Maps + Playwright + Claude = pipeline de ventas desde cero.  
> Sin pagar publicidad. Sin herramientas de pago. Replicable en cualquier nicho.

---

## ¿Qué es este sistema y por qué funciona?

La prospección manual es el cuello de botella de cualquier negocio que vende a empresas o profesionales locales. Buscar uno por uno en Google, copiar teléfonos a mano, armar una lista en Excel — eso no es un proceso, es un castigo.

Este sistema automatiza todo eso usando tres herramientas que ya existen y son gratuitas:

1. **Google Maps** tiene el directorio de negocios más completo del mundo, actualizado en tiempo real por los propios negocios.
2. **Playwright** es una librería de Python que controla un browser real — navega, hace scroll, abre cada perfil y extrae los datos como si fuera un humano, pero en segundos.
3. **Claude con Airtable** actúa como el filtro inteligente: lee el CSV, descarta los que no hacen fit y sube directo los leads válidos a tu CRM.

El resultado es una base de datos de prospectos calificados lista para trabajar en menos de una hora.

---

## Arquitectura del sistema

```
┌─────────────────────────────────────────────────────────────┐
│  FASE 1 — EXTRACCIÓN                                        │
│                                                             │
│  Google Maps                                                │
│      ↓  Playwright abre el browser, busca la query,        │
│         hace scroll hasta el final y visita cada perfil    │
│  CSV por ciudad                                             │
│  (Nombre, Teléfono, Dirección, Rating, Web, URL Maps...)   │
└─────────────────────────────────────────────────────────────┘
            ↓  (repite por cada ciudad o país)
┌─────────────────────────────────────────────────────────────┐
│  FASE 2 — CONSOLIDACIÓN Y LIMPIEZA                          │
│                                                             │
│  N archivos CSV de distintas ciudades                       │
│      ↓  consolidar_leads.py                                 │
│  Un solo CSV limpio, sin duplicados                         │
│  (deduplicado por WhatsApp → por Nombre → reporte)         │
└─────────────────────────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────────────────────────┐
│  FASE 3 — CALIFICACIÓN Y CARGA                              │
│                                                             │
│  CSV limpio → Claude (claude.ai) con Airtable activado      │
│      ↓  Claude lee, filtra por criterio de negocio          │
│         y sube los válidos al CRM                           │
│  Tabla LEADS en Airtable                                    │
└─────────────────────────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────────────────────────┐
│  FASE 4 — OPERACIÓN                                         │
│                                                             │
│  Llamadas frías / WhatsApp / Email / Seguimiento            │
└─────────────────────────────────────────────────────────────┘
```

---

## Instalación desde cero

### Requisitos previos

- Python 3.8 o superior
- Una cuenta en [Airtable](https://airtable.com) con el conector de Claude activado
- Una cuenta en [Claude.ai](https://claude.ai)

### 1. Clonar el repositorio

```bash
git clone https://github.com/RodrigoInfante48/MQLs.git
cd MQLs
```

### 2. Instalar dependencias

```bash
pip install playwright pandas
python -m playwright install chromium
```

> **Windows (PowerShell):** Ejecuta cada línea por separado.  
> **Mac/Linux:** Puedes encadenarlas con `&&`.

---

## Fase 1 — Extracción con Python + Playwright

Tienes dos scripts según tu escala de trabajo:

### `gmaps_scraper.py` — Una búsqueda, una ciudad

El más simple. Ideal para empezar o para nichos muy específicos.

```bash
# Default: odontólogos en Bogotá
python gmaps_scraper.py

# Otra ciudad
python gmaps_scraper.py --query "odontólogo Medellín Colombia" --output leads_medellin.csv --city "Medellín"

# Otro país
python gmaps_scraper.py --query "dentist Buenos Aires" --output leads_buenosaires.csv --city "Buenos Aires"

# Otro nicho
python gmaps_scraper.py --query "veterinaria Bogotá Colombia" --output leads_vets.csv --city "Bogotá"
```

**Parámetros:**

| Parámetro | Descripción | Default |
|---|---|---|
| `--query` | Búsqueda en Google Maps | `"odontólogo Bogotá Colombia"` |
| `--output` | Nombre del CSV de salida | `leads_bogota.csv` |
| `--city` | Ciudad para el campo Ciudad del CRM | `"Bogotá"` |
| `--max` | Máximo de resultados | `200` |

**Campos del CSV de salida** (mapeados a la tabla LEADS de Airtable):

| Campo | Descripción |
|---|---|
| Nombre | Nombre del negocio o profesional |
| WhatsApp | Número de contacto |
| Ciudad | Ciudad (del parámetro `--city`) |
| Zona / Barrio | Dirección completa |
| Canal | `Google Maps` |
| Estado | `Nuevo` |
| Consultorio propio | `true` |
| Notas | Categoría, Rating, Reseñas, Web, URL Maps |

---

### `python_leads.py` — Multi-ciudad por código de país

Para cuando necesitas volumen. Un solo comando lanza el scraper en todas las ciudades del país.

```bash
python python_leads.py co ./leads_output/       # Colombia
python python_leads.py mx ./leads_output/       # México
python python_leads.py de ./leads_output/       # Alemania
python python_leads.py "Monterrey" ./output/    # Ciudad libre (cualquier query)
```

**Países disponibles:**

| Código | País | Ciudades incluidas |
|---|---|---|
| `co` | Colombia | Bogotá, Medellín, Cali, Barranquilla |
| `mx` | México | CDMX, Guadalajara, Monterrey, Puebla |
| `ar` | Argentina | Buenos Aires, Córdoba, Rosario |
| `cl` | Chile | Santiago, Valparaíso, Concepción |
| `es` | España | Madrid, Barcelona, Valencia, Sevilla |
| `pe` | Perú | Lima, Arequipa, Trujillo |
| `ve` | Venezuela | Caracas, Maracaibo, Valencia |
| `ec` | Ecuador | Quito, Guayaquil |
| `bo` | Bolivia | La Paz, Santa Cruz |
| `py` | Paraguay | Asunción |
| `uy` | Uruguay | Montevideo |
| `us` | EE.UU. hispano | Miami, LA, Houston, Nueva York |
| `de` | Alemania | Berlín, Múnich, Hamburgo, Frankfurt, Colonia |

**Campos del CSV de salida:**

| Campo | Descripción |
|---|---|
| Nombre | Nombre del negocio |
| Categoría | Tipo según Google Maps |
| Dirección | Dirección física |
| Teléfono | Número de contacto |
| Sitio web | URL del sitio |
| Rating | Calificación (1.0–5.0) |
| Reseñas | Número de reseñas |
| Horario | Estado actual (abierto/cerrado) |
| URL Maps | Link directo al perfil |
| Fecha | Fecha de extracción |
| Canal | `Google Maps` |
| Estado | `Nuevo` |

> **Límite de Google Maps:** ~120 resultados por búsqueda. Para más leads en una ciudad grande, usa `gmaps_scraper.py` con queries por zona:
> ```bash
> python gmaps_scraper.py --query "odontólogo Chapinero Bogotá" --output leads_chapinero.csv
> python gmaps_scraper.py --query "odontólogo Suba Bogotá" --output leads_suba.csv
> python gmaps_scraper.py --query "odontólogo Kennedy Bogotá" --output leads_kennedy.csv
> ```

---

## Fase 2 — Consolidación y deduplicación

Después de correr el scraper en varias ciudades o varias zonas, tienes múltiples CSVs. `consolidar_leads.py` los fusiona en uno solo y elimina registros repetidos.

```bash
# Consolida todos los CSV de la carpeta actual
python consolidar_leads.py

# Desde una carpeta específica
python consolidar_leads.py --folder "C:/Users/rodri/Desktop/DentBot/leads"

# Con nombre de salida personalizado
python consolidar_leads.py --folder ./leads_output/ --output leads_colombia_final.csv
```

**Cómo funciona la deduplicación:**

1. Lee todos los archivos `.csv` de la carpeta (excepta el output anterior).
2. Separa los registros **con teléfono** de los **sin teléfono**.
3. Deduplica los que tienen teléfono por columna `WhatsApp`.
4. Deduplica los sin teléfono por columna `Nombre`.
5. Hace un dedup final por `Nombre` para eliminar cruces entre ambos grupos.
6. Guarda `leads_consolidado.csv` + `leads_duplicados.csv` (para revisión).

**Output del proceso:**

```
📂 Carpeta: /ruta/leads_output
📄 CSVs encontrados: 4

  ✅ leads_bogota.csv            112 registros
  ✅ leads_medellin.csv           98 registros
  ✅ leads_cali.csv               87 registros
  ✅ leads_barranquilla.csv       74 registros

───────────────────────────────────────────────────
  Total bruto (con duplicados): 371 registros
  Duplicados eliminados:         43 registros
  Total limpio final:           328 registros
───────────────────────────────────────────────────

✅ leads_consolidado.csv guardado.
```

---

## Fase 3 — Calificación y carga con Claude

Con el CSV limpio en mano, abre [claude.ai](https://claude.ai) con el **conector de Airtable activado** y pégale el contenido del archivo.

### Prompt base

```
Acá te paso los resultados del scraper de Google Maps para odontólogos en Colombia.

Filtra únicamente los que tengan consultorio propio y atención directa a pacientes.
Excluye: laboratorios dentales, centros de radiología, distribuidores de materiales, universidades.

Por cada lead válido:
- Sube a mi tabla LEADS en Airtable
- Canal = "Google Maps"
- Estado = "Nuevo"
- Consultorio propio = true
- Ciudad = [la que corresponda según la dirección]
```

### Variantes por nicho

```
# Veterinarias
Filtra solo clínicas veterinarias con atención presencial.
Excluye: tiendas de mascotas, petshops, distribuidores de alimentos.

# Gimnasios
Filtra gimnasios con membresías activas y atención presencial.
Excluye: tiendas de suplementos, estudios de yoga sin equipos, academias deportivas escolares.

# Restaurantes
Filtra restaurantes con servicio en mesa o delivery propio.
Excluye: food trucks sin dirección fija, catering empresarial, panaderías sin mesas.
```

---

## Fase 4 — Operación desde Airtable

Los leads quedan en tu tabla con todos los campos listos:

- **Vista Kanban** por `Estado`: Nuevo → Contactado → Interesado → Cerrado → Descartado
- **Vista de llamadas**: ordena por `Ciudad` para hacer bloques de llamadas por zona
- **Vista de seguimiento**: filtra por `Estado = Interesado` para las siguientes acciones

---

## Fuentes alternativas de leads

Además de Google Maps, puedes alimentar el mismo CRM con:

| Fuente | Cómo usarla |
|---|---|
| Páginas Amarillas | Copia el texto de cada página y pégaselo a Claude |
| LinkedIn (búsqueda manual) | Perfiles individuales → Claude extrae y sube a Airtable |
| Apollo.io | Plan gratuito: 50 leads/mes con email verificado |
| Outscraper.com | Alternativa sin código, ~$10 por 1,000 leads |

---

## Tips y buenas prácticas

**Modo visible para debug:** El scraper corre headless (sin ventana). Para verlo en acción, cambia `headless=True` a `headless=False` en el script.

**Horario de ejecución:** Google Maps no bloquea scrapers comunes, pero para grandes volúmenes (>500 leads seguidos) conviene correr el script en horarios de menor tráfico.

**El CSV sale listo para Airtable:** Los headers de `gmaps_scraper.py` están mapeados exactamente a los campos de la tabla LEADS. Importa directo sin reasignar columnas.

**Para escalar a otros idiomas:** El scraper funciona con cualquier query válida de Google Maps. Solo cambia el texto de búsqueda al idioma del país objetivo.

---

## Casos de uso validados

| Nicho | Query ejemplo | Producto que se vende |
|---|---|---|
| Odontólogos | `odontólogo Bogotá Colombia` | Automatizaciones de historia clínica (DentBot) |
| Veterinarias | `veterinaria Medellín Colombia` | Sistema de citas y fichas de mascotas |
| Gimnasios | `gimnasio Cali Colombia` | CRM de seguimiento de miembros |
| Restaurantes | `restaurante vegano Bogotá` | Sistema de reservas o menú digital |
| Cualquier profesional | query libre | Servicios digitales a medida |

---

## Licencia

MIT — libre para usar, modificar y distribuir.

---

## Autor

**Rodrigo Infante** — [Daily Duty Institute](https://linktr.ee/DailyDuty)  
Data Analyst · Analytics Engineer · Builder de herramientas digitales para negocios locales

> Si este repo te fue útil, dale una ⭐ y compártelo.
