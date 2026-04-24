"""
Consolidador y Deduplicador de Leads — DDI / DentBot
======================================================
Fusiona todos los CSVs de localidades en un solo archivo limpio,
elimina duplicados y genera un reporte del proceso.

Uso:
    # Consolida todos los CSV de la carpeta actual
    python consolidar_leads.py

    # Especifica una carpeta distinta
    python consolidar_leads.py --folder "C:/Users/rodri/OneDrive/Desktop/DentBot"

    # Cambia el archivo de salida
    python consolidar_leads.py --output leads_bogota_completo.csv

Requisitos:
    pip install pandas
"""

import pandas as pd
import argparse
from pathlib import Path
from datetime import datetime

# ─── CONFIG ────────────────────────────────────────────────────────────────────

DEFAULT_FOLDER = "."                          # carpeta donde están los CSVs
DEFAULT_OUTPUT = "leads_consolidado.csv"      # archivo final
DEDUP_COLUMNS  = ["WhatsApp", "Nombre"]       # columnas para detectar duplicados

# ─── MAIN ──────────────────────────────────────────────────────────────────────

def consolidar(folder: str, output: str):
    folder_path = Path(folder)

    # 1. Encontrar todos los CSVs en la carpeta (excepto el output anterior)
    csv_files = [
        f for f in folder_path.glob("*.csv")
        if f.name != output and f.name != "leads_consolidado.csv"
    ]

    if not csv_files:
        print(f"⚠️  No se encontraron archivos CSV en: {folder_path.resolve()}")
        return

    print(f"\n📂 Carpeta: {folder_path.resolve()}")
    print(f"📄 CSVs encontrados: {len(csv_files)}\n")

    # 2. Leer y concatenar todos los CSVs
    dfs = []
    total_raw = 0

    for f in sorted(csv_files):
        try:
            df = pd.read_csv(f, encoding="utf-8")
            count = len(df)
            total_raw += count
            dfs.append(df)
            print(f"  ✅ {f.name:<45} {count:>4} registros")
        except Exception as e:
            print(f"  ⚠️  {f.name}: Error al leer — {e}")

    if not dfs:
        print("\n⚠️  No se pudo leer ningún CSV.")
        return

    print(f"\n{'─'*55}")
    print(f"  Total bruto (con duplicados): {total_raw} registros")

    # 3. Concatenar
    combined = pd.concat(dfs, ignore_index=True)

    # 4. Limpiar espacios y vacíos en columnas clave
    for col in DEDUP_COLUMNS:
        if col in combined.columns:
            combined[col] = combined[col].astype(str).str.strip()
            combined[col] = combined[col].replace({"nan": "", "None": ""})

    # 5. Deduplicar — primero por WhatsApp (si tiene número), luego por Nombre
    before = len(combined)

    # Separar los que tienen WhatsApp de los que no
    con_tel    = combined[combined["WhatsApp"].str.len() > 5].copy()
    sin_tel    = combined[combined["WhatsApp"].str.len() <= 5].copy()

    # Dedup por WhatsApp en los que tienen número
    con_tel_clean = con_tel.drop_duplicates(subset=["WhatsApp"], keep="first")

    # Dedup por Nombre en los que no tienen número
    sin_tel_clean = sin_tel.drop_duplicates(subset=["Nombre"], keep="first")

    # Reunir
    final = pd.concat([con_tel_clean, sin_tel_clean], ignore_index=True)

    # Dedup final por Nombre por si hay registros con y sin teléfono del mismo lugar
    final = final.drop_duplicates(subset=["Nombre"], keep="first")

    after       = len(final)
    duplicates  = before - after

    print(f"  Duplicados eliminados:        {duplicates} registros")
    print(f"  Total limpio final:           {after} registros")
    print(f"{'─'*55}\n")

    # 6. Ordenar por Ciudad y luego por Nombre
    sort_cols = [c for c in ["Ciudad", "Nombre"] if c in final.columns]
    if sort_cols:
        final = final.sort_values(sort_cols).reset_index(drop=True)

    # 7. Guardar CSV final
    output_path = folder_path / output
    final.to_csv(output_path, index=False, encoding="utf-8")

    print(f"✅ Archivo consolidado guardado en:")
    print(f"   {output_path.resolve()}")
    print(f"\n📊 Resumen:")
    print(f"   Archivos procesados : {len(dfs)}")
    print(f"   Registros brutos    : {total_raw}")
    print(f"   Duplicados removidos: {duplicates}")
    print(f"   Registros finales   : {after}")

    # 8. Reporte de duplicados (opcional — guarda un CSV con los que se eliminaron)
    if duplicates > 0:
        dupes_path = folder_path / "leads_duplicados.csv"
        duplicated_mask = combined.duplicated(subset=["WhatsApp"], keep="first") | \
                          combined.duplicated(subset=["Nombre"], keep="first")
        combined[duplicated_mask].to_csv(dupes_path, index=False, encoding="utf-8")
        print(f"   Duplicados exportados a: {dupes_path.name} (para revisión)")

    print()

# ─── ENTRY POINT ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Consolidador de Leads CSVs — DDI / DentBot")
    parser.add_argument("--folder", default=DEFAULT_FOLDER, help="Carpeta con los CSVs (default: carpeta actual)")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Nombre del archivo consolidado de salida")
    args = parser.parse_args()

    consolidar(folder=args.folder, output=args.output)
