from flask import Flask, jsonify, render_template, request
import requests
from requests.auth import HTTPBasicAuth
import os
import json
import base64
from dotenv import load_dotenv
import httpx
import asyncio

load_dotenv()

app = Flask(__name__)

# Braspress credentials, headers and URL
braspress_username = os.environ.get('BRASPRESS_USERNAME_1')
braspress_password = os.environ.get('BRASPRESS_PASSWORD_1')
braspress_credentials = base64.b64encode(f'{braspress_username}:{braspress_password}'.encode('utf-8')).decode('utf-8')

# TEST
print(braspress_credentials)

braspress_headers = {
    'Authorization': f'Basic {braspress_credentials}',
    'Content-Type': 'application/json; charset=utf-8',
    'Accept': 'application/json',
}

braspress_url = "https://api.braspress.com/v1/cotacao/calcular/json"

# Patrus credentials and headers


patrus_url = "https://api-patrus.azure-api.net/api/v1/logistica/comercial/cotacoes/online"

# Paulineris credentials and headers


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
            client.post(braspress_url, json=braspress_data, headers=braspress_headers),
            # client.post(patrus_url, json=data, headers=patrus_headers),
            # client.post( , json=data, headers= )
        ]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

    results = []
    errors = []
    for response in responses:
        if isinstance(response, Exception):
            errors.append(str(response))
        else:
            results.append(response.json())

    # TO BE FIXED
    '''
    print("Result:", results)
    id = response.get('id')
    prazo = response.get('prazo')
    totalFrete = response.get('totalFrete')
    '''

    return render_template('result.html', results=results, errors=errors)


# TO BE FIXED
'''
@app.route('/api/response', methods=['GET'])
def handle_response():

    #TEST
    print("response handling working")

    # Retrieve "result" (witch is the response of the API request) from the JSON response
    result_string = request.args.get('var1')
    result = json.loads(result_string)
   

    # Retrieve "data" from the JSON response so the user can double-check the data sent
    data_string = request.args.get('var2')
    data = json.loads(data_string)
    print("Data:", data)

    # Get the data from "data" individually if needed
    """
    cnpjRemetente = data_dict.get('cnpjRemetente')
    cnpjDestinatario = data_dict.get('cnpjDestinatario')
    (...)
    cubagem_list = data_dict.get('cubagem')
    for cubagem in cubagem_list:
        altura = cubagem.get('altura')
        largura = cubagem.get('largura')
    """
    
    # Previous way of handling the response
    return render_template('result.html', id=id, prazo=prazo, totalFrete=totalFrete, data=data)
'''

if __name__ == '__main__':
    app.run(debug=True)