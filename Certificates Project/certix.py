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
    print(f"⏳ Waiting for {target_time}...")

    while True:
        now = datetime.now().strftime("%H:%M")

        if now == target_time:
            print(f"✅ {target_time} reached! Starting process...")
            break

        time.sleep(20)

# -----------------------------
# GOOGLE SHEET SETUP
# -----------------------------
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(
    "credentials.json",
    scopes=scope
)

client = gspread.authorize(creds)
sheet = client.open_by_key("1fm-xMzXBDmHIXewo7V0U8uBKEEGpbtMMURz1SG1FXcY").sheet1

# -----------------------------
# CERTIFICATE GENERATOR
# -----------------------------
def generate_certificate(name):
    safe_name = name.replace("/", "_")

    today = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

    path = f"{CERT_FOLDER}/{safe_name}_{today}.pdf"

    print("Generating:", path)

    c = canvas.Canvas(path, pagesize=landscape(A4))
    width, height = landscape(A4)

    # Certificate Background Template
    c.drawImage(
         "certificate_template.png",
          0,
          0,
          width=width,
          height=height
    )

# Student Name
    
    c.setFillColor(colors.HexColor("#222222"))

    c.setFont("GreatVibes", 46)

    c.drawCentredString(
         width/2,
         240,
         name.title()
    )

# Date
    today = datetime.now().strftime("%d-%m-%Y")

    c.setFont("Helvetica", 12)
    c.drawString(100, 80, today)    

    c.save()

    print("Certificate saved:", path)

    return path

# -----------------------------
# EMAIL FUNCTION
# -----------------------------
def send_email(receiver_email, name, file_path):

    if not receiver_email or "@" not in receiver_email:
        print(f"Skipping invalid email: {receiver_email}")
        return

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

    <p>
    We are pleased to inform you that your certificate has been successfully generated.
    </p>

    <p>
    Please find your certificate attached to this email.
    </p>

    <p>
    Thank you for your participation and support.
    </p>

    <br>

    <p>
    Best Regards,<br>
    <b>KITE Team</b>
    </p>

    </body>
    </html>
    """, subtype="html")

    with open(file_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="pdf",
            filename=os.path.basename(file_path)
        )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
        smtp.send_message(msg)

    print(f"Email sent to {receiver_email}")

# -----------------------------
# BULK PROCESS
# -----------------------------
def process_and_send():
    data = sheet.get_all_records()

    sent = 0
    skipped = 0

    for i, row in enumerate(data, start=2):

       name = row.get("Name", "").strip()
       email = row.get("Email", "").strip()
       status = row.get("Status", "").strip()

       if status == "Sent":
         print(f"Skipping {name} - Already Sent")
         continue
        
       if not email or "@" not in email:
        print("Skipping invalid email:", email)

        sheet.update_cell(i, 4, "Invalid Email")

        skipped += 1
        continue

       pdf = generate_certificate(name)

       send_email(email, name, pdf)

    # Update Status column
       sheet.update_cell(i, 4, "Sent")

       sent += 1
    print(f"\n✔ Sent: {sent}")
    print(f"⚠ Skipped: {skipped}")

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

    choice = input("Enter choice: ")

    if choice == "1":
        name = input("Enter Name: ")
        age = int(input("Enter Age: "))
        email = input("Enter Email: ")

        sheet.append_row([name, age, email,""])

        print("Data added!")

    elif choice == "2":
        data = sheet.get_all_records()
        print(data)

    elif choice == "3":
        row = int(input("Row number to delete: "))
        sheet.delete_rows(row)
        print("Row deleted!")

    elif choice == "4":
        data = sheet.get_all_records()

        for row in data:
            generate_certificate(row["Name"])

        print("All certificates generated!")

    elif choice == "5":
        process_and_send()

    # ✅ FIXED ALARM MODE
    elif choice == "6":
       target_time = input("Enter time in 24-hour format (e.g. 10:52 or 18:30): ")

       wait_until_time(target_time)
       process_and_send()

    elif choice == "7":
        print("Exiting...")
        break

    elif choice == "8":

        data = sheet.get_all_records()

        total = len(data)
        sent = 0
        invalid = 0
        pending = 0

        for row in data:

            status = row.get("Status", "").strip()

            if status == "Sent":
                sent += 1

            elif status == "Invalid Email":
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

    else:
         print("Invalid choice!")