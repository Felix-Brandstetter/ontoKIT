import os
import logging
from dotenv import load_dotenv

# Laden der Umgebungsvariablen aus der .env-Datei
load_dotenv()

# Extrahieren des Logging-Levels aus den Umgebungsvariablen
log_level = os.getenv("LOGLEVEL", "WARNING").upper()  # Standardwert ist WARNING
logging.getLogger().setLevel(log_level)
