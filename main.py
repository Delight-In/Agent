import re
import os
import requests
import logging
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage
from twilio.rest import Client

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)

EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')


def is_valid_email(email):
    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    return bool(re.match(regex, email, re.IGNORECASE))


def is_valid_phone(phone):
    # Basic India format validation: +91 followed by 10 digits
    return bool(re.match(r'^\+91\d{10}$', phone))


def send_sms(content, phone_number):
    if not is_valid_phone(phone_number):
        return False, f"Invalid phone number: {phone_number}"

    url = "https://www.fast2sms.com/dev/bulkV2"

    payload = {
        "sender_id": "TXTIND",
        "message": content,
        "language": "english",
        "route": "v3",
        "numbers": phone_number,
    }
    headers = {
        "authorization": os.getenv("FAST2SMS_API_KEY"),
        "Content-Type": "application/x-www-form-urlencoded",
    }

    try:
        response = requests.post(url, data=payload, headers=headers)
        if response.status_code == 200:
            logging.info(f"SMS sent to {phone_number}")
            return True, "SMS sent successfully"
        else:
            logging.error(f"Fast2SMS failed: {response.text}")
            return False, f"SMS failed: {response.text}"
    except Exception as e:
        logging.error("Exception in send_sms", exc_info=True)
        return False, str(e)


def send_email(name, recipient_email, message_body, subject=None, attachments=None):
    if not is_valid_email(recipient_email):
        return False, f"Invalid email address: {recipient_email}"

    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        logging.error("Email credentials not set in environment variables")
        return False, "Email credentials not configured"

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = recipient_email
    msg.set_content(message_body)

    # Attach files if any
    import mimetypes
    if attachments:
    for file_storage in attachments:
        # Skip empty files (no filename or empty content)
        if not file_storage.filename or file_storage.content_length == 0:
            continue

        file_data = file_storage.read()
        file_name = file_storage.filename

        # Guess MIME type
        mime_type, _ = mimetypes.guess_type(file_name)
        if mime_type:
            maintype, subtype = mime_type.split('/')
        else:
            maintype, subtype = 'application', 'octet-stream'

        msg.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=file_name)

        file_storage.seek(0)  # Reset pointer if needed elsewhere



    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        logging.info(f"Email sent to {recipient_email}")

        return True, f"Email sent to {name} successfully"
    except Exception as e:
        logging.error("Exception in send_email", exc_info=True)
        return False, str(e)


def send_whatsapp(content, phone_number):
    if not is_valid_phone(phone_number):
        return False, f"Invalid WhatsApp number: {phone_number}"

    account_sid = os.getenv("TWILIO_SID")
    auth_token = os.getenv("TWILIO_TOKEN")

    if not account_sid or not auth_token:
        logging.error("Twilio credentials not set in environment variables")
        return False, "Twilio credentials not configured"

    client = Client(account_sid, auth_token)

    try:
        message = client.messages.create(
            body=content,
            from_='whatsapp:+14155238886',  # Twilio sandbox WhatsApp number
            to=f'whatsapp:{phone_number}'
        )
        logging.info(f"WhatsApp message sent to {phone_number}, SID: {message.sid}")
        return True, f"WhatsApp sent: {message.sid}"
    except Exception as e:
        logging.error("Exception in send_whatsapp", exc_info=True)
        return False, str(e)


def handle_call(content, phone_number):
    if not is_valid_phone(phone_number):
        return False, f"Invalid phone number for call: {phone_number}"

    SID = os.getenv("EXOTEL_SID")
    TOKEN = os.getenv("EXOTEL_TOKEN")
    exophone = os.getenv("EXOPHONE")
    exotel_from = os.getenv("EXOTEL_FROM")

    if not all([SID, TOKEN, exophone, exotel_from]):
        logging.error("Exotel credentials not set in environment variables")
        return False, "Exotel credentials not configured"

    url = f"https://{SID}:{TOKEN}@twilix.exotel.in/v1/Accounts/{SID}/Calls/connect"

    payload = {
        "From": exotel_from,      # Your Exotel virtual number
        "To": phone_number,       # Customer's number
        "CallerId": exophone,     # Caller ID to show on receiver's phone
        "CallType": "trans",
        "TimeLimit": "30",
        "TimeOut": "10",
        "StatusCallback": "http://yourapp.com/callback",  # optional
    }

    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            logging.info(f"Call initiated to {phone_number}")
            return True, "Call initiated successfully"
        else:
            logging.error(f"Exotel call failed: {response.text}")
            return False, f"Call failed: {response.text}"
    except Exception as e:
        logging.error("Exception in handle_call", exc_info=True)
        return False, str(e)
def dispatch_message(mode, content, contact, name=None, subject=None, attachments=None):
    """
    Dispatch message by mode:
    - For email, name param is required for personalized subject.
    - subject and attachments are used only for email.
    """
    
    if mode == "sms":
        return send_sms(content, contact)
        
    elif mode == "email":
        if not name:
            name = "User"  # fallback name if not provided
        
        # Pass subject and attachments to send_email
        return send_email(name, contact, content, subject=subject, attachments=attachments)
    
    elif mode == "whatsapp":
        return send_whatsapp(content, contact)
    
    elif mode == "call":
        return handle_call(content, contact)
    
    else:
        return False, f"Unsupported communication mode: {mode}"
