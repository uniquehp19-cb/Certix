import os
from datetime import datetime
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from config import Config

_font_registered = False


def _ensure_font():
    global _font_registered
    if not _font_registered:
        if os.path.exists(Config.FONT_PATH):
            pdfmetrics.registerFont(TTFont("GreatVibes", Config.FONT_PATH))
        _font_registered = True


def generate_certificate(name):
    """Generates a certificate PDF for the given name and returns its path."""
    _ensure_font()

    safe_name = name.replace("/", "_")
    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    path = os.path.join(Config.CERT_FOLDER, f"{safe_name}_{timestamp}.pdf")

    c = canvas.Canvas(path, pagesize=landscape(A4))
    width, height = landscape(A4)

    if os.path.exists(Config.TEMPLATE_IMAGE):
        c.drawImage(Config.TEMPLATE_IMAGE, 0, 0, width=width, height=height)

    c.setFillColor(colors.HexColor("#222222"))

    font_name = "GreatVibes" if "GreatVibes" in pdfmetrics.getRegisteredFontNames() else "Helvetica-Bold"
    c.setFont(font_name, 46)
    c.drawCentredString(width / 2, 240, name.title())

    today = datetime.now().strftime("%d-%m-%Y")
    c.setFont("Helvetica", 12)
    c.drawString(100, 80, today)

    c.save()
    return path
