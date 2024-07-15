from flask import Flask, redirect, render_template, request, url_for
import requests
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
    # TEST
    json_string = json.dumps(data, indent=4)
    print("JSON STRING")
    print(json_string)

    user1_braspress = os.environ.get('API_BRASPRESS_USERNAME1')
    pass1_braspress = os.environ.get('API_BRASPRESS_PASSWORD1')

    #TEST
    print(user1_braspress)
    print(pass1_braspress)
    username = user1_braspress
    password = pass1_braspress

    # Isolated for testing purposes
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
    headers = {'Authorization': f'Basic {credentials}'}

    # TEST
    print(headers)
    print(credentials)

    response = requests.post('https://api.braspress.com/v1/cotacao/calcular/json', json=data, headers=headers)
    
    if response.status_code == 200:
        # Assuming JSON response for simplicity. For XML, you'll need an XML parser.
        result = response.json()
        json_string = json.dumps(data, indent=4)
        # Extracting the relevant information from the response
        id = result.get('id')
        prazo = result.get('prazo')
        totalFrete = result.get('totalFrete')
        # You can now pass these values to your template or handle them as needed
        return render_template('result.html', id=id, prazo=prazo, totalFrete=totalFrete, json_string=json_string)
    else:
        if response.content and 'application/json' in response.headers.get('Content-Type', ''):
            try:
                error_response = response.json()  # Attempt to parse JSON
                statusCode = error_response.get('statusCode')
                message = error_response.get('message')
                dateTime = error_response.get('dateTime')
                errorList = error_response.get('errorList', [])
            except ValueError:  # Includes json.JSONDecodeError
                # Fallback if JSON parsing fails
                statusCode = response.status_code
                message = "Um erro com a API ocorreu: ValueError. Contate o suporte técnico."
                dateTime = None
                errorList = []
        else:
            # Handle non-JSON responses or empty bodies
            statusCode = response.status_code
            message = "Um erro inesperado ocorreu, contate o suporte técnico."
            dateTime = None
            errorList = []

        return render_template('error.html', error_message=message, code=statusCode, dateTime=dateTime, errorList=errorList)


if __name__ == '__main__':
    app.run(debug=True)