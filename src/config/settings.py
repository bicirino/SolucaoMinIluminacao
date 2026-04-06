import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
SRC_DIR = BASE_DIR / "src"
ASSETS_DIR = BASE_DIR / "assets"
LOGS_DIR = BASE_DIR / "logs"

# Criar diretório de logs se não existir
LOGS_DIR.mkdir(exist_ok=True)

# Google Cloud Vision
GOOGLE_CLOUD_CREDENTIALS_PATH = os.getenv(
    "GOOGLE_CLOUD_CREDENTIALS_PATH",
    str(BASE_DIR / "credentials.json")
)
GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID", "seu-projeto-id")

# WhatsApp Configuration
WHATSAPP_SESSION_PATH = os.getenv(
    "WHATSAPP_SESSION_PATH",
    str(BASE_DIR / "session")
)
WHATSAPP_DELAY_SECONDS = int(os.getenv("WHATSAPP_DELAY_SECONDS", "3"))

# Scheduler Configuration
SCHEDULER_ENABLED = os.getenv("SCHEDULER_ENABLED", "True").lower() == "true"
MESSAGE_ADVANCE_HOURS = int(os.getenv("MESSAGE_ADVANCE_HOURS", "12"))
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "30"))

# File Paths
CONTACTS_FILE_PATH = os.getenv(
    "CONTACTS_FILE_PATH",
    str(BASE_DIR / "contatos.json")
)
SCALE_IMAGE_PATH = os.getenv(
    "SCALE_IMAGE_PATH",
    str(ASSETS_DIR / "escala-mes.png")
)

# Scale Validation
SCALE_VALIDATION_FILE = os.getenv(
    "SCALE_VALIDATION_FILE",
    str(BASE_DIR / "escala_valida.json")
)

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", str(LOGS_DIR / "app.log"))

# Constants
TIMEZONE = "America/Sao_Paulo"
