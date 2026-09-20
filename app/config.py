from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
DATABASE_PATH = DATA_DIR / "kiosco.db"

APP_TITLE = "Kiosco Escolar - Control de Ventas"
LOW_STOCK_LIMIT = 5

