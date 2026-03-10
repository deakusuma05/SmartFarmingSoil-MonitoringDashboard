
# Soil Moisture Monitoring Dashboard

Proyek ini menyajikan sistem pemantauan kelembaban tanah menggunakan data sensor.
Dashboard interaktif dibangun dengan Streamlit untuk visualisasi tren, distribusi,
dan korelasi kelembaban tanah.

## Struktur Repositori:

```
repo_github/
├── README.md
├── data/
│   └── raw/ 
│       └── *.CSV (file data mentah sensor)
├── Data_Lifecycle_Smart_Farming.ipynb 
├── dashboard/
│   └── streamlit_app.py
├── outputs/
│   ├── cleaned_data.csv
│   ├── analysis_report.pdf (Laporan Analisis - Placeholder)
│   └── dashboard_screenshot.png (Screenshot Dashboard - Placeholder)
└── requirements.txt
```

## Cara Menjalankan Dashboard (Lokal):

1.  Clone repositori ini.
2.  Navigasi ke folder `dashboard/`.
3.  Instal dependensi: `pip install -r ../requirements.txt`
4.  Jalankan aplikasi Streamlit: `streamlit run streamlit_app.py`

## Live Dashboard:

Aplikasi ini dideploy ke Streamlit Community Cloud dan dapat diakses di: [https://smartfarmingsoil-monitoringdashboard-deakusumaningrum.streamlit.app/]


