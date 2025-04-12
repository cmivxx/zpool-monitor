import subprocess
import requests
import datetime
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
import os

# -------- Load Config from .env --------
load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")
LOG_FILE = os.getenv("LOG_FILE", "zpool_monitor.log")
# ---------------------------------------

# Setup logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s %(message)s')

def check_zpool_status():
    try:
        result = subprocess.run(["/sbin/zpool", "status"], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error executing zpool status: {e}"

def parse_zpool_status(status_output):
    warnings = []
    warning_keywords = ["DEGRADED", "FAULTED", "OFFLINE", "UNAVAIL", "REMOVED", "ERROR"]
    for line in status_output.splitlines():
        if any(keyword in line for keyword in warning_keywords):
            warnings.append(line.strip())
    return warnings

def format_message(warnings, full_output):
    header = "**🚨 ZFS Zpool Alert**\nThe following issues were found:\n"
    warning_text = "\n".join(f"- `{w}`" for w in warnings)
    full_message = header + warning_text + "\n\n**Full zpool status:**\n"
    full_message += f"```{full_output[:1900]}```"
    return full_message

def log_status(warnings, full_output):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "HEALTHY" if not warnings else "ISSUES FOUND"
    log_entry = f"[{timestamp}] STATUS: {status}\n{full_output}\n{'-' * 60}\n"
    logging.info(log_entry)

def send_discord_alert(message):
    payload = {"content": message}
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    if response.status_code != 204:
        raise Exception(f"Discord alert failed: {response.status_code} - {response.text}")
    print("Discord alert sent.")

def send_email_backup(subject, message):
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        email = Mail(
            from_email=EMAIL_FROM,
            to_emails=EMAIL_TO,
            subject=subject,
            plain_text_content=message
        )
        response = sg.send(email)
        if response.status_code >= 400:
            print(f"SendGrid error: {response.status_code} - {response.body}")
        else:
            print("Backup email sent via SendGrid.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    status_output = check_zpool_status()
    if "Error executing" in status_output:
        print(status_output)
        return

    warnings = parse_zpool_status(status_output)
    log_status(warnings, status_output)

    if warnings:
        message = format_message(warnings, status_output)
        try:
            send_discord_alert(message)
        except Exception as discord_error:
            print(f"Discord alert failed: {discord_error}")
        send_email_backup("ZFS Zpool Monitor ALERT", message)

if __name__ == "__main__":
    main()

