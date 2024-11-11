# This project was developed with the assistance of GitHub Copilot and CS50's Duck Debugger (ddb).

from flask import Flask, render_template, request
import os
import base64
from dotenv import load_dotenv
import httpx
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

load_dotenv()

app = Flask(__name__)

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

# TEST
print(BRASPRESS_CREDENTIALS)

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
        header_error = {
            'statusCode': e.response.status_code,
            'message': e.response.json().get('message', 'Unknown error')
        }
        print(f"HTTP error occurred: {e}")
        print(f"Response Content: {e.response.text}")
        return None, header_error
    except Exception as e:
        header_error = {
            'statusCode': 'Unknown',
            'message': str(e)
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
    except Exception as e:


        #TEST
        print(f"Failed to send email: {e}")


# DATA SANITIZING FUNCTIONS
def format_datetime(input):
    if isinstance(input, int):
        today = datetime.now()
        date_obj = today + timedelta(days=input)
        formatted_date = date_obj.strftime("%d/%m/%Y")
        days_left = input
    elif isinstance(input, str):
        date_obj = datetime.strptime(input, "%Y-%m-%dT%H:%M:%S") # Parse the date string 
        today = datetime.now() # Calculate the days left
        days_left = (date_obj - today).days   
        formatted_date = date_obj.strftime("%d/%m/%Y") # Format the date as dd/mm/yyyy
    else:
        formatted_date = None
        days_left = None
    
    return formatted_date, days_left


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


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/error/<int:code>/<path:error_message>')
def error(error_message, code):
    return render_template('error.html', error_message=error_message, code=code)

@app.route('/submit', methods=['POST'])
async def submit():

    # TEST
    print("submission working")
    
    # Initialize errors and results array (add one slot for each freight company)
    errors = [None, None] 
    results = [None, None]

    
    patrus_headers, header_error = await get_patrus_headers()
    if header_error:
        patrus_headers = None
    
    #TEST
    print("initiating main form handling")  
    
    nome_fantasia = request.form['nome_fantasia']
    
    modalidade = "R" 

    try:
        cnpj_tomador = request.form['cnpj_remetente']
        cnpj_remetente = sanitize_text(cnpj_tomador)
    except ValueError:
        return error("CNPJ do remetente inválido", 400)
    
    try:
        cnpj_destino = request.form['cnpj_destinatario']
        cnpj_destinatario = sanitize_text(cnpj_destino)
    except ValueError:
        return error("CNPJ do destinatário inválido", 400)
    
    try:
        cep_origem = request.form['cep_origem']
        cep_remetente = sanitize_text(cep_origem)
    except ValueError:
        return error("CEP de origem inválido", 400)
    
    try:
        cep_destino = request.form['cep_destino']
        cep_destinatario = sanitize_text(cep_destino)
    except ValueError:
        return error("CEP de destino inválido", 400)

    if request.form['tipo_frete'] not in ["1", "2"]:
        return error("Tipo de frete inválido", 400)
    
    tipo_frete = request.form['tipo_frete']
    
    try:
        vlr_mercadoria = sanitize_float(request.form['vlr_mercadoria'])
    except ValueError:
        return error("Valor da mercadoria inválido", 400)
    
    try:
        peso_total = sanitize_float(request.form['peso_total'])
    except ValueError:
        return error("Valor do peso inválido", 400)
    
    try:
        volumes_total = sanitize_int(request.form['volumes_total'])
    except ValueError:
        return error("Total de volumes inválido", 400)

    cubagem = []

    volume_group_ids = request.form['volumeGroupIds'].split(",")   

    total_cubic_weight = 0

    # Dynamically handling volume groups
    for i in volume_group_ids:
        altura_key = f'altura{i}'
        largura_key = f'largura{i}'
        comprimento_key = f'comprimento{i}'
        volumes_key = f'volumes{i}'

        altura = sanitize_float(request.form[altura_key])
        largura = sanitize_float(request.form[largura_key])
        comprimento = sanitize_float(request.form[comprimento_key])
        volumes = sanitize_int(request.form[volumes_key])

        # Calculate the cubic weight
        cubic_weight = (altura * largura * comprimento) * CUBIC_FACTOR * volumes
        total_cubic_weight += cubic_weight

        # Store the volume group data
        cubagem.append({
            "altura": altura,
            "largura": largura,
            "comprimento": comprimento,
            "volumes": volumes
        })

    round_cubic_weight = round(total_cubic_weight, 2)

    braspress_data = {
        "cnpjRemetente": cnpj_remetente,
        "cnpjDestinatario": cnpj_destinatario,
        "modal": modalidade,
        "tipoFrete": tipo_frete,
        "cepOrigem": cep_remetente,
        "cepDestino": cep_destinatario,
        "vlrMercadoria": vlr_mercadoria,
        "peso": peso_total,
        "volumes": volumes_total,
        "cubagem": cubagem
    }
    
    patrus_data = {
        "CnpjTomador": cnpj_tomador,
        "CepDestino": cep_destino,
        "CnpjCpf": cnpj_destino,
        "Carga": {
            "Volumes": volumes_total,
            "Peso": peso_total,
            "PesoCubado": round_cubic_weight,
            "ValorMercadoria": vlr_mercadoria
        },
    }

    main_data = {
        "nomeFantasia": nome_fantasia,
        "cnpjRemetente": cnpj_tomador,
        "cnpjDestinatario": cnpj_destino,
        "modal": modalidade,
        "tipoFrete": tipo_frete,
        "cepOrigem": cep_origem,
        "cepDestino": cep_destino,
        "vlrMercadoria": vlr_mercadoria,
        "peso": peso_total,
        "volumes": volumes_total,
        "pesoCubado": total_cubic_weight,
        "cubagem": cubagem
    }

    async with httpx.AsyncClient() as client:
        tasks = [
            client.post(BRASPRESS_URL, json=braspress_data, headers=BRASPRESS_HEADERS, timeout=30.0),
            client.post(PATRUS_URL, json=patrus_data, headers=patrus_headers, timeout=30.0),
        ]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    for i, response in enumerate(responses):

        #TEST
        print(response)
        
        if isinstance(response, Exception):
            errors[i] = str(response)
        else:
            try:
                response.raise_for_status()
                results[i] = response.json()
            except httpx.ReadTimeout:
                errors[i] = "The read operation timed out"
            except httpx.HTTPStatusError as e:
                errors[i] = {
                    'statusCode': e.response.status_code,
                    'message': e.response.json().get('message', 'Unknown error')
                }

    # PADRONIZING THE RESULTS
    # Braspress
    if results[0]:
        delivery_date, delivery_time = format_datetime(results[0]['prazo'])
        results[0]['entrega'] = delivery_date
        results[0]['prazo'] = delivery_time

        #TEST
        print("Results 0")
        print(results[0])

    # Patrus
    if results[1]:
        delivery_date, delivery_time = format_datetime(results[1]['EntregaPrevista'])
        results[1]['entrega'] = delivery_date
        results[1]['prazo'] = delivery_time

        #TEST
        print("Result 1")
        print(results[1])

    # SENDING EMAIL
    date = datetime.now().strftime("%d/%m/%Y às %H:%M")
    price = f"{vlr_mercadoria:.2f}"
    subject = f"Cotação para {nome_fantasia} | valor do pedido: R$ {price} | {date}"
    html_content = render_template('email_result.html', results=results, errors=errors, data=main_data, header_error=header_error, date=date)

    send_email(subject, RECIPIENT_EMAIL, html_content)
    
    return render_template('result.html', results=results, errors=errors, data=main_data, header_error=header_error)

if __name__ == '__main__':
    app.run(debug=True)