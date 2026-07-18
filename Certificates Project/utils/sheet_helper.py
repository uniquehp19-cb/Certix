import gspread
from google.oauth2.service_account import Credentials
from config import Config

_sheet_cache = None


def get_sheet():
    """Returns a cached gspread worksheet object (sheet1)."""
    global _sheet_cache
    if _sheet_cache is not None:
        return _sheet_cache

    creds = Credentials.from_service_account_file(
        Config.GOOGLE_CREDENTIALS_FILE, scopes=Config.SCOPES
    )
    client = gspread.authorize(creds)
    _sheet_cache = client.open_by_key(Config.GOOGLE_SHEET_KEY).sheet1
    return _sheet_cache


def get_all_data():
    """Returns list of dict rows from the sheet."""
    sheet = get_sheet()
    return sheet.get_all_records()


def add_row(name, age, email):
    sheet = get_sheet()
    sheet.append_row([name, age, email, ""])


def delete_row(row_number):
    sheet = get_sheet()
    sheet.delete_rows(row_number)


def update_status(row_index, status):
    """row_index here is the actual sheet row number (data row + 2, since
    row 1 is the header and gspread is 1-indexed)."""
    sheet = get_sheet()
    sheet.update_cell(row_index, 4, status)


def get_dashboard_stats():
    data = get_all_data()
    total = len(data)
    sent = invalid = pending = 0

    for row in data:
        status = str(row.get("Status", "")).strip()
        if status == "Sent":
            sent += 1
        elif status == "Invalid Email":
            invalid += 1
        else:
            pending += 1

    success_rate = round((sent / total) * 100, 2) if total > 0 else 0

    return {
        "total": total,
        "sent": sent,
        "invalid": invalid,
        "pending": pending,
        "success_rate": success_rate,
    }
