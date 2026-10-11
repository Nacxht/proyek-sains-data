"""Pemetaan tutupan lahan dari citra Sentinel-2 — aplikasi Streamlit.

Aplikasi hanya MEMUAT hasil yang sudah dihitung di notebook (folder data/).
Mengganti model = mengganti file di data/ (lihat README.md), app.py tidak perlu diubah.
"""
import json
from pathlib import Path

import altair as alt
import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

BASE = Path(__file__).parent
DATA = BASE / "data"

# ---------------------------------------------------------------- identitas (ubah sesuai kebutuhan)
APP = {
    "judul": "Pemetaan Tutupan Lahan dari Citra Sentinel-2",
    "subjudul": "Studi kasus Jawa Timur: wilayah percontohan Banyuwangi dan sekitarnya",
    "penulis": "Nama Mahasiswa",
    "mk": "Proyek Sains Data",
}

# ---------------------------------------------------------------- parameter alur (dokumentasi)
PIPELINE = {
    "sumber": "Sentinel-2 L2A (Copernicus Data Space Ecosystem, lewat openEO)",
    "periode": "1 Juni – 30 September 2026 (musim kemarau)",
    "band": "B2, B3, B4, B8, B8A, B11, B12",
    "resolusi": "20 m, EPSG:32749 (UTM 49S)",
    "bbox": [113.25, -8.84, 114.64, -7.56],        # barat, selatan, timur, utara
    "komposit": "B8A–B11–B4 (R=B8A, G=B11, B=B4)",
    "indeks": "NDVI, NDWI, NDBI, MNDWI, NDMI",
}

CLASSES = [
    {"code": "built_up", "label": "Bangunan", "en": "Built-up", "color": "#e53935"},
    {"code": "farmland", "label": "Lahan pertanian", "en": "Farmland", "color": "#fdd835"},
    {"code": "water", "label": "Badan air", "en": "Water body", "color": "#1e88e5"},
    {"code": "forest", "label": "Hutan", "en": "Forest", "color": "#2e7d32"},
    {"code": "mangrove", "label": "Hutan mangrove", "en": "Mangrove forest", "color": "#00e5c0"},
]
ESRI_IMAGERY = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
ESRI_LABELS = ("https://server.arcgisonline.com/ArcGIS/rest/services/Reference/"
               "World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}")

st.set_page_config(page_title=APP["judul"], page_icon="🛰️", layout="wide")


# ---------------------------------------------------------------- pemuat data (di-cache)
@st.cache_data(show_spinner=False)
def load_json(name):
    p = DATA / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


@st.cache_data(show_spinner=False)
def load_csv(name):
    p = DATA / name
    return pd.read_csv(p) if p.exists() else None


@st.cache_data(show_spinner="Memuat layer…")
def load_layer(code):
    return load_json(f"hasil_{code}.geojson")


def swatch(color):
    return (f"<span style='display:inline-block;width:14px;height:14px;border-radius:3px;"
            f"background:{color};margin-right:6px;vertical-align:-2px'></span>")


def show_image(name, caption):
    p = DATA / name
    if p.exists():
        st.image(str(p), caption=caption, width="stretch")
    else:
        st.info(f"Gambar `{name}` belum ada di folder data/.")


metrics = load_json("metrics.json")
area = load_csv("luas_per_kelas.csv")
meta = load_json("meta.json") or {}

# ---------------------------------------------------------------- header
st.title(APP["judul"])
st.caption(f"{APP['subjudul']}  ·  {APP['mk']}  ·  {APP['penulis']}")

tab_bu, tab_alur, tab_peta, tab_hasil = st.tabs(
    ["1 · Business Understanding", "2 · Alur & Data", "3 · Peta Interaktif", "4 · Ringkasan Hasil"])

# ================================================================ TAB 1: business understanding
with tab_bu:
    st.header("Business Understanding")
    st.subheader("Latar belakang")
    st.markdown(
        "Jawa Timur memiliki tutupan lahan yang sangat beragam: permukiman padat, persawahan, hutan "
        "pegunungan, hingga pesisir dengan hutan mangrove. Lahan terus berubah, sementara survei lapangan "
        "dan pemetaan manual lambat serta mahal untuk diulang. Citra satelit Sentinel-2 tersedia gratis, "
        "diakuisisi berulang secara berkala, dan beresolusi cukup untuk membedakan jenis tutupan lahan. "
        "Dipadukan dengan *machine learning*, citra ini memungkinkan pemetaan permukaan bumi yang otomatis "
        "dan dapat direproduksi.")

    st.subheader("Tujuan")
    st.markdown(
        "1. Memetakan permukaan bumi secara otomatis dari citra Sentinel-2 L2A ke dalam **lima kelas**: "
        "bangunan, lahan pertanian, badan air, hutan, dan hutan mangrove.\n"
        "2. Membedakan **mangrove dari hutan biasa**. Keduanya sama-sama hijau, tetapi respons band "
        "inframerah-gelombang-pendek (komposit B8A–B11–B4) berbeda.\n"
        "3. Mendukung pemantauan lahan, tata ruang, dan konservasi lewat peta interaktif, ringkasan luas "
        "per kelas, dan akurasi model yang transparan.")

    st.subheader("Pengguna dan manfaat")
    st.markdown(
        "| Pengguna | Manfaat yang diharapkan |\n|---|---|\n"
        "| **Pemerintah daerah** | Gambaran cepat tutupan lahan untuk tata ruang dan pemantauan alih fungsi lahan |\n"
        "| **Peneliti** | Dasar analisis perubahan tutupan lahan, alur kerja yang dapat diulang untuk wilayah lain |\n"
        "| **Masyarakat** | Informasi yang mudah diakses tentang kondisi lahan, termasuk sebaran mangrove |\n")

    st.subheader("Kelas klasifikasi")
    st.markdown(
        "| Kelas | Keterangan |\n|---|---|\n" +
        "\n".join(f"| {swatch(c['color'])}**{c['label']}** ({c['en']}) | {d} |" for c, d in zip(CLASSES, [
            "Permukiman, bangunan, dan permukaan buatan",
            "Sawah dan lahan pertanian",
            "Laut, danau, dan perairan lainnya",
            "Hutan daratan",
            "Hutan mangrove di pesisir",
        ])))

    st.subheader("Cakupan wilayah")
    w, s, e, n = PIPELINE["bbox"]
    st.info(
        "Konteks studi adalah **Jawa Timur**. Karena keterbatasan waktu dan data, sampel latih dan peta "
        "dibuat untuk **wilayah percontohan Banyuwangi dan sekitarnya** (mendekati Situbondo dan Lumajang), "
        f"yaitu kotak {w}°–{e}° BT dan {abs(n)}°–{abs(s)}° LS. Kotak ini juga memuat Selat Bali dan sedikit "
        "daratan Bali bagian barat, yang bukan wilayah Jawa Timur. Alur yang sama dapat diterapkan ke "
        "wilayah Jawa Timur lainnya dengan sampel latih tambahan.")

# ================================================================ TAB 2: alur & data
with tab_alur:
    st.header("Alur aplikasi")
    steps = [
        ("1 · Ambil data",
         f"Citra **{PIPELINE['sumber']}**, periode {PIPELINE['periode']}. Band: {PIPELINE['band']}."),
        ("2 · Proses",
         "Awan, bayangan awan, dan cirrus dibuang lewat band SCL. Median per piksel, resolusi dan CRS "
         f"diseragamkan ({PIPELINE['resolusi']}). Ditambah indeks {PIPELINE['indeks']}."),
        ("3 · Klasifikasi",
         f"Model **{metrics['model'] if metrics else 'XGBoost / Random Forest'}** dilatih dari poligon "
         "sampel hasil digitasi, diuji per poligon, lalu diterapkan ke seluruh raster."),
        ("4 · Tampilkan informasi",
         "Hasil diubah menjadi poligon GeoJSON per kelas, ditampilkan di peta interaktif beserta "
         "ringkasan luas dan akurasi."),
    ]
    for col, (title, text) in zip(st.columns(4), steps):
        with col.container(border=True):
            st.markdown(f"**{title}**")
            st.write(text)
    st.caption("Langkah 1–3 dijalankan di notebook (openEO dan Python). Aplikasi ini memuat hasilnya, "
               "sehingga cepat dan tidak membutuhkan akun atau kuota Copernicus.")

    with st.expander("Detail parameter"):
        st.json(PIPELINE)

    st.header("Data sampel latih")
    if metrics:
        pk = pd.Series(metrics.get("poligon_per_kelas", {}))
        names = {c["code"]: c["label"] for c in CLASSES}
        df_s = pd.DataFrame({"Kelas": [names.get(k, k) for k in pk.index], "Jumlah poligon": pk.values})
        c1, c2 = st.columns([1, 2])
        c1.dataframe(df_s, hide_index=True, width="stretch")
        def _fmt(v):
            return f"{v:,}".replace(",", ".") if isinstance(v, (int, float)) else "-"
        c1.caption(f"Piksel latih: {_fmt(metrics.get('piksel_latih'))} · piksel uji: {_fmt(metrics.get('piksel_uji'))}")
        with c2:
            show_image("tanda_spektral.png", "Tanda spektral rata-rata ± simpangan baku per kelas")
    else:
        st.warning("`data/metrics.json` belum ada.")

    st.header("Komposit B8A–B11–B4")
    show_image("perbandingan_komposit.png",
               "Contoh tiap kelas: warna alami, komposit tugas (B8A-B11-B4), dan vegetasi (B8-B4-B3)")

# ================================================================ TAB 3: peta
with tab_peta:
    st.header("Peta hasil klasifikasi")
    st.caption("Centang kelas yang ingin ditampilkan. Jika hanya satu kelas dicentang, hanya area kelas itu yang muncul.")

    selected = []
    for col, c in zip(st.columns(len(CLASSES)), CLASSES):
        with col:
            if st.checkbox(c["label"], value=True, key=f"cb_{c['code']}"):
                selected.append(c)
            st.markdown(swatch(c["color"]) + f"<small>{c['en']}</small>", unsafe_allow_html=True)

    o1, o2, o3 = st.columns(3)
    opacity = o1.slider("Transparansi layer", 0.1, 1.0, 0.6, 0.05)
    basemap = o2.radio("Peta dasar", ["Citra satelit", "Peta jalan"], horizontal=True)
    labels_on = o3.checkbox("Tampilkan nama tempat", value=True, disabled=(basemap != "Citra satelit"))

    bounds = meta.get("bounds") or [PIPELINE["bbox"][0], PIPELINE["bbox"][1], PIPELINE["bbox"][2], PIPELINE["bbox"][3]]
    w, s, e, n = bounds
    m = folium.Map(location=[(s + n) / 2, (w + e) / 2], zoom_start=9, tiles=None, control_scale=True)
    if basemap == "Citra satelit":
        folium.TileLayer(ESRI_IMAGERY, attr="Esri, Maxar, Earthstar Geographics", name="Citra satelit", max_zoom=19).add_to(m)
        if labels_on:
            folium.TileLayer(ESRI_LABELS, attr="Esri", name="Nama tempat", overlay=True, max_zoom=19).add_to(m)
    else:
        folium.TileLayer("OpenStreetMap", name="Peta jalan").add_to(m)

    missing = []
    for c in selected:
        data = load_layer(c["code"])
        if data is None:
            missing.append(c["label"])
            continue
        folium.GeoJson(
            data, name=c["label"],
            style_function=lambda f, col=c["color"], op=opacity: {
                "color": col, "weight": 0.6, "fillColor": col, "fillOpacity": op},
            tooltip=folium.GeoJsonTooltip(fields=["label", "luas_ha"], aliases=["Kelas", "Luas (ha)"]),
        ).add_to(m)
    m.fit_bounds([[s, w], [n, e]])
    if missing:
        st.warning("Layer belum tersedia: " + ", ".join(missing))
    if not selected:
        st.info("Belum ada kelas yang dicentang.")
    st_folium(m, height=650, use_container_width=True, returned_objects=[], key="peta")
    if meta:
        st.caption(f"Poligon pada peta disederhanakan agar ringan (bercak kecil kelas besar dibuang, "
                   f"≥ {meta.get('min_ha_kelas_besar', '-')} ha). Luas pada tab ringkasan dihitung dari raster penuh, "
                   "bukan dari poligon di peta.")

# ================================================================ TAB 4: ringkasan hasil
with tab_hasil:
    st.header("Ringkasan hasil")
    if metrics:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Akurasi (data uji)", f"{metrics['akurasi_uji'] * 100:.1f}%")
        m2.metric("F1 macro", f"{metrics['f1_macro_uji'] * 100:.1f}%")
        m3.metric("Model", metrics["model"])
        m4.metric("Jumlah poligon sampel", sum(metrics.get("poligon_per_kelas", {}).values()))
        st.caption("Data dibagi per poligon (bukan per piksel) agar piksel bertetangga tidak bocor "
                   "antara data latih dan data uji.")
    else:
        st.warning("`data/metrics.json` belum ada.")

    st.subheader("Luas per kelas")
    if area is not None:
        area = area.copy()
        area["luas_ha"] = (area["luas_km2"] * 100).round(0)
        color_of = {c["label"]: c["color"] for c in CLASSES}
        c1, c2 = st.columns([1, 1])
        with c1:
            st.dataframe(
                area.rename(columns={"kelas": "Kelas", "luas_km2": "Luas (km²)", "luas_ha": "Luas (ha)",
                                     "persen": "Persen (%)", "piksel": "Piksel"})
                    [["Kelas", "Luas (km²)", "Luas (ha)", "Persen (%)", "Piksel"]],
                hide_index=True, width="stretch")
        with c2:
            chart = (alt.Chart(area).mark_bar()
                     .encode(x=alt.X("kelas:N", sort=None, title=None, axis=alt.Axis(labelAngle=-20)),
                             y=alt.Y("luas_km2:Q", title="Luas (km²)"),
                             color=alt.Color("kelas:N", legend=None,
                                             scale=alt.Scale(domain=list(color_of), range=list(color_of.values()))),
                             tooltip=["kelas", "luas_km2", "persen"])
                     .properties(height=300))
            st.altair_chart(chart, width="stretch")
    else:
        st.warning("`data/luas_per_kelas.csv` belum ada.")

    if metrics:
        st.subheader("Evaluasi per kelas")
        rep = metrics.get("laporan", {})
        rows = [{"Kelas": c["label"], "Presisi": rep[c["label"]]["precision"], "Recall": rep[c["label"]]["recall"],
                 "F1": rep[c["label"]]["f1-score"], "Sampel uji (piksel)": int(rep[c["label"]]["support"])}
                for c in CLASSES if c["label"] in rep]
        if rows:
            df_r = pd.DataFrame(rows)
            st.dataframe(df_r.style.format({"Presisi": "{:.3f}", "Recall": "{:.3f}", "F1": "{:.3f}"}),
                         hide_index=True, width="stretch")
            worst = df_r.sort_values("F1").iloc[0]
        else:
            worst = None

        g1, g2 = st.columns(2)
        with g1:
            show_image("confusion_matrix.png", "Confusion matrix (data uji, per poligon)")
        with g2:
            show_image("feature_importance.png", "Kepentingan fitur")

        if metrics.get("cv"):
            st.subheader("Perbandingan model (cross-validation per poligon)")
            st.dataframe(pd.DataFrame(metrics["cv"]).rename(columns={
                "model": "Model", "akurasi_cv": "Akurasi CV", "std": "Std", "f1_macro_cv": "F1 macro CV"}),
                hide_index=True, width="stretch")

        st.subheader("Keterbatasan")
        lemah = (f"Kelas dengan F1 terendah adalah **{worst['Kelas']}** ({worst['F1']:.3f}). "
                 "Kelas ini paling sering tertukar dengan kelas bervegetasi lain. " if worst is not None else "")
        st.markdown(
            f"- Akurasi diukur pada poligon sampel yang bersih dan seragam, **bukan pada seluruh peta**. "
            f"Piksel campuran di lapangan cenderung lebih sulit.\n"
            f"- {lemah}\n"
            "- Hanya ada lima kelas. Tutupan lain (tanah terbuka, savana, kebun, bayangan, lahan vulkanik) "
            "terpaksa dimasukkan ke salah satu dari lima kelas itu.\n"
            "- Satu komposit musim kemarau (Juni–September 2026) tidak menangkap perubahan musiman, "
            "misalnya sawah berair, tanam, dan bera.\n"
            "- Resolusi 20 m: objek sempit (rumah tunggal, jalur mangrove tipis) tidak tertangkap.\n"
            "- Cakupan hanya wilayah percontohan, bukan seluruh Jawa Timur.")

st.divider()
st.caption("Data: Copernicus Sentinel-2 (ESA) · Peta dasar: Esri World Imagery, OpenStreetMap · "
           f"{APP['mk']}")
