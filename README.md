# 🔧 Service & Diagnosa Motor

Aplikasi web untuk penjadwalan servis dan diagnosa kendaraan bermotor (motor & mobil).

## ✨ Fitur

- 📅 **Penjadwalan Servis** – Hitung kapan waktu ganti oli & servis berikutnya berdasarkan odometer dan tanggal terakhir servis
- 🔍 **Diagnosa Keluhan** – Analisis keluhan kendaraan dengan rekomendasi perbaikan dan estimasi biaya
- 💾 **Simpan Riwayat** – Simpan tiket servis per plat nomor kendaraan
- 📋 **Lacak Riwayat** – Lacak riwayat servis berdasarkan nomor plat

## 🚀 Cara Menjalankan Lokal

```bash
# Clone repo
git clone https://github.com/Kyp1277/service-and-diagnosa-motor.git
cd service-and-diagnosa-motor

# Install dependencies
pip install -r requirements.txt

# Jalankan aplikasi
python app.py
```

Buka browser ke `http://localhost:5000`

## 🌐 Demo Online

👉 [https://huggingface.co/spaces/kypli/service](https://huggingface.co/spaces/kypli/service)

## 🛠️ Teknologi

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript (Vanilla)

## 📁 Struktur Proyek

```
├── app.py                 # Main Flask application
├── database.py            # Database operations (SQLite)
├── diagnostic_engine.py   # Engine diagnosa keluhan kendaraan
├── requirements.txt       # Python dependencies
├── static/
│   ├── css/style.css      # Styling
│   └── js/app.js          # Frontend logic
└── templates/
    └── index.html         # Main HTML template
```
