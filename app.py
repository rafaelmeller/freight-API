# This project was developed with the assistance of GitHub Copilot and CS50's Duck Debugger (ddb).

import asyncio
import httpx
from datetime import datetime
from flask import Flask, render_template, request
from helpers import (
    send_email, format_datetime, format_currency, sanitize_text, sanitize_int, sanitize_float,
    get_patrus_headers, BRASPRESS_HEADERS, BRASPRESS_URL, PATRUS_URL, CUBIC_FACTOR
)

app = Flask(__name__)


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
        email_envio = request.form['email_envio']
        email_envio = email_envio.strip()
    except ValueError:
        return error("E-mail do destinatário inválido", 400)

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
    valor_mercadoria = format_currency(vlr_mercadoria)

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
        "vlrMercadoria": valor_mercadoria,
        "peso": peso_total,
        "volumes": volumes_total,
        "pesoCubado": total_cubic_weight,
        "cubagem": cubagem
    }

    async with httpx.AsyncClient() as client:
        tasks = [
            client.post(BRASPRESS_URL, json=braspress_data, headers=BRASPRESS_HEADERS, timeout=30.0),
        ]
        if patrus_headers:
            tasks.append(client.post(PATRUS_URL, json=patrus_data, headers=patrus_headers, timeout=30.0))
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
                    'message': e.response.text
                }

    # PADRONIZING THE RESULTS
    # Braspress
    if results[0]:
        value_result = results[0]['totalFrete']
        delivery_date, delivery_time = format_datetime(results[0]['prazo'])
        results[0]['entrega'] = delivery_date
        results[0]['prazo'] = delivery_time
        results[0]['totalFrete'] = format_currency(value_result)

        #TEST
        print("Results 0")
        print(results[0]['prazo'])
        print(results[0])

    # Patrus
    if results[1]:
        value_result = results[1]['ValorFrete']
        delivery_date, delivery_time = format_datetime(results[1]['EntregaPrevista'])
        results[1]['entrega'] = delivery_date
        results[1]['prazo'] = delivery_time
        results[1]['ValorFrete'] = format_currency(value_result)

        #TEST
        print("Result 1")
        print(results[1]['EntregaPrevista'])
        print(results[1])

    # SENDING EMAIL
    recipient_email = email_envio 
    date = datetime.now().strftime("%d/%m/%Y às %H:%M")
    price = f"{vlr_mercadoria:.2f}"
    subject = f"Cotação para {nome_fantasia} | valor do pedido: R$ {price} | {date}"
    html_content = render_template('email_result.html', results=results, errors=errors, data=main_data, header_error=header_error, date=date)

    email_success, email_error = send_email(subject, recipient_email, html_content)
    
    return render_template('result.html', results=results, errors=errors, data=main_data, header_error=header_error, email_success=email_success, email_error=email_error)

if __name__ == '__main__':
    app.run(debug=True)