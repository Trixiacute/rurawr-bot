# Discord Rich Presence untuk Bot

Fitur Rich Presence telah diimplementasikan untuk memberikan status dinamis pada bot Discord. Rich Presence memungkinkan bot untuk menampilkan informasi yang lebih detail dan menarik pada status online-nya.

## Fitur yang Ditambahkan

1. **Rotasi Status Otomatis**
   * Bot akan secara otomatis mengganti statusnya setiap 5 menit
   * Informasi status selalu diperbarui dengan data terbaru (jumlah server, pengguna, dll)

2. **Status yang Informatif**
   * Menampilkan jumlah server yang dilayani
   * Menampilkan jumlah pengguna total
   * Menampilkan uptime bot
   * Menampilkan versi bot

3. **Variasi Jenis Status**
   * `Playing` - Menunjukkan bot sedang bermain game
   * `Listening` - Menunjukkan bot sedang mendengarkan sesuatu
   * `Watching` - Menunjukkan bot sedang menonton sesuatu
   * `Competing` - Menunjukkan bot sedang berkompetisi

## Contoh Status

Bot akan menampilkan status-status berikut secara bergantian:

1. `Watching 25 server` - Menunjukkan jumlah server yang dilayani
2. `Listening !help` - Mengingatkan pengguna tentang command bantuan
3. `Playing Anime & Jadwal Imsakiyah` - Menunjukkan fitur utama bot
4. `Competing layanan terbaik` - Menampilkan uptime bot

## Cara Penggunaan

Status Rich Presence dimuat secara otomatis ketika bot dimulai. Kode ini telah diimplementasikan dalam file `rich_presence.py` dan terintegrasi dengan `main_refactored.py`.

## Kustomisasi

Untuk mengubah status yang ditampilkan, Anda dapat memodifikasi daftar `presence_list` di dalam class `RichPresence` dalam file `rich_presence.py`.

```python
self.presence_list = [
    {"type": "watching", "name": "{guilds} server", "details": "Melayani {users} pengguna"},
    {"type": "listening", "name": "{prefix}help", "details": "untuk bantuan"},
    {"type": "playing", "name": "Anime & Jadwal Imsakiyah", "details": "Versi {version}"},
    {"type": "competing", "name": "layanan terbaik", "details": "Uptime: {uptime}"}
]
```

## Format Placeholder

Anda dapat menggunakan berbagai placeholder dalam teks status:

* `{guilds}` - Jumlah server yang dilayani
* `{users}` - Jumlah total pengguna 
* `{commands}` - Jumlah command yang tersedia
* `{prefix}` - Prefix default bot
* `{uptime}` - Waktu bot telah berjalan
* `{version}` - Versi bot
* `{python}` - Versi Python
* `{discord}` - Versi Discord.py 