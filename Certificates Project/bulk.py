import os
import time
import smtplib
import gspread
from datetime import datetime
from email.message import EmailMessage
from google.oauth2.service_account import Credentials
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# REGISTER FONT HERE
pdfmetrics.registerFont(
    TTFont("GreatVibes", "GreatVibes-Regular.ttf")
)

print("GreatVibes font loaded")

# -----------------------------
# SETTINGS
# -----------------------------

SENDER_EMAIL = "kitegamified@gmail.com"
SENDER_PASSWORD = "pvez czim qdoc bzof"

CERT_FOLDER = "certificates"
if not os.path.exists(CERT_FOLDER):
    os.makedirs(CERT_FOLDER)

# -----------------------------
# TIME ALARM FUNCTION (FIXED)
# -----------------------------

def wait_until_time(target_time):

    try:
        # -----------------------
        # Validate input format
        # -----------------------
        if not target_time or ":" not in target_time:
            print("❌ Invalid time format. Use HH:MM (e.g. 10:30)")
            return

        print(f"⏳ Waiting for {target_time}...")

        while True:
            try:
                now = datetime.now().strftime("%H:%M")

                if now == target_time:
                    print(f"✅ {target_time} reached! Starting process...")
                    break

                time.sleep(20)

            except Exception as e:
                print(f"⚠ Time loop error: {e}")
                time.sleep(5)
                continue

    except Exception as e:
        print(f"❌ Wait function failed: {e}")


# =========================
# GOOGLE SHEETS CONFIG
# =========================
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def connect_sheet():
    try:
        # =========================
        # AUTHENTICATION
        # =========================
        creds = Credentials.from_service_account_file(
            "credentials.json",
            scopes=SCOPES
        )

        client = gspread.authorize(creds)

        # IMPORTANT: set timeout for stability
        client.session.timeout = 30

        SPREADSHEET_ID = "1fm-xMzXBDmHIXewo7V0U8uBKEEGpbtMMURz1SG1FXcY"

        # =========================
        # RETRY LOGIC (VERY IMPORTANT)
        # =========================
        sheet = None

        for i in range(5):
            try:
                print(f"🔄 Connecting to Google Sheet... attempt {i+1}")

                sheet = client.open_by_key(SPREADSHEET_ID).sheet1

                print("✅ Google Sheet connected successfully!")
                return sheet

            except Exception as e:
                print(f"❌ Attempt {i+1} failed:", e)
                time.sleep(5)

        raise Exception("❌ Failed to connect to Google Sheet after multiple retries")

    except Exception as e:
        print("❌ Critical error in Google Sheets setup:", e)
        return None


# =========================
# USAGE
# =========================
sheet = connect_sheet()

if sheet:
    print("🚀 Ready to use Google Sheet")
else:
    print("⚠ Google Sheet connection failed")

# -----------------------------
# CERTIFICATE GENERATOR
# -----------------------------

def generate_certificate(name):

    try:
        if not name or not name.strip():
            print("❌ Empty name skipped")
            return None

        safe_name = name.replace("/", "_").replace("\\", "_").strip()
        timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

        path = os.path.join(CERT_FOLDER, f"{safe_name}_{timestamp}.pdf")

        print("📄 Generating:", path)

        # =========================
        # PAGE SETUP
        # =========================
        c = canvas.Canvas(path, pagesize=landscape(A4))
        width, height = landscape(A4)

        # =========================
        # BACKGROUND TEMPLATE
        # =========================
        bg_path = "certificate_template.png"
        if os.path.exists(bg_path):
            c.drawImage(bg_path, 0, 0, width=width, height=height)

        # =========================
        # 🔥 DEBUG GUIDE LINE (REMOVE LATER IF YOU WANT)
        # =========================
        GUIDE_Y = 200  # 👈 CHANGE THIS ONLY UNTIL IT MATCHES YOUR LINE

        c.setStrokeColor(colors.red)
        c.setLineWidth(2)
        c.line(0, GUIDE_Y, width, GUIDE_Y)

        # =========================
        # NAME POSITION (LOCKED TO GUIDE)
        # =========================
        NAME_X = width / 2
        NAME_Y = 165

        c.setStrokeColor(colors.red)
        c.line(0, NAME_Y, width, NAME_Y)

        c.setFont("GreatVibes", 48)
        c.setFillColor(colors.HexColor("#1A1A1A"))

        c.drawCentredString(
            NAME_X,
            NAME_Y,
            name.title()
        )

        # =========================
        # DATE
        # =========================
        today = datetime.now().strftime("%d-%m-%Y")

        c.setFont("Helvetica", 11)
        c.setFillColor(colors.black)

        c.drawRightString(
            width - 80,
            60,
            f"Date: {today}"
        )

        c.save()
        return path

    except Exception as e:
        print(f"❌ Certificate generation failed for {name}: {e}")
        return None

# -----------------------------
# EMAIL FUNCTION
# -----------------------------

def send_email(receiver_email, name, file_path):

    try:
        # -----------------------
        # Email validation
        # -----------------------
        if not receiver_email or "@" not in receiver_email:
            print(f"❌ Skipping invalid email: {receiver_email}")
            return

        # -----------------------
        # Check file exists
        # -----------------------
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return

        # -----------------------
        # Create email
        # -----------------------
        msg = EmailMessage()
        msg["Subject"] = f"🎓 Certificate of Participation - {name}"
        msg["From"] = SENDER_EMAIL
        msg["To"] = receiver_email

        msg.set_content(
            f"Congratulations {name}! Your certificate is attached."
        )

        msg.add_alternative(f"""
        <html>
        <body>

        <h2>🎉 Congratulations {name}!</h2>

        <p>We are pleased to inform you that your certificate has been successfully generated.</p>

        <p>Please find your certificate attached to this email.</p>

        <p>Thank you for your participation and support.</p>

        <br>

        <p>Best Regards,<br>
        <b>KITE Team</b></p>

        </body>
        </html>
        """, subtype="html")

        # -----------------------
        # Attach file safely
        # -----------------------
        with open(file_path, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="pdf",
                filename=os.path.basename(file_path)
            )

        # -----------------------
        # Send email safely
        # -----------------------
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
                smtp.send_message(msg)

            print(f"✅ Email sent to {receiver_email}")

        except smtplib.SMTPAuthenticationError:
            print("❌ Gmail login failed (check app password)")
        except smtplib.SMTPException as e:
            print(f"❌ SMTP error: {e}")
        except Exception as e:
            print(f"❌ Unexpected email error: {e}")

    except Exception as e:
        print(f"❌ Function error for {receiver_email}: {e}")

# -----------------------------
# BULK PROCESS
# -----------------------------

def process_and_send():
    data = sheet.get_all_records()

    sent = 0
    skipped = 0
    failed = 0

    for i, row in enumerate(data, start=2):

        try:
            name = row.get("Name", "").strip()
            email = row.get("Email", "").strip()
            status = row.get("Status", "").strip()

            # -----------------------
            # Already sent check
            # -----------------------
            if status == "Sent":
                print(f"⏩ Skipping {name} - Already Sent")
                continue

            # -----------------------
            # Email validation
            # -----------------------
            if not email or "@" not in email:
                print(f"❌ Skipping invalid email: {email}")

                sheet.update_cell(i, 4, "Invalid Email")
                skipped += 1
                continue

            # -----------------------
            # Generate certificate
            # -----------------------
            try:
                pdf = generate_certificate(name)
            except Exception as e:
                print(f"❌ Certificate error for {name}: {e}")
                failed += 1
                continue

            # -----------------------
            # Send email
            # -----------------------
            try:
                send_email(email, name, pdf)
            except Exception as e:
                print(f"❌ Email failed for {name}: {e}")
                failed += 1
                continue

            # -----------------------
            # Update status
            # -----------------------
            sheet.update_cell(i, 4, "Sent")
            sent += 1

            print(f"✅ Sent to {name}")

        except Exception as e:
            print(f"⚠ Unexpected error in row {i}: {e}")
            failed += 1
            continue

    # -----------------------
    # SUMMARY
    # -----------------------
    print("\n===== BULK PROCESS REPORT =====")
    print(f"✔ Sent     : {sent}")
    print(f"⚠ Skipped  : {skipped}")
    print(f"❌ Failed   : {failed}")

def merge_pdfs(pdf_list, output_file):

    from PyPDF2 import PdfWriter, PdfReader

    writer = PdfWriter()
    valid = 0

    for pdf in pdf_list:
        try:
            reader = PdfReader(pdf)
            for page in reader.pages:
                writer.add_page(page)
            valid += 1
        except Exception as e:
            print(f"⚠ Skipping file {pdf}: {e}")

    if valid == 0:
        print("❌ No PDFs to merge!")
        return None

    try:
        with open(output_file, "wb") as f:
            writer.write(f)

        print("✅ Merged PDF created:", output_file)
        return output_file

    except Exception as e:
        print("❌ Merge failed:", e)
        return None


# -----------------------------
# BULK EMAIL SYSTEM
# -----------------------------

def generate_and_send_bulk():

    data = sheet.get_all_records()
    pdf_files = []

    print("📄 Generating all certificates...")

    for row in data:
        name = str(row.get("Name", "")).strip()

        if not name:
            continue

        pdf = generate_certificate(name)

        if pdf:
            pdf_files.append(pdf)

        time.sleep(0.2)

    print(f"Total PDFs generated: {len(pdf_files)}")

    if not pdf_files:
        print("❌ No PDFs generated!")
        return

    merged_file = os.path.join(
        CERT_FOLDER,
        f"ALL_CERTIFICATES_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )

    final_pdf = merge_pdfs(pdf_files, merged_file)

    if not final_pdf:
        print("❌ Merge failed!")
        return

    print("✅ Merged PDF ready:", final_pdf)

    try:
        email = input("Enter recipient email: ").strip()

        if "@" not in email:
            print("❌ Invalid email")
            return

        send_email(email, "All Students", final_pdf)

    except Exception as e:
        print("❌ Email error:", e)

# -----------------------------
# MENU SYSTEM
# -----------------------------

while True:
    print("\n========= MAIN MENU =========")
    print("1. Add Data to Sheet")
    print("2. View Sheet Data")
    print("3. Delete Row")
    print("4. Generate Certificates")
    print("5. Send Emails Immediately")
    print("6. Send Emails at Custom Time (ALARM MODE)")
    print("7. Exit")
    print("8. Dashboard")
    print("9. Bulk Certificate (Single PDF + Email)")

    try:
        choice = input("Enter choice: ").strip()

    except EOFError:
        print("❌ No input received. Please use terminal.")
        continue

    # =========================
    # 1. ADD DATA
    # =========================
    if choice == "1":
        try:
            name = input("Enter Name: ").strip()
            age = int(input("Enter Age: ").strip())
            email = input("Enter Email: ").strip()

            sheet.append_row([name, age, email, "Pending"])
            print("✅ Data added!")

        except ValueError:
            print("❌ Age must be a number.")
            continue

        except EOFError:
            print("❌ Input error.")
            continue

    # =========================
    # 2. VIEW DATA
    # =========================
    elif choice == "2":
        data = sheet.get_all_records()
        print(data)

    # =========================
    # 3. DELETE ROW
    # =========================
    elif choice == "3":
        try:
            row = int(input("Row number to delete: ").strip())
            sheet.delete_rows(row)
            print("✅ Row deleted!")

        except ValueError:
            print("❌ Please enter a valid row number.")
            continue

        except EOFError:
            print("❌ Input error.")
            continue

    # =========================
    # 4. GENERATE CERTIFICATES
    # =========================
    elif choice == "4":
        try:
            data = sheet.get_all_records()

            for row in data:
                generate_certificate(row["Name"])

            print("✅ All certificates generated!")

        except Exception as e:
            print(f"❌ Certificate error: {e}")

    # =========================
    # 5. SEND EMAILS
    # =========================
    elif choice == "5":
        process_and_send()

    # =========================
    # 6. ALARM MODE
    # =========================
    elif choice == "6":
        try:
            target_time = input("Enter time (HH:MM): ").strip()
            wait_until_time(target_time)
            process_and_send()

        except EOFError:
            print("❌ Input error.")
            continue

    # =========================
    # 7. EXIT
    # =========================
    elif choice == "7":
        print("👋 Exiting...")
        break

    # =========================
    # 8. DASHBOARD
    # =========================
    elif choice == "8":

        data = sheet.get_all_records()

        total = len(data)
        sent = 0
        invalid = 0
        pending = 0

        for row in data:
            status = str(row.get("Status", "")).strip().lower()

            if status == "sent":
                sent += 1

            elif status == "invalid email":
                invalid += 1

            else:
                pending += 1

        print("\n===== DASHBOARD =====")
        print("Total Participants :", total)
        print("Certificates Sent  :", sent)
        print("Invalid Emails     :", invalid)
        print("Pending            :", pending)

        if total > 0:
            success_rate = round((sent / total) * 100, 2)
            print("Success Rate       :", success_rate, "%")

        input("\nPress Enter to return to main menu...")

    # =========================
    # 9. BULK CERTIFICATE SYSTEM
    # =========================
    elif choice == "9":
        generate_and_send_bulk()

    else:
        print("❌ Invalid choice! Try again.") 