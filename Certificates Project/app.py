import os
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, jsonify, send_file
)

from config import Config
from utils import sheet_helper, processor
from utils.certificate_generator import generate_certificate

app = Flask(__name__)
app.config.from_object(Config)


@app.errorhandler(Exception)
def handle_error(e):
    """Catches Google Sheet / credential errors so the UI never crashes hard."""
    flash(f"Something went wrong: {e}", "error")
    return redirect(url_for("dashboard"))


@app.route("/")
def dashboard():
    try:
        stats = sheet_helper.get_dashboard_stats()
    except Exception as e:
        stats = {"total": 0, "sent": 0, "invalid": 0, "pending": 0, "success_rate": 0}
        flash(f"Could not load sheet data: {e}", "error")
    return render_template("dashboard.html", stats=stats)


@app.route("/add", methods=["GET", "POST"])
def add_data():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        age = request.form.get("age", "").strip()
        email = request.form.get("email", "").strip()

        if not name or not age or not email:
            flash("All fields are required.", "error")
            return redirect(url_for("add_data"))

        try:
            sheet_helper.add_row(name, int(age), email)
            flash(f"{name} added successfully!", "success")
        except Exception as e:
            flash(f"Failed to add row: {e}", "error")

        return redirect(url_for("add_data"))

    return render_template("add_data.html")


@app.route("/view")
def view_data():
    try:
        data = sheet_helper.get_all_data()
    except Exception as e:
        data = []
        flash(f"Could not load sheet: {e}", "error")
    return render_template("view_data.html", data=data)


@app.route("/delete", methods=["GET", "POST"])
def delete_row():
    if request.method == "POST":
        row_number = request.form.get("row_number", "").strip()
        try:
            row_number = int(row_number)
            sheet_helper.delete_row(row_number)
            flash(f"Row {row_number} deleted successfully.", "success")
        except Exception as e:
            flash(f"Failed to delete row: {e}", "error")
        return redirect(url_for("delete_row"))

    try:
        data = sheet_helper.get_all_data()
    except Exception:
        data = []
    return render_template("delete_row.html", data=data)


@app.route("/generate", methods=["GET", "POST"])
def generate_certificates():
    if request.method == "POST":
        try:
            count = processor.generate_all_certificates()
            flash(f"{count} certificate(s) generated successfully!", "success")
        except Exception as e:
            flash(f"Certificate generation failed: {e}", "error")
        return redirect(url_for("generate_certificates"))

    certs = []
    if os.path.exists(Config.CERT_FOLDER):
        certs = sorted(os.listdir(Config.CERT_FOLDER), reverse=True)
    return render_template("generate_certificates.html", certs=certs)


@app.route("/certificates/<filename>")
def download_certificate(filename):
    path = os.path.join(Config.CERT_FOLDER, filename)
    if not os.path.exists(path):
        flash("Certificate not found.", "error")
        return redirect(url_for("generate_certificates"))
    return send_file(path, as_attachment=True)


@app.route("/send", methods=["GET", "POST"])
def send_emails():
    if request.method == "POST":
        if processor.job_status["running"]:
            flash("A send job is already running.", "error")
        else:
            processor.run_process_in_background()
            flash("Sending started in the background — watch the live log below.", "success")
        return redirect(url_for("send_emails"))

    return render_template("send_emails.html")


@app.route("/schedule", methods=["GET", "POST"])
def schedule_emails():
    if request.method == "POST":
        target_time = request.form.get("target_time", "").strip()
        if processor.job_status["running"] or processor.job_status.get("scheduled_for"):
            flash("A send/schedule job is already active.", "error")
        elif not target_time:
            flash("Please choose a time.", "error")
        else:
            processor.schedule_send(target_time)
            flash(f"Emails scheduled for {target_time}. Keep this app running.", "success")
        return redirect(url_for("schedule_emails"))

    return render_template("schedule_emails.html")


@app.route("/job-status")
def job_status_api():
    """Polled by JS to show live progress on Send/Schedule pages."""
    return jsonify(processor.job_status)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
