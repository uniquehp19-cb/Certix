import threading
import time
from datetime import datetime

from utils import sheet_helper
from utils.certificate_generator import generate_certificate
from utils.email_sender import send_email

# Simple in-memory job tracker so the UI can poll progress.
job_status = {
    "running": False,
    "log": [],
    "sent": 0,
    "skipped": 0,
    "total": 0,
    "finished": False,
    "scheduled_for": None,
}

_lock = threading.Lock()


def _log(message):
    with _lock:
        job_status["log"].append(message)
        if len(job_status["log"]) > 300:
            job_status["log"] = job_status["log"][-300:]


def reset_job_status():
    with _lock:
        job_status.update(
            {
                "running": False,
                "log": [],
                "sent": 0,
                "skipped": 0,
                "total": 0,
                "finished": False,
                "scheduled_for": None,
            }
        )


def generate_all_certificates():
    """Generates certificates for every row in the sheet. Returns count."""
    data = sheet_helper.get_all_data()
    count = 0
    for row in data:
        name = str(row.get("Name", "")).strip()
        if name:
            generate_certificate(name)
            count += 1
    return count


def process_and_send():
    """Mirrors the original process_and_send(): generates a certificate
    for each pending row and emails it, updating the sheet Status column."""
    reset_job_status()
    job_status["running"] = True

    data = sheet_helper.get_all_data()
    job_status["total"] = len(data)

    sent = 0
    skipped = 0

    for i, row in enumerate(data, start=2):
        name = str(row.get("Name", "")).strip()
        email = str(row.get("Email", "")).strip()
        status = str(row.get("Status", "")).strip()

        if status == "Sent":
            _log(f"Skipping {name} — already sent")
            continue

        if not email or "@" not in email:
            _log(f"Skipping invalid email for {name}: '{email}'")
            sheet_helper.update_status(i, "Invalid Email")
            skipped += 1
            continue

        try:
            pdf_path = generate_certificate(name)
            ok, info = send_email(email, name, pdf_path)

            if ok:
                sheet_helper.update_status(i, "Sent")
                sent += 1
                _log(f"Sent certificate to {name} ({email})")
            else:
                sheet_helper.update_status(i, "Failed")
                skipped += 1
                _log(f"Failed to send to {name} ({email}): {info}")
        except Exception as e:
            skipped += 1
            _log(f"Error processing {name}: {e}")

        job_status["sent"] = sent
        job_status["skipped"] = skipped

    job_status["running"] = False
    job_status["finished"] = True
    _log(f"Done. Sent: {sent}, Skipped: {skipped}")
    return sent, skipped


def run_process_in_background():
    """Runs process_and_send() in a separate thread so the web request
    returns immediately and the UI can poll for progress."""
    thread = threading.Thread(target=process_and_send, daemon=True)
    thread.start()


def schedule_send(target_time_str):
    """target_time_str format: 'HH:MM' (24-hour). Waits in a background
    thread until that time, then runs process_and_send()."""
    reset_job_status()
    job_status["scheduled_for"] = target_time_str

    def _wait_and_run():
        _log(f"Waiting until {target_time_str} to start sending...")
        while True:
            now = datetime.now().strftime("%H:%M")
            if now == target_time_str:
                _log(f"{target_time_str} reached — starting process.")
                process_and_send()
                break
            time.sleep(15)

    thread = threading.Thread(target=_wait_and_run, daemon=True)
    thread.start()
