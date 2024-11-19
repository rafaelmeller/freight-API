# This project was developed with the assistance of GitHub Copilot and CS50's Duck Debugger (ddb).

import os
import base64
from dotenv import load_dotenv
import httpx
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

load_dotenv()

# E-MAIL CREDENTIALS, RECIPIENT AND CONFIGURATION
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD')
RECIPIENT_EMAIL = os.environ.get('RECIPIENT_EMAIL')
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# BRASPRESS CREDENTIALS, HEADERS AND URL
BRASPRESS_USERNAME = os.environ.get('BRASPRESS_USERNAME_1')
BRASPRESS_PASSWORD = os.environ.get('BRASPRESS_PASSWORD_1')
BRASPRESS_CREDENTIALS = base64.b64encode(f'{BRASPRESS_USERNAME}:{BRASPRESS_PASSWORD}'.encode('utf-8')).decode('utf-8')

BRASPRESS_HEADERS = {
    'Authorization': f'Basic {BRASPRESS_CREDENTIALS}',
    'Content-Type': 'application/json; charset=utf-8',
    'Accept': 'application/json',
}

BRASPRESS_URL = "https://api.braspress.com/v1/cotacao/calcular/json"

# PATRUS CREDENTIALS, HEADERS, URL AND FUNCTIONS
PATRUS_USERNAME = os.environ.get('PATRUS_USERNAME')
PATRUS_PASSWORD = os.environ.get('PATRUS_PASSWORD')
PATRUS_SUBSCRIPTION = os.environ.get('PATRUS_SUB_TOKEN')

PATRUS_AUTH_URL = "https://api-patrus.azure-api.net/security/app_services/auth.oauth2.svc/token"

async def get_patrus_access_token():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            PATRUS_AUTH_URL,
            data={
                'username': PATRUS_USERNAME,
                'password': PATRUS_PASSWORD,
                'grant_type': 'password'
            },
            headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Subscription': PATRUS_SUBSCRIPTION
        }
        )
        response.raise_for_status()
        return response.json()['access_token']
    
async def get_patrus_headers():
    try:
        access_token = await get_patrus_access_token()
    except httpx.HTTPStatusError as e:
        response_json = e.response.json()
        header_error = {
            'statusCode': e.response.status_code,
            'message': response_json.get('error', 'Unknown error'),
            'description': response_json.get('error_description', 'No description available')
        }
        
        print(f"HTTP error occurred: {e}")
        print(f"Response Content: {e.response.text}")
        return None, header_error
    except Exception as e:
        header_error = {
            'statusCode': 'Unknown',
            'message': str(e),
            'description': 'No description available'
        }
        return None, header_error

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'Subscription': PATRUS_SUBSCRIPTION
    }
    return headers, None

PATRUS_URL = "https://api-patrus.azure-api.net/api/v1/logistica/comercial/cotacoes/online"

CUBIC_FACTOR = 300 # Constant for cubic weight calculation (used only for Patrus)

# FUNCTION FOR SENDING EMAILS
def send_email(subject, recipient, html_content):
    sender_email = SENDER_EMAIL
    sender_password = SENDER_PASSWORD

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient

    part = MIMEText(html_content, 'html')
    msg.attach(part)

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient, msg.as_string())
        server.quit()

        #TEST
        print("Email sent successfully")

        return True, None
    except Exception as e:
        #TEST
        print(f"Failed to send email: {e}")

        return False, str(e)


# DATA SANITIZING FUNCTIONS
def format_datetime(input):
    if isinstance(input, int):
        days_left = input
        date_obj = datetime.now()
        while days_left > 0:
            date_obj += timedelta(days=1)
            if date_obj.weekday() < 5:
                days_left -= 1
        days_left = input
        formatted_date = date_obj.strftime("%d/%m/%Y")
    elif isinstance(input, str):
        date_obj = datetime.strptime(input, "%Y-%m-%dT%H:%M:%S") # Parse the date string 
        today = datetime.now() # Calculate the days left
        days_left = (date_obj - today).days   
        formatted_date = date_obj.strftime("%d/%m/%Y") # Format the date as dd/mm/yyyy
    else:
        formatted_date = None
        days_left = None
    
    return formatted_date, days_left


def format_currency(value):
    print(type(value))
    print(value)
    if isinstance(value, str):
        value = sanitize_float(value.replace("R$", ""))
        print(value)
    formatted_value = f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") 

    return formatted_value


def sanitize_text(input_string):
        for char in [".", "/", "-", " "]:
            input_string = input_string.replace(char, "")
        output_string = int(input_string)
        return output_string


def sanitize_int(input_string):
    if "," in input_string:
        input_string = input_string.replace(",", ".")
    elif " " in input_string:
        input_string = input_string.replace(" ", "")
    output_string = int(input_string)  
    return output_string


def sanitize_float(input_string):
    if "," in input_string:
        input_string = input_string.replace(",", ".")
    elif " " in input_string:
        input_string = input_string.replace(" ", "")
    output_string = float(input_string) 
    formatted_output = round(output_string, 2)
    return formatted_output

