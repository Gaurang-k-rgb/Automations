import os
from twilio.rest import Client
from datetime import datetime
import time

# Use environment variables in production; fall back to placeholders for local testing
account_sid = os.getenv("TWILIO_ACCOUNT_SID", "AC6e7e99b5789cb9ec8beab0dfa166ba64")
account_token = os.getenv("TWILIO_AUTH_TOKEN", "29d43395d31919506ca6bc2a8d50f074")

client = Client(account_sid, account_token)

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
    name = input('Enter recipient name: ')
    recipient_number = input('Enter recipient WhatsApp number (with country code, e.g. +15551234567): ')
    message_body = input(f'Enter your message for {name}: ')

    date_str = input('Enter the date to send the message (YYYY-MM-DD): ')
    time_str = input('Enter the time to send the message (HH:MM in 24-hour format): ')

    # correct format: Year-month-day Hour:Minute
    try:
        scheduled_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    except ValueError:
        print("Invalid date/time format. Use YYYY-MM-DD and HH:MM (24-hour).")
        raise SystemExit(1)

    current_datetime = datetime.now()
    delay_seconds = (scheduled_datetime - current_datetime).total_seconds()

    if delay_seconds <= 0:
        print("Scheduled time is in the past. Please enter a future time.")
    else:
        print(f"Message scheduled to be sent to {name} at {scheduled_datetime}.")
        time.sleep(delay_seconds)
        send_whatsapp_message(recipient_number, message_body)

