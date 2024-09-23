from flask import Flask, render_template, request
import os
import json
import base64
from dotenv import load_dotenv
import httpx
import asyncio

load_dotenv()

app = Flask(__name__)

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

# PATRUS CREDENTIALS, HEADERS AND URL
PATRUS_USERNAME = os.environ.get('PATRUS_USERNAME')
PATRUS_PASSWORD = os.environ.get('PATRUS_PASSWORD')
PATRUS_SUBSCRIPTION = os.environ.get('PATRUS_SUB_TOKEN')

PATRUS_AUTH_URL = "https://api-patrus.azure-api.net/app_services/auth.oauth2.svc/token"

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
        print(f"HTTP error occurred: {e}")
        print(f"Response Content: {e.response.text}")
        raise

    return {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {access_token}',
    'Subscription': PATRUS_SUBSCRIPTION
}

PATRUS_URL = "https://api-patrus.azure-api.net/api/v1/logistica/comercial/cotacoes/online"

# Constant for cubic weight calculation (used only for Patrus)
CUBIC_FACTOR = 300

# PAULINERIS CREDENTIALS, HEADERS AND URL


# DATA SANITIZING FUNCTIONS

# Used for Braspress API
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
    
    patrus_headers = await get_patrus_headers()
    
    # TEST
    print("submission working")

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
    
    modalidade = "R" 
    
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
    
    print("cep_destino") #TEST

    if request.form['tipo_frete'] not in ["1", "2"]:
        return error("Tipo de frete inválido", 400)
    
    tipo_frete = request.form['tipo_frete']
    
    print("tipo_frete") #TEST

    try:
        vlr_mercadoria = sanitize_float(request.form['vlr_mercadoria'])
    except ValueError:
        return error("Valor da mercadoria inválido", 400)
    
    print("vlr_mercadoria") #TEST

    try:
        peso_total = sanitize_float(request.form['peso_total'])
    except ValueError:
        return error("Valor do peso inválido", 400)
    
    print("peso_total") #TEST

    try:
        volumes_total = sanitize_int(request.form['volumes_total'])
    except ValueError:
        return error("Total de volumes inválido", 400)

    print("volumes_total") #TEST

    cubagem = []

    print("main forms succesfull") #TEST 
    
    print(request.form['volumeGroupIds']) #TEST

    volume_group_ids = request.form['volumeGroupIds'].split(",")   

    print(volume_group_ids) #TEST
    print(request.form) #TEST

    total_cubic_weight = 0

        # Dynamically handling volume groups
    for i in volume_group_ids:
        altura_key = f'altura{i}'
        print(altura_key) #TEST
        largura_key = f'largura{i}'
        print(largura_key) #TEST
        comprimento_key = f'comprimento{i}'
        print(comprimento_key) #TEST
        volumes_key = f'volumes{i}'
        print(volumes_key) #TEST

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
            "PesoCubado": total_cubic_weight,
            "ValorMercadoria": vlr_mercadoria
        },
    }

    main_data = {
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

    data_test1 = json.dumps(braspress_data)
    data_test2 = json.dumps(patrus_data)

    #TEST
    print("BRASPRESS JSON")
    print(data_test1)
    print("PATRUS JSON")
    print(data_test2)

    async with httpx.AsyncClient() as client:
        tasks = [
            client.post(BRASPRESS_URL, json=braspress_data, headers=BRASPRESS_HEADERS),
            client.post(PATRUS_URL, json=patrus_data, headers=patrus_headers, timeout=30.0),
            # client.post( , json=data, headers= )
        ]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

    results = []
    errors = []

    # TEST
    print("Response:")
    
    for response in responses:
        
        # TEST
        print(response)


        if isinstance(response, Exception):
            errors.append(str(response))
        else:
            try:
                response.raise_for_status()
                results.append(response.json())
            except httpx.ReadTimeout:
                errors.append("The read operation timed out")
            except httpx.HTTPStatusError as e:
                errors.append(f"HTTP error occurred: {e}")
                errors.append(f"Response Content: {e.response.text}")

    # TEST
    print("Result:")
    print(results)
    print("Errors:")
    print(errors)

    return render_template('result.html', results=results, errors=errors, data=main_data)


if __name__ == '__main__':
    app.run(debug=True)