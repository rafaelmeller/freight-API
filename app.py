from flask import Flask, redirect, render_template, request, url_for
import requests
import os
import json

# isolate for TESTING
# auth_key = os.environ.get('BRASPRESS_AUTH_KEY')
# headers = {'Authorization': f'Basic {auth_key}'}   

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
        return input_string
    
    def sanitize_num(input_string):
        if "," in input_string:
            input_string = input_string.replace(",", ".")
        elif " " in input_string:
            input_string = input_string.replace(" ", "")   
        return input_string

    cnpj_remetente = int(sanitize_text(request.form['cnpj_remetente']))
    cnpj_destinatario = int(sanitize_text(request.form['cnpj_destinatario']))
    modalidade = "R" 
    cep_origem = int(sanitize_text(request.form['cep_origem']))
    cep_destino = int(sanitize_text(request.form['cep_destino']))
    print("cep_destino") #TEST
    tipo_frete = sanitize_text(request.form['tipo_frete'])
    print("tipo_frete") #TEST
    try:
        vlr_mercadoria = float(sanitize_num(request.form['vlr_mercadoria']))
    except ValueError:
        return error("Valor da mercadoria inválido", 400)
    print("vlr_mercadoria") #TEST
    try:
        peso_total = float(sanitize_num(request.form['peso_total']))
    except ValueError:
        return error("Valor do peso inválido", 400)
    print("peso_total") #TEST
    try:
        volumes_total = int(sanitize_num(request.form['volumes_total']))
    except ValueError:
        return error("Total de volumes inválido", 400)

    print("volumes_total") #TEST

    cubagem = []

    # TEST
    data_test = {
            "cnpjRemetente": cnpj_remetente,
            "cnpjDestinatario": cnpj_destinatario,
            "modal": modalidade,
            "tipoFrete": tipo_frete,
            "cepOrigem": cep_origem,
            "cepDestino": cep_destino,
            "vlrMercadoria": vlr_mercadoria,
            "peso": peso_total,
            "volumes": volumes_total,
    }
    print("Data test created")   
    
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

        
        
        altura = float(sanitize_num(request.form[altura_key]))
        largura = float(sanitize_num(request.form[largura_key]))
        comprimento = float(sanitize_num(request.form[comprimento_key]))
        volumes = int(sanitize_num(request.form[volumes_key]))

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
    return redirect(url_for('index'))




    # Isolated for TESTING
    # response = requests.post('https://api.braspress.com/v1/cotacao/calcular/json', json=data, headers=headers)
    # result = response.json()
    # return render_template('result.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)