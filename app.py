from flask import Flask, flash, redirect, render_template, request, url_for
import requests
import os
import json

auth_key = os.environ.get('BRASPRESS_AUTH_KEY')
headers = {'Authorization': f'Basic {auth_key}'}   

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    
    cnpj_remetente = request.form['cnpj_remetente'].replace(".", "").replace("/", "").replace("-", "").replace(" ", "")
    cnpj_destinatario = request.form['cnpj_destinatario'].replace(".", "").replace("/", "").replace("-", "").replace(" ", "")
    modalidade = "R"
    tipo_frete = request.form['tipo_frete'].replace(" ", "")
    cep_origem = request.form['cep_origem'].replace(".", "").replace("-", "").replace(" ", "")
    cep_destino = request.form['cep_destino'].replace(".", "").replace("-", "").replace(" ", "")
    try:
        vlr_mercadoria = float(request.form['vlr_mercadoria'].replace(',', '.').replace(" ", ""))
    except ValueError:
        flash("Valor da mercadoria inválido")
        return redirect(url_for('index'))
    try:
        peso_total = float(request.form['peso_total'].replace(',', '.').replace(" ", ""))
    except ValueError:
        flash("Valor do peso total inválido")
        return redirect(url_for('index'))
    try:
        volumes_total = int(request.form['volumes_total'].replace(" ", ""))
    except ValueError:
        flash("Valor total de volumes inválido")
        return redirect(url_for('index'))
    
    cubagem = []

    volume_group_ids = request.form['volumeGroupIds'].split(',')

        # Dynamically handle volume groups
    for i in volume_group_ids:
        altura_key = f'altura{i}'
        largura_key = f'largura{i}'
        comprimento_key = f'comprimento{i}'
        volumes_key = f'volumes{i}'

        # Check if these keys exist in the form data
        if altura_key in request.form and largura_key in request.form and comprimento_key in request.form and volumes_key in request.form:
            altura = float(request.form[altura_key].replace(',', '.').replace(" ", ""))
            largura = float(request.form[largura_key].replace(',', '.').replace(" ", ""))
            comprimento = float(request.form[comprimento_key].replace(',', '.').replace(" ", ""))
            volumes = int(request.form[volumes_key].replace(" ", ""))

            # Store the volume group data
            cubagem.append({
                "altura": altura,
                "largura": largura,
                "comprimento": comprimento,
                "volumes": volumes
            })
        else:
            return flash(f"Campo do volume {i} está em branco")

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
    # Created just for testing
    json_string = json.dumps(data, indent=4)
    print(json_string)
    return redirect(url_for('index'))




    # Isolated for testing
    # response = requests.post('https://api.braspress.com/v1/cotacao/calcular/json', json=data, headers=headers)
    # result = response.json()
    # return render_template('result.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)