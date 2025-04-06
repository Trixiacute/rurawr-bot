# Rurawr Discord Bot

Bot Discord multifungsi dengan fitur anime dan jadwal imsakiyah.

## Struktur File

Struktur file dalam project ini telah diorganisir untuk memudahkan pengembangan dan pemeliharaan:

```
rurawr-bot/
├── main.py                # Entry point utama
├── .env                   # File konfigurasi environment variables
├── README.md              # Dokumentasi project
└── src/                   # Source code
    ├── commands/          # Command bot
    │   ├── general/       # Command-command umum
    │   │   ├── help.py    # Command help
    │   │   ├── info.py    # Command info
    │   │   ├── invite.py  # Command invite
    │   │   ├── ping.py    # Command ping
    │   │   └── stats.py   # Command stats
    │   ├── anime/         # Command-command terkait anime
    │   │   ├── anime.py   # Command anime
    │   │   └── waifu.py   # Command waifu
    │   ├── islamic/       # Command-command terkait islami
    │   │   └── imsakiyah.py # Command imsakiyah
    │   └── settings/      # Command-command pengaturan
    │       ├── language.py # Command language
    │       └── prefix.py  # Command prefix
    ├── core/              # Komponen inti bot
    │   ├── bot.py         # Inisialisasi bot utama
    │   ├── config.py      # Konfigurasi bot
    │   ├── database.py    # Pengelolaan database
    │   └── presence.py    # Fitur Rich Presence Discord
    ├── utils/             # Fungsi utilitas
    │   └── helper.py      # Fungsi helper/pembantu
    └── data/              # Data yang disimpan oleh bot
        └── database.json  # File database
```

## Fitur

- **Fitur Anime**
  - Pencarian informasi anime
  - Kirim gambar waifu acak
  
- **Fitur Islami**
  - Jadwal imsakiyah
  
- **Pengaturan Server**
  - Ubah prefix perintah
  - Ubah bahasa bot
  
- **Fitur Lainnya**
  - Discord Rich Presence yang dinamis
  - Help menu yang informatif
  - Statistik penggunaan bot

## Cara Penggunaan

1. Clone repository ini
2. Buat file `.env` dengan isi:
```
DISCORD_TOKEN=token_bot_anda_disini
```
3. Install dependencies:
```
pip install -r requirements.txt
```
4. Jalankan bot:
```
python main.py
```

## Rich Presence

Bot ini memiliki fitur Discord Rich Presence yang dinamis. Status bot akan berganti secara otomatis setiap 5 menit, menampilkan:

- Jumlah server yang dilayani
- Jumlah user yang menggunakan bot
- Uptime bot
- Versi bot

## Perintah

Gunakan `!help` untuk melihat daftar perintah yang tersedia.

## Requirements

- Python 3.8+
- discord.py 2.0+
- requests
- python-dotenv 