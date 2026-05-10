from flask import Flask, request, jsonify
import os
import logging
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

app = Flask(__name__)
SECRET_CODE = os.environ.get("ACCESS_CODE", "1234")

logging.basicConfig(
    filename='/logs/auth.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

def send_email(ip, success):
    try:
        sender    = os.environ.get("MAIL_FROM")
        recipient = os.environ.get("MAIL_TO")
        password  = os.environ.get("MAIL_PASSWORD")
        smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.environ.get("SMTP_PORT", "587"))

        status = "הצליחה" if success else "נכשלה"
        body = f"התחברות {status}\nזמן: {datetime.now()}\nIP: {ip}"

        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = f"התראת התחברות - {status}"
        msg["From"]    = sender
        msg["To"]      = recipient

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
    except Exception as e:
        logging.error(f"שגיאה בשליחת מייל: {e}")

@app.route("/auth", methods=["POST"])
def auth():
    data = request.get_json()
    ip   = request.remote_addr

    if data.get("code") == SECRET_CODE:
        logging.info(f"התחברות מוצלחת מ-{ip}")
        send_email(ip, success=True)
        return jsonify({"status": "ok", "token": "allowed"}), 200
    else:
        logging.warning(f"ניסיון כושל מ-{ip}")
        send_email(ip, success=False)
        return jsonify({"status": "denied"}), 401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
