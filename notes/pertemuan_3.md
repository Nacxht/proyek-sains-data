# Pertemuan 3

## Catatan

- Memperbaiki kualitas data sebelum melakukan ekstraksi fitur
- Setelah data understanding, adalah melakukan data preprocessing
- Salah satunya adalah interpolasi (interpolation), yaitu sebuah teknik untuk mengisi missing value dengan memperkirakan nilainya dari data diantara/disekitarnya. Terdapat beberapa metode interpolation:
    - Linear
    - Polynomial
    - Spline
- Teknik imputasi merupakan proses mengganti atau mengisi missing value dengan suatu metode
- Identifikasi outlier sebelum melakukan imputasi atau menangani missing value
- Teknik deteksi outlier:
    - IQR (Interquartile Range)
    - Z-Score
    - Box Plot
    - Scatter Plot
    - DBSCAN
    - Isolation Forest
    - KNN/Distance-Based Detection
- Setelah identifikasi outlier, selanjutnya adalah menangani outlier. Bisa diperbaiki atau dihapus, tergantung dari kondisi
- Ekstraksi fitur hanya bisa dilakukan jika data sudah bersih
- Ekstraksi fitur dilakukan untuk menghasillkan ratusan angka, fitur statistik, temporal, dan spektrak seketika
- 3 domain utama ekstraksi
    - Domain statistik
    - Domain temporal
    - Domain spektral

## Library Baru

- TSFEL

## Tugas/Todo

- Modifikasi daerah dari tugas 1 menjadi tingkat kecamatan, dan tidak boleh ada yang sama
- Lakukan untuk 1 polutan saja dahulu (CO / Carbon Monoxide)
- Menangani missing values dengan teknik imputasi (imputation)
- Setelah itu, identifikasi outlier
- Setelah ditemukan outlier, perbaiki outlier yang ditemukan
- Data yang sebanyak 365 (hari) diekstrak fiturnya menggunakan setiap fitur yang disediakan oleh library TSFEL sebagai perwakilan, dengan rangkaian tabel:
    - [nama_fitur] (ke-1/f1)
    - [nama_fitur] (ke-2/f2)
    - [nama_fitur] (ke-68/f3)
    - ...
    - [nama_fitur] (ke-68/f68)
- Mencari kemiripan CO2
- Pelajari dari masing-masing fitur yang disediakan. Termasuk:
    - Definisi
    - Cara kerja
    - Cara menghitung
    - Rumus
- Jika ada yang tidak dipahami bisa ditanyakan minggu depan
- Pahami juga makna dari masing-masing 68 fitur yang telah dibuat sebelumnya
