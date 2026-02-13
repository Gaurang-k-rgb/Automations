import os
import pandas as pd
from twilio.rest import Client
from datetime import datetime
import time

# Use environment variables in production; fall back to placeholders for local testing
account_sid = os.getenv("TWILIO_ACCOUNT_SID", "AC6e7e99b5789cb9ec8beab0dfa166ba64")
account_token = os.getenv("TWILIO_AUTH_TOKEN", "29d43395d31919506ca6bc2a8d50f074")

client = Client(account_sid, account_token)

def normalize_number(raw, default_cc="+91"):
    s = str(raw).strip()
    if not s or s.lower() == 'nan':
        return None
    # remove spaces and common separators
    s = s.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if s.startswith("+"):
        return s
    # strip leading zeros and add default country code
    s = s.lstrip("0")
    return default_cc + s

def send_whatsapp_message(recipient_number, message_body):
    try:
        message = client.messages.create(
            from_='whatsapp:+14155238886',
            body=message_body,
            to=f'whatsapp:{recipient_number}'
        )
        print(f"Message sent to {recipient_number}: {message.sid}")
    except Exception as e:
        print(f"Failed to send message to {recipient_number}: {e}")

if __name__ == "__main__":
    # locate Book1.xlsx in the same folder as this script
    script_dir = os.path.dirname(__file__)
    excel_path = os.path.join(script_dir, "Book1.xlsx")

    if not os.path.exists(excel_path):
        print(f"Book1.xlsx not found at {excel_path}")
        raise SystemExit(1)

    # read workbook (expects data in columns B, C, D)
    try:
        df = pd.read_excel(excel_path, engine="openpyxl")
    except Exception as e:
        msg = str(e).lower()
        if "openpyxl" in msg or "missing optional dependency 'openpyxl'".lower() in msg:
            print("Missing dependency 'openpyxl'. Install it with:")
            print("  python -m pip install openpyxl")
        else:
            print(f"Failed to read Excel file: {e}")
        raise SystemExit(1)

    # try to read by header names if present, otherwise use column positions:
    # B -> index 1 (name), C -> index 2 (number), D -> index 3 (message)
    try:
        names = df.iloc[:, 1].astype(str).str.strip()
        raw_numbers = df.iloc[:, 2]
        messages = df.iloc[:, 3].astype(str)
    except Exception as e:
        print("Unexpected Excel format. Ensure columns B (name), C (number), D (message) exist.")
        raise SystemExit(1)

    recipients = []
    for n, rn, msg in zip(names, raw_numbers, messages):
        num = normalize_number(rn, default_cc="+91")
        if num:
            recipients.append((n, num, msg))

    if not recipients:
        print("No valid recipients found in Book1.xlsx (columns B/C/D).")
        raise SystemExit(1)

    date_str = input('Enter the date to send the message (YYYY-MM-DD): ')
    time_str = input('Enter the time to send the message (HH:MM in 24-hour format): ')

    try:
        scheduled_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    except ValueError:
        print("Invalid date/time format. Use YYYY-MM-DD and HH:MM (24-hour).")
        raise SystemExit(1)

    delay_seconds = (scheduled_datetime - datetime.now()).total_seconds()
    if delay_seconds <= 0:
        print("Scheduled time is in the past. Please enter a future time.")
        raise SystemExit(1)

    print(f"Scheduling {len(recipients)} messages to be sent at {scheduled_datetime}.")
    time.sleep(delay_seconds)

    for name, number, body in recipients:
        # use message from column D; you can format it with name if desired
        send_whatsapp_message(number, body)
        time.sleep(1)  # small gap to avoid rapid-fire requests


