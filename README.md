# Missing-Persons Multimodal Pipeline

End-to-end toolkit for **scraping**, **cleaning & geocoding**, **multimodal clustering**, and **regression analysis** of Peruvian missing-person notices.  
Developed for academic research at Universidad del Pacífico (2025).

---

##  Project Layout

```
.
├── data/
│   ├── raw/          # HTML / CSV straight from the scraper
│   ├── interim/      # cleaned but not yet geocoded
│   └── processed/    # final dataset,
│   └── external/     # shapefile of peru
├── results/          # plots, metrics, checkpoints
├── src/
│   ├── scraping/     # main_scraper.py, web_scraper.py …
│   ├── preprocessing/# main_preprocessing.py …
│   ├── clustering/   # main_clustering.py …
│   └── regression/   # main_regression.py …
└── README.md
└── Notebooks         # How to use the code
```

Each stage has its own `main_<stage>.py` entry‑point plus a `config.py` holding tunable parameters.

---

##  Quick Start

### 1 · Set up a fresh environment

```bash
python -m venv .venv               # or: conda create -n missingpersons python=3.11
source .venv/bin/activate          # Windows ⇒ .venv\Scripts\activate
pip install -r requirements.txt
```

> **GeoPandas**  
> On bare‑metal Python you must install the GEOS & PROJ binaries first. With **conda** simply run  
> `conda install geopandas shapely pyproj fiona`

> **Selenium**  
> Download a **ChromeDriver** that matches your Chrome build and place it in your `PATH` (or in `drivers/`).

### 2 · Run the full pipeline

```bash
# 1) Scrape notices + face images
python -m src.scraping.main_scraper        --out_dir data/raw --delay 1

# 2) Clean, normalise, geocode
python -m src.preprocessing.main_preprocessing        --input     data/raw/notices.csv        --shapefile data/external/peru_districts.shp        --out_dir   data/processed

# 3) Multimodal clustering (GMM)
python -m src.clustering.main_clustering        --input data/processed/combined_geocoded.csv

# 4) Regression analysis
python -m src.regression.main_regression        --input data/processed/combined_geocoded.csv
```

All scripts expose `--help` for optional arguments (batch size, device, cache paths, etc.).


### Or run the interactive notebooks

Prefer a point-and-click workflow?  
Open the **`notebooks/`** folder and execute the notebooks in order:

1. **`01_scraping.ipynb`** – downloads notices and face images  
2. **`02_preprocessing.ipynb`** – cleaning, normalisation, geocoding  
3. **`03_clustering.ipynb`** – builds multimodal embeddings and GMM clusters  
4. **`04_regression.ipynb`** – trains the regression model and reports metrics  

The notebooks call the exact same functions as the CLI, save to the same `data/` and `results/` directories, and include extra visualisations and progress bars.

---

##  Key Configuration Knobs

| Stage | What to tweak (in `config.py`) |
|-------|--------------------------------|
| Scraping | `BASE_URL`, `HEADLESS`, `WAIT_TIME`, `SAVE_HTML` |
| Pre‑processing | regex patterns, `GEOCODE_CACHE`, `MAX_RETRIES` |
| Clustering | `GMM_PARAMS`, `EMBEDDING_MODEL`, `SAMPLE_PCT` |
| Regression | `TRAIN_SPLIT`, model hyper‑params, `RANDOM_SEED` |

---

##  Hardware Requirements

| Phase | CPU | GPU (optional) | RAM |
|-------|-----|----------------|-----|
| Scraper | low | – | ≤2 GB |
| Pre‑processing | medium | – | ≥4 GB |
| Embeddings & Clustering | medium | CUDA accelerates ResNet + Sentence‑BERT | ≥6 GB |
| Regression | low | optional | ≥4 GB |

---

##  Troubleshooting

| Symptom | Likely cause | Quick fix |
|---------|--------------|-----------|
| `SessionNotCreatedException` | ChromeDriver mismatch | Install driver matching your Chrome version |
| `ImportError: DLL load failed (geopandas)` | Missing GEOS / PROJ | Install via conda or your OS package manager |
| `CUDA out of memory` | GPU too small | Run on CPU (`--device cpu`) or reduce batch size |
| Photon API timeouts | Rate‑limit hit | Increase `--geocode-delay` or reuse cache |

---

##  License

If you build on this work, please cite the repository and any related publication.

---




