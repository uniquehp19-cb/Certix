import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

    # Gmail sender credentials
    SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "")
    SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD", "")

    # Google Sheet
    GOOGLE_SHEET_KEY = os.environ.get("GOOGLE_SHEET_KEY", "")
    GOOGLE_CREDENTIALS_FILE = os.path.join(
        BASE_DIR, os.environ.get("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    )

    # Folders
    CERT_FOLDER = os.path.join(BASE_DIR, "certificates")
    FONT_PATH = os.path.join(BASE_DIR, "fonts", "GreatVibes-Regular.ttf")
    TEMPLATE_IMAGE = os.path.join(BASE_DIR, "static", "certificate_template.png")

    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]


os.makedirs(Config.CERT_FOLDER, exist_ok=True)
