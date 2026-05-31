"""
fix_raw.py
Corre una sola vez sobre el CSV crudo. Genera data/data_raw.csv.
No documentar.

Uso:
    python fix_raw.py --input <ruta_csv_original> --output data/data_raw.csv
"""

import argparse
from pathlib import Path

import pandas as pd

DROP_COLS = [
    "Unnamed: 0.1",
    "Unnamed: 0",
    "Fecha de Denuncia",
    "Fecha de Nacimiento",
    "Fecha del Hecho",
    "photo_matrix",
    "sexo",
    "Nro Denuncia",
    "Instructor policial",
    "Hora de Denuncia",
    "Hora de Nacimiento",
    "Hora del Hecho",
    "Hora de Aparición",
]


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input",  required=True,               help="CSV original de entrada")
    p.add_argument("--output", default="data/data_raw.csv", help="CSV de salida")
    return p.parse_args()


def main():
    args = parse_args()
    df = pd.read_csv(args.input)
    print(f"[fix_raw] shape original     : {df.shape}")

    to_drop = [c for c in DROP_COLS if c in df.columns]
    df = df.drop(columns=to_drop)
    print(f"[fix_raw] columnas eliminadas: {len(to_drop)}")

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)
    print(f"[fix_raw] guardado en        : {args.output}  ({df.shape[0]} filas, {df.shape[1]} cols)")


if __name__ == "__main__":
    main()
