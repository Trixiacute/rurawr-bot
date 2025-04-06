# Refaktorisasi Bot Discord

Repositori ini telah direfaktorisasi untuk memisahkan fungsi-fungsi dan logika program ke dalam beberapa file terpisah. Berikut adalah penjelasan mengenai struktur kode yang baru:

## Struktur File

1. **main_refactored.py** - File utama yang digunakan sebagai entrypoint bot, lebih bersih dan terorganisir
2. **memory_db.py** - Modul untuk penanganan database dalam memori
3. **utils.py** - Berisi fungsi-fungsi utilitas yang digunakan di seluruh aplikasi
4. **mal.py** - Berisi kode untuk fitur pencarian anime
5. **imsakiyah.py** - Berisi kode untuk fitur jadwal imsakiyah
6. **constants.py** - Berisi konstanta-konstanta yang digunakan di seluruh aplikasi

## Perubahan yang Dilakukan

### 1. Pemisahan Fungsi dan Modul

- **Database Memory**: Memindahkan semua fungsi terkait penyimpanan data ke dalam file `memory_db.py`
- **Utilitas**: Fungsi-fungsi pembantu seperti get_prefix, get_lang, log_command dipindahkan ke `utils.py`
- **Anime Module**: Fungsi pencarian anime dipindahkan ke `mal.py`
- **Imsakiyah Module**: Fungsi jadwal imsakiyah sudah ada di `imsakiyah.py`

### 2. Penerapan Prinsip Single Responsibility

Setiap modul sekarang memiliki tanggung jawab yang jelas:
- `memory_db.py` - Menyimpan dan mengelola data
- `utils.py` - Fungsi-fungsi pembantu
- `mal.py` - Pencarian dan tampilan anime
- `imsakiyah.py` - Fitur jadwal imsakiyah
- `main_refactored.py` - Inisialisasi bot dan command dasar

### 3. Pengurangan Ukuran File

- `main.py` asli: 2498 baris
- `main_refactored.py` baru: ~350 baris

### 4. Import Terorganisir

Setiap file kini memiliki import yang lebih terorganisir dan hanya mengimpor modul yang diperlukan.

### 5. Peningkatan Dokumentasi

Semua fungsi dan class kini memiliki docstring yang menjelaskan tujuan dan penggunaannya.

## Cara Penggunaan

Untuk menjalankan bot yang telah direfaktorisasi:

```bash
python main_refactored.py
```

Pastikan semua file berada dalam direktori yang sama dan dependensi telah terpasang dengan benar.

## Keuntungan Refaktorisasi

1. **Maintainability**: Kode lebih mudah dikelola karena terpisah ke dalam modul-modul yang lebih kecil
2. **Readability**: Kode lebih mudah dibaca karena tidak terlalu panjang dan memiliki dokumentasi yang lebih baik
3. **Extensibility**: Lebih mudah untuk menambahkan fitur baru tanpa memodifikasi seluruh codebase
4. **Testability**: Modul-modul terpisah lebih mudah untuk diuji secara independen
5. **Collaboration**: Memudahkan kolaborasi karena developer dapat bekerja pada file yang berbeda secara bersamaan 