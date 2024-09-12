from flask import Flask, render_template, request
import requests                                         # Uninstall after testing
from requests.auth import HTTPBasicAuth
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


PATRUS_URL = "https://api-patrus.azure-api.net/api/v1/logistica/comercial/cotacoes/online"

# PAULINERIS CREDENTIALS, HEADERS AND URL


# Data sanitizing functions
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

    try:
        cnpj_remetente = sanitize_text(request.form['cnpj_remetente'])
    except ValueError:
        return error("CNPJ do remetente inválido", 400)
    
    try:
        cnpj_destinatario = sanitize_text(request.form['cnpj_destinatario'])
    except ValueError:
        return error("CNPJ do destinatário inválido", 400)
    
    modalidade = "R" 
    
    try:
        cep_origem = sanitize_text(request.form['cep_origem'])
    except ValueError:
        return error("CEP de origem inválido", 400)
    
    try:
        cep_destino = sanitize_text(request.form['cep_destino'])
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

        # Store the volume group data
        cubagem.append({
            "altura": altura,
            "largura": largura,
            "comprimento": comprimento,
            "volumes": volumes
        })
       
    data = {
            "cnpjRemetente": cnpj_remetente,
            "cnpjDestinatario": cnpj_destinatario,
            "modal": modalidade,
            "tipoFrete": tipo_frete,
            "cepOrigem": cep_origem,
            "cepDestino": cep_destino,
            "vlrMercadoria": vlr_mercadoria,
            "peso": peso_total,
            "volumes": volumes_total,
            "cubagem": cubagem
    }
    
    braspress_data = json.dumps(data)

    #TEST
    print("BRASPRESS JSON")
    print(braspress_data)

    async with httpx.AsyncClient() as client:
        tasks = [
            client.post(BRASPRESS_URL, json=braspress_data, headers=BRASPRESS_HEADERS),
            # client.post(PATRUS_URL, json=patrus_data, headers=PATRUS_HEADERS),
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
            results.append(response.json())

    # TEST
    print("Result:")
    print(results)
    print("Errors:")
    print(errors)

    return render_template('result.html', results=results, errors=errors, data=braspress_data)


if __name__ == '__main__':
    app.run(debug=True)