#!/usr/bin/env python3
"""Perkecil hasil klasifikasi dari notebook (outputs/) menjadi data ringan untuk aplikasi (data/).

Jalankan LOKAL (butuh geopandas), bukan di server deploy:
    python prepare_data.py --src ../outputs --dst data --target-mb 12

Setiap kali model dilatih ulang, jalankan lagi skrip ini lalu push folder data/ ke GitHub.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

import geopandas as gpd

CODES = ["built_up", "farmland", "water", "forest", "mangrove"]
PROTECTED = {"mangrove", "water"}   # kelas kecil/penting: jangan dibuang bercaknya
# (luas minimum ha, toleransi penyederhanaan dalam derajat ~ 0.0003 deg = 33 m), dari halus ke kasar
LEVELS = [(0, 0.0001), (1, 0.0002), (2, 0.0003), (5, 0.0005), (10, 0.0008), (20, 0.0012), (40, 0.002)]
COPY_FILES = ["luas_per_kelas.csv", "metrics.json", "confusion_matrix.png", "feature_importance.png",
              "tanda_spektral.png", "perbandingan_komposit.png", "separabilitas_fitur.csv"]


def shrink(gdf, code, min_ha, tol):
    g = gdf[["class", "label", "luas_ha", "geometry"]].copy()
    if code in PROTECTED:
        min_ha, tol = 0, min(tol, 0.0002)
    g = g[g["luas_ha"] >= min_ha].copy()
    g["geometry"] = g.geometry.simplify(tol, preserve_topology=True)
    try:
        g["geometry"] = g.geometry.set_precision(1e-5)   # kurangi digit koordinat
    except Exception:
        pass
    return g[g.geometry.notna() & ~g.geometry.is_empty]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="outputs")
    ap.add_argument("--dst", default="data")
    ap.add_argument("--target-mb", type=float, default=12.0, help="total ukuran semua GeoJSON")
    a = ap.parse_args()
    src, dst = Path(a.src), Path(a.dst)
    dst.mkdir(parents=True, exist_ok=True)

    full = {}
    for c in CODES:
        p = src / f"hasil_{c}.geojson"
        if not p.exists():
            sys.exit(f"File tidak ditemukan: {p}")
        full[c] = gpd.read_file(p).to_crs(4326)
        print(f"{c:9s} asli: {len(full[c]):6d} poligon")

    chosen = None
    for min_ha, tol in LEVELS:
        shr = {c: shrink(full[c], c, min_ha, tol) for c in CODES}
        mb = sum(len(g.to_json()) for g in shr.values()) / 1e6
        print(f"min_ha={min_ha:>3}  tol={tol:<7}  ->  {mb:6.1f} MB")
        chosen = (min_ha, tol, shr, mb)
        if mb <= a.target_mb:
            break
    min_ha, tol, shr, mb = chosen
    if mb > a.target_mb:
        print(f"PERINGATAN: ukuran {mb:.1f} MB masih di atas target {a.target_mb} MB (level paling kasar sudah dipakai).")

    for c, g in shr.items():
        g.to_file(dst / f"hasil_{c}.geojson", driver="GeoJSON")
    for f in COPY_FILES:
        if (src / f).exists():
            shutil.copy(src / f, dst / f)
        else:
            print("lewati (tidak ada):", f)

    w, s, e, n = (min(g.total_bounds[0] for g in shr.values()), min(g.total_bounds[1] for g in shr.values()),
                  max(g.total_bounds[2] for g in shr.values()), max(g.total_bounds[3] for g in shr.values()))
    meta = {"bounds": [w, s, e, n], "min_ha_kelas_besar": min_ha, "toleransi_derajat": tol,
            "ukuran_mb": round(mb, 2), "poligon": {c: int(len(g)) for c, g in shr.items()}}
    json.dump(meta, open(dst / "meta.json", "w"), indent=2)
    print("\nSelesai ->", dst.resolve(), "|", meta["poligon"])


if __name__ == "__main__":
    main()
