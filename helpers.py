# This project was developed by me with the assistance of GitHub Copilot and CS50's Duck Debugger (ddb).

import asyncio
import os
import base64
from dotenv import load_dotenv
import httpx
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from flask import redirect, session
from functools import wraps

load_dotenv()

# E-MAIL CREDENTIALS, RECIPIENT AND CONFIGURATION
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD')
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

async def fetch_data(data1, headers1, data2):
        async with httpx.AsyncClient() as client:
            tasks = [
                client.post(BRASPRESS_URL, json=data2,
                            headers=BRASPRESS_HEADERS, timeout=30.0),
            ]
            if headers1:
                tasks.append(client.post(PATRUS_URL, json=data1,
                             headers=headers1, timeout=30.0))
            return await asyncio.gather(*tasks, return_exceptions=True)


# FLASK decorator function copied from CS50's project "Finance"
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def update_env(key, value, env_file='.env'):
    with open(env_file, 'r') as file:
        lines = file.readlines()

    with open(env_file, 'w') as file:
        for line in lines:
            if line.startswith(f"{key}="):
                file.write(f"{key}={value}\n")
            else:
                file.write(line)
    os.environ[key] = value
    load_dotenv()
    


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
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        if tomorrow.weekday() > 4: # If tomorrow is Saturday (5) or Sunday (6)
            first_day = tomorrow + timedelta(days=(7 - tomorrow.weekday()))  # Move to next Monday
        else:
            first_day = tomorrow
        days_left = 1
        current_day = first_day
        while current_day <= date_obj:
            if current_day.weekday() < 5:  # Monday to Friday are < 5
                days_left += 1
            current_day += timedelta(days=1)   
        formatted_date = date_obj.strftime("%d/%m/%Y") # Format the date as dd/mm/yyyy
    else:
        formatted_date = None
        days_left = None
    
    return formatted_date, days_left


def format_currency(value):
    if isinstance(value, str):
        value = sanitize_float(value.replace("R$", ""))
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

