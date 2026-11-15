# Bike Sharing Data Analysis Dashboard ✨

Proyek akhir kelas **Belajar Fundamental Analisis Data** (Dicoding) menggunakan *Bike Sharing Dataset* (2011–2012).

## Struktur Proyek
```
├── dashboard/
│   ├── dashboard.py      # aplikasi Streamlit
│   ├── main_data.csv     # data harian bersih
│   └── hour_data.csv     # data per jam bersih
├── data/
│   ├── day.csv
│   └── hour.csv
├── notebook.ipynb
├── requirements.txt
├── url.txt
└── README.md
```

## Setup Environment - Anaconda
```
conda create --name main-ds python=3.11
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
```
python -m venv venv
venv\Scripts\activate        # Windows  (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
```

## Run Streamlit App
```
streamlit run dashboard/dashboard.py
```
