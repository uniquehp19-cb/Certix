import os
import smtplib
from email.message import EmailMessage
from config import Config


def send_email(receiver_email, name, file_path):
    if not receiver_email or "@" not in receiver_email:
        return False, "Invalid email address"

    msg = EmailMessage()
    msg["Subject"] = f"Certificate of Participation - {name}"
    msg["From"] = Config.SENDER_EMAIL
    msg["To"] = receiver_email

    msg.set_content(f"Congratulations {name}! Your certificate is attached.")

    msg.add_alternative(
        f"""
    <html>
    <body style="font-family: Arial, sans-serif; color:#222;">
    <h2>Congratulations {name}!</h2>
    <p>We are pleased to inform you that your certificate has been
    successfully generated.</p>
    <p>Please find your certificate attached to this email.</p>
    <p>Thank you for your participation and support.</p>
    <br>
    <p>Best Regards,<br><b>KITE Team</b></p>
    </body>
    </html>
    """,
        subtype="html",
    )

    if file_path and os.path.exists(file_path):
        with open(file_path, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="pdf",
                filename=os.path.basename(file_path),
            )

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(Config.SENDER_EMAIL, Config.SENDER_PASSWORD)
            smtp.send_message(msg)
        return True, "Sent"
    except Exception as e:
        return False, str(e)
