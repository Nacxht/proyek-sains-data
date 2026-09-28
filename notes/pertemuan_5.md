# Pertemuan 5

## Catatan

- Breakdown Perhitungan Manual Interpolasi (Interpolation)
  - Linear Interpolation
  - Polynomial Interpolation
- Implementasi Kelas
- Pengenalan Klasifikasi di Citra Satelit
  - Menampilkan visual QGIS (aplikasi) sekilas
  - Land Use & Land Cover
  - Sentinel-2A

## Tugas:

### Interpolasi Polinomial

- Mulai ulang dari data hasil tugas 1
- Mengimplementasikan Interpolasi Polinomial
- Setelah itu dilakukan ekstraksi fitur menggunakan TSFEL
- Digabungkan lagi

Note:
> Intinya sama kayak tugas sebelumnya. Bedanya, interpolasi di tugas ini menggunakan interpolasi polinomial.

### Citra Satelit (Sentinel-2A)

- Praktek Klasifikasi Citra Satelit
  - Menandai AoI (Area of Interests), spesifiknya hanya "sawah"
    - Menggunakan geojson.io
    - Di daerah kecamatan masing-masing
    - Kelas "sawah", ada 50 data
    - Kelas "bukan sawah", ada 50 data
  - Mengambil citra satelit menggunakan Sentinel-2A dari AoI yang sudah ditandai sebelumnya
  - Membuat output .tif sebagai hasil akhir
  - Tinggal modifikasi source code yang sudah di share sebelumnya
