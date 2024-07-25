from flask import Flask, jsonify, render_template, request, url_for
import requests
from requests.auth import HTTPBasicAuth
import os
import json
import base64
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/error/<int:code>/<path:error_message>')
def error(error_message, code):
    return render_template('error.html', error_message=error_message, code=code)

@app.route('/submit', methods=['POST'])
def submit():
    # TEST
    print("submission working")

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

    print("main forms succesful") #TEST 
    
    print(request.form['volumeGroupIds']) #TEST

    volume_group_ids = request.form['volumeGroupIds'].split(",")   

    print(volume_group_ids) #TEST
    print(request.form) #TEST

        # Dynamically handle volume groups
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
    
    user1_braspress = os.environ.get('API_BRASPRESS_USERNAME1')
    pass1_braspress = os.environ.get('API_BRASPRESS_PASSWORD1')

    #TEST
    username = user1_braspress
    password = pass1_braspress

    # Isolated for testing purposes, will be developed further
    '''
    user2_braspress = os.environ.get('API_BRASPRESS_USERNAME2')
    pass2_braspress = os.environ.get('API_BRASPRESS_PASSWORD2')
    credentials_index = request.form['credential_index']

    credentials_list = [
        {'username': user1_braspress, 'password': pass1_braspress},
        {'username': user2_braspress, 'password': pass2_braspress}
    ]

    selected_credentials = credentials_list[int(credentials_index)]
    username = selected_credentials['username']
    password = selected_credentials['password']
    '''
    credentials = base64.b64encode(f'{username}:{password}'.encode('utf-8')).decode('utf-8')
    data_json = json.dumps(data)

    #TEST
    print("JSON STRING")
    print(data_json)

    # TEST
    print(credentials)

    return render_template('submit.html', data_json=data_json, credentials=credentials)

@app.route('/api/response', methods=['POST'])
def handle_response():

    #TEST
    print("response handling working")

    # Retrieve "result" (witch is the response of the API request) from the JSON response
    result = request.json.get('result')
    id = result.get('id')
    prazo = result.get('prazo')
    totalFrete = result.get('totalFrete')

    # Retrieve "data" from the JSON response so the user can double-check the data sent
    data_string = request.json.get('data')
    data = json.loads(data_string)
    json_string = json.dumps(data, indent=4)

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
    
    #TEST
    print(id, prazo, totalFrete)
    print(json_string)
    
    # Pass these values to your template or handle them as needed
    return render_template('result.html', id=id, prazo=prazo, totalFrete=totalFrete, json_string=json_string)

@app.route('/api/error', methods=['POST'])
def handle_error():
    
    #TEST
    print("error handling working")

    error_data = request.json
    if not error_data:
        print("No JSON data received")
    # Assuming the error data format includes statusCode, message, dateTime, and errorList
    statusCode = error_data.get('status')
    message = error_data.get('statusText')
    responseText = error_data.get('responseText')

    #TEST
    print(statusCode, message, responseText)

    # Pass these values to your template or handle them as needed
    return render_template('error.html', error_message=message, code=statusCode, responseText=responseText)
if __name__ == '__main__':
    app.run(debug=True)