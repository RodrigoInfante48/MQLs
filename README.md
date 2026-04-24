# MQLs — De Google Maps a tu CRM en minutos

> 200 prospectos con teléfono, dirección y web.  
> Costo: $0. Herramientas de pago: ninguna. Solo Python y Claude.

---

## El problema que esto resuelve

Cada freelancer, agencia y emprendedor digital llega al mismo punto muerto: necesita clientes, pero buscarlos uno por uno no escala, y pagar publicidad antes de validar la oferta es tirar dinero.

Lo que casi nadie sabe: Google Maps tiene millones de negocios locales registrados, cada uno con nombre, teléfono, dirección y sitio web — datos públicos, gratuitos y actualizados.

Este sistema los extrae, los limpia y los sube directo a tu CRM.

---

## Arquitectura

```
[Google Maps]
      ↓  Playwright — automatiza el browser, navega y extrae
[CSV por ciudad]  × N ciudades
      ↓  consolidar_leads.py — fusiona y elimina duplicados
[CSV limpio y único]
      ↓  Claude + Airtable Connector — filtra y carga al CRM
[Pipeline de ventas listo para trabajar]
```

**4 pasos. 0 costos fijos. Pipeline de ventas completo.**

---

## Stack

| Herramienta | Rol | Costo |
|---|---|---|
| Python 3.x | Motor de ejecución | Gratis |
| Playwright | Automatización del browser | Gratis |
| Google Maps | Fuente de leads | Gratis |
| `consolidar_leads.py` | Fusión y deduplicación | Gratis |
| Claude (claude.ai) | Filtrado inteligente + carga a Airtable | Gratis / Pro |
| Airtable | CRM centralizado | Gratis |

---

## Inicio rápido

```bash
# 1. Instalar dependencias
pip install playwright pandas
python -m playwright install chromium

# 2. Extraer leads — una ciudad
python gmaps_scraper.py --query "odontólogo Bogotá Colombia" --output leads_bogota.csv

# 2b. O extraer por país completo (multi-ciudad automático)
python python_leads.py co ./leads_output/
python python_leads.py mx ./leads_output/
python python_leads.py de ./leads_output/

# 3. Consolidar y limpiar duplicados
python consolidar_leads.py --folder ./leads_output/

# 4. Pégale el CSV a Claude con el conector de Airtable activado → listo
```

**Países disponibles:** `co` `mx` `ar` `cl` `es` `pe` `ve` `ec` `bo` `py` `uy` `us` `de`

---

## Estructura del repositorio

```
MQLs/
├── gmaps_scraper.py      # Scraper de una búsqueda / ciudad
├── python_leads.py       # Scraper multi-ciudad por código de país
├── consolidar_leads.py   # Fusiona CSVs y elimina duplicados
├── claude.md             # Guía completa: setup, prompts y buenas prácticas
└── README.md
```

Para la guía operacional completa con prompts y ejemplos → [claude.md](claude.md)

---

## Casos de uso

Funciona para cualquier nicho B2B local: odontólogos, veterinarias, gimnasios, restaurantes, profesionales independientes — en cualquier ciudad, en cualquier idioma.

---

## Licencia

MIT — libre para usar, modificar y distribuir.

---

**Autor:** Rodrigo Infante — [Daily Duty Institute](https://linktr.ee/DailyDuty)

> Si este repo te fue útil, dale una ⭐ y compártelo.
