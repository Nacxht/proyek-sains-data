# Peta Tutupan Lahan — Streamlit

Struktur:
```
app.py              aplikasi Streamlit (titik masuk deploy)
requirements.txt    dependensi aplikasi (ringan, tanpa geopandas/rasterio)
prepare_data.py     skrip LOKAL: memperkecil hasil notebook -> folder data/
data/               hasil_*.geojson, luas_per_kelas.csv, metrics.json, *.png, meta.json
```

Jalankan lokal:
```
pip install -r requirements.txt
streamlit run app.py
```

Ganti model / hasil baru (tanpa mengubah app.py):
1. Jalankan ulang notebook -> folder `outputs/` terbarui.
2. `python prepare_data.py --src ../outputs --dst data` (butuh geopandas).
3. Commit dan push folder `data/`. Streamlit Cloud otomatis memuat ulang.
