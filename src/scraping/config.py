"""
Configuration file for missing persons data scraping
Contains URLs, headers, and other constants used throughout the project
"""

import datetime
from selenium.webdriver.chrome.options import Options

# Date configuration
TODAY_DATE = datetime.date.today().strftime("%d%m%Y")

# Web scraping configuration
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Target URLs
BASE_URL = 'https://desaparecidosenperu.policia.gob.pe'
MISSING_ADULTS_URL = f'{BASE_URL}/Desaparecidos/mujer_desaparecido'
MISSING_MINORS_URL = f'{BASE_URL}/Desaparecidos/menor_desaparecido'
FOUND_PERSONS_URL = f'{BASE_URL}/Desaparecidos/UBICADOS'

# CSS selectors and XPath expressions
PHOTO_XPATH = '//img[contains(@src, "fotos_desaparecidos")]'
PHOTO_CSS_CLASS = 'adaptive-image foto-desa'

# HTML structure selectors
DETAIL_SECTION_CLASS = 'detalle-desaparecidos-p1'
AGENCY_SECTION_STYLE = 'font-family: arial; font-size: 20px; color: #174e75;'
AGENCY_HEADER_STYLE = 'font-family: arial; font-size: 20px; color: #000000; text-transform: uppercase;'
PERSON_DATA_STYLE = 'color: #174e75;'
BORDER_DIV_STYLE = 'border: 1px solid #949393; margin-bottom: 15px;'
ADDITIONAL_INFO_STYLE = 'font-family: arial; font-size: 20px; color: #174e75;'

# Chrome driver options
def get_chrome_driver_options():
    """Returns configured Chrome options for web scraping"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--incognito")
    return chrome_options

# Output paths
RAW_DATA_DIR = "data/raw"
PROCESSED_DATA_DIR = "data/processed"

# File naming patterns
MISSING_PERSONS_FILENAME = f"missing_persons_{TODAY_DATE}.csv"
FOUND_PERSONS_FILENAME = f"found_persons_{TODAY_DATE}.csv"

# CSV configuration
CSV_SEPARATOR = ';'
CSV_ENCODING = 'utf-8-sig'