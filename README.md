# 🔍 Belt Monitor - System Monitorowania Taśmy Przenośnika

System do automatycznego monitorowania szerokości taśmy przenośnika z wykorzystaniem analizy obrazu (Computer Vision). Wykrywa segmenty taśmy (szwy) i generuje raporty o stanie technicznym.

## 🎯 Funkcjonalności

- **Analiza wideo/obrazów** - pomiar szerokości taśmy klatka po klatce
- **Detekcja segmentów** - automatyczne wykrywanie szwów/łączeń taśmy
- **Generowanie raportów** - Excel, CSV, JSON z min/max/avg szerokością per segment
- **REST API** - pełne API do integracji z innymi systemami
- **Alerty** - wykrywanie anomalii szerokości
- **Konteneryzacja** - gotowe obrazy Docker

## 🚀 Szybki Start

### Docker (zalecane)

```bash
# Sklonuj repozytorium

# Uruchom kontener
docker-compose up -d

# API dostępne pod http://localhost:8000
# Dokumentacja: http://localhost:8000/docs
```

### Lokalna instalacja

```bash
# Wymagania: Python 3.10+
python -m venv venv
source venv/bin/activate  # Linux/Mac
# lub: venv\Scripts\activate  # Windows

pip install -r requirements.txt

# Uruchom API
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```

## 📖 Użycie

### REST API

#### Analiza pliku wideo/obrazu

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -F "file=@video.mp4" \
  -F "min_width_threshold=100" \
  -F "sample_rate=5"
```

#### Pobranie raportu Excel

```bash
curl "http://localhost:8000/api/v1/reports/{analysis_id}/excel" \
  --output report.xlsx
```

#### Pobranie raportu CSV

```bash
curl "http://localhost:8000/api/v1/reports/{analysis_id}/csv" \
  --output report.csv
```

### CLI

```bash
# Analiza wideo
python main.py video.mp4 --output reports --format all

# Analiza obrazu
python main.py image.jpg --format csv --json-stdout

# Z ROI (Region of Interest)
python main.py video.mp4 --roi 100 50 400 300
```

## 📊 Format Raportu

### Struktura danych JSON

```json
{
  "source_file": "video.mp4",
  "total_frames": 1500,
  "fps": 30.0,
  "total_segments": 5,
  "segments": [
    {
      "segment_id": 1,
      "frame_start": 0,
      "frame_end": 300,
      "min_width_px": 485.5,
      "max_width_px": 502.3,
      "avg_width_px": 494.2,
      "measurement_count": 300
    }
  ],
  "alerts": [
    {
      "type": "width_warning",
      "frame": 245,
      "message": "Belt width below threshold",
      "severity": "warning"
    }
  ]
}
```

## 🔧 Konfiguracja

| Parametr | Opis | Domyślnie |
|----------|------|-----------|
| `min_width_threshold` | Minimalna oczekiwana szerokość (px) | 100 |
| `max_width_threshold` | Maksymalna oczekiwana szerokość (px) | 2000 |
| `seam_threshold` | Czułość detekcji szwów (0-1) | 0.3 |
| `sample_rate` | Przetwarzaj co N-tą klatkę | 1 |
| `roi` | Region of Interest (x, y, w, h) | None |

## 🏗️ Architektura

```
belt-monitor/
├── app/
│   ├── __init__.py
│   ├── api.py              # FastAPI REST API
│   ├── belt_analyzer.py    # Moduł CV do analizy taśmy
│   └── report_generator.py # Generator raportów
├── tests/
│   ├── test_analyzer.py
│   └── test_api.py
├── data/                   # Dane wejściowe
├── reports/                # Wygenerowane raporty
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── main.py                 # CLI entry point
```

## 📡 API Endpoints

| Endpoint | Metoda | Opis |
|----------|--------|------|
| `/health` | GET | Health check |
| `/api/v1/analyze` | POST | Analiza pliku wideo/obrazu |
| `/api/v1/results` | GET | Lista wszystkich analiz |
| `/api/v1/results/{id}` | GET | Szczegóły analizy |
| `/api/v1/reports/{id}/excel` | GET | Pobierz raport Excel |
| `/api/v1/reports/{id}/csv` | GET | Pobierz raport CSV |
| `/api/v1/reports/{id}/json` | GET | Pobierz raport JSON |

Pełna dokumentacja API: `http://localhost:8000/docs`

## 🧪 Testy

```bash
# Uruchom testy
pytest tests/ -v

# Z coverage
pytest tests/ --cov=app --cov-report=html
```

## 📋 Wymagania

- Python 3.10+
- OpenCV 4.9+
- FastAPI 0.109+
- Docker (opcjonalnie)

## 🔒 Bezpieczeństwo

- Wszystkie dane przetwarzane lokalnie (on-premise)
- Brak zewnętrznych zależności sieciowych podczas analizy
- Wspiera TLS dla komunikacji API
- Gotowe do integracji z systemami uwierzytelniania

## 📄 Licencja

Open Source - MIT License

## 👥 Zespół

Projekt stworzony na hackathon JSW IT Systems.

## 📞 Kontakt

- Robert Zając: 605 092 402
- Jacek Garus: 605 747 595
- Konrad Wesenfeld: 605 091 074
