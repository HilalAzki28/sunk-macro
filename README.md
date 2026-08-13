# SunK Macro

**SunK Macro** adalah aplikasi desktop modern berbasis Python untuk merekam dan memutar kembali (playback) aksi mouse dan keyboard. Aplikasi ini dilengkapi dengan antarmuka grafis (GUI) yang elegan menggunakan `customtkinter` serta dukung global hotkeys sehingga mudah dikontrol meskipun jendela aplikasi sedang tidak aktif (minimized atau di latar belakang).

---

## Fitur Utama

- **Perekaman Aksi Presisi**: Merekam gerakan mouse, klik mouse, scroll, serta penekanan tombol keyboard dengan ketepatan waktu tinggi.
- **Global Hotkeys**:
  - `F8`: Mulai / Berhenti Perekaman.
  - `F9`: Mulai / Berhenti Pemutaran (Playback).
- **Pengaturan Kecepatan**: Putar kembali aksi yang direkam dengan kecepatan yang dapat disesuaikan (misal: 0.5x, 1x, 2x, dll.).
- **Opsi Perulangan & Interval**: Mengatur berapa kali makro diputar (looping) serta jeda waktu antar perulangan.
- **Simpan & Muat Makro**: Simpan rekaman aksi ke dalam file berformat `.json` agar dapat digunakan kembali kapan saja.
- **Log Realtime**: Panel sebelah kanan menampilkan detail urutan event yang sedang direkam atau diputar secara langsung.
- **Tampilan Modern**: Tema gelap (Dark Mode) bawaan yang nyaman di mata.

---

## Prasyarat & Instalasi

Pastikan Anda telah menginstal **Python 3.8** atau versi yang lebih baru di sistem Anda.

1. **Klon atau Unduh Repositori Ini**:
   ```bash
   git clone https://github.com/HilalAzki28/sunk-macro.git
   cd sunk-macro
   ```

2. **Instal Dependensi**:
   Instal library Python yang diperlukan menggunakan perintah berikut:
   ```bash
   pip install -r requirements.txt
   ```

---

## Cara Menjalankan Aplikasi

Jalankan skrip utama `main.py` menggunakan Python:

```bash
python main.py
```

---

## Cara Membuat Executable (.exe) Standalone

Proyek ini dilengkapi dengan skrip otomatis `build.py` untuk mengemas aplikasi menjadi file `.exe` tunggal yang dapat dijalankan secara langsung tanpa memerlukan instalasi Python.

Untuk membuat file executable:
1. Jalankan perintah berikut di terminal:
   ```bash
   python build.py
   ```
2. Skrip ini akan secara otomatis:
   - Menginstal `PyInstaller` jika belum terpasapng.
   - Mengompilasi kode program menjadi file binary tunggal (`SunK Macro.exe`).
   - Menyalin file `.exe` yang berhasil dibuat langsung ke **Desktop** Anda agar mudah diakses.

---

## Struktur Proyek

- `main.py`: Titik masuk utama (Entry Point) aplikasi. Menginisialisasi GUI dan listener keyboard global.
- `build.py`: Skrip build otomatis menggunakan PyInstaller.
- `requirements.txt`: Daftar dependensi modul Python.
- `src/`: Direktori kode sumber utama aplikasi:
  - `gui.py`: Logika antarmuka pengguna (CustomTkinter) dan penataan tata letak layout.
  - `player.py`: Modul pemutaran kembali (playback) aksi yang direkam.
  - `recorder.py`: Modul perekam input mouse dan keyboard menggunakan `pynput`.
  - `utils.py`: Fungsi pembantu untuk pemrosesan file JSON dan serialisasi event.
