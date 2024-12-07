# This project was developed by me with the assistance of GitHub Copilot and CS50's Duck Debugger (ddb).
# Part of the Flask code was copied from my version of CS50's project "Finance"

import asyncio
import httpx
import os
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from flask import Blueprint, Flask, render_template, request, session, redirect, url_for
from flask_session import Session
from helpers import (
    fetch_data, format_datetime, format_currency, get_headers, login_required, sanitize_float, sanitize_int,
    sanitize_text, send_email, update_env, CUBIC_FACTOR
)
from werkzeug.security import check_password_hash, generate_password_hash

# Clear any cached environment variables
os.environ.clear()

# Ensures .env file is properly loaded form the file system
load_dotenv(find_dotenv())

app = Flask(__name__)

cotacao_bp = Blueprint('cotacao', __name__, url_prefix='/cotacao')

@cotacao_bp.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@cotacao_bp.route('/')
@login_required
def index():
    return render_template('index.html')


@cotacao_bp.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return error("Insira seu nome de usuário", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return error("insira sua senha", 403)

        # Reload environment variables
        load_dotenv()

        # Query .env for username
        username = os.environ.get('MAIN_USER')
        user_password = os.environ.get('MAIN_PASSWORD_HASH')

        input_password = request.form.get("password")

        # Ensure username exists and password is correct
        if not check_password_hash(user_password, input_password):
            return error("Senha inválida", 403)
        elif username != request.form.get("username"):
            return error("Usuário não existe", 403)

        # Remember which user has logged in
        session["user_id"] = username

        # Redirect user to home page
        return redirect(url_for('cotacao.index'))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Reload environment variables
        load_dotenv(find_dotenv())
        
        return render_template("login.html")


@cotacao_bp.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect(url_for('cotacao.login'))


@cotacao_bp.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        user_password = os.environ.get('MAIN_PASSWORD_HASH')
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        input_password = request.form.get("password")

        # Ensure id exists and password is correct
        if not check_password_hash(user_password, input_password):
            return error("Senha atual incorreta", 403)

        # Ensure password and validation was submitted and are the same
        if not confirmation == new_password:
            return error("Nova senha e confirmação são diferentes", 403)

        # Generate a hash for the new password
        hash = generate_password_hash(new_password)

        # Insert new hash in database
        update_env("MAIN_PASSWORD_HASH", hash)

        # Reload environment variables
        load_dotenv(find_dotenv())
        user_password = os.environ.get('MAIN_PASSWORD_HASH')

        # Inform if the password was updated
        if not check_password_hash(user_password, new_password):
            password_error = "Erro ao alterar a senha!"
            return render_template("index.html", password_error=password_error)
        else:
            password_success = "Senha alterada com sucesso!"
            return render_template("index.html", password_success=password_success)

    else:
        return render_template("change_password.html")


@cotacao_bp.route('/error/<int:code>/<path:error_message>')
def error(error_message="Erro inesperado", code=400):
    return render_template('error.html', error_message=error_message, code=code)


@cotacao_bp.route('/submit', methods=['POST'])
@login_required
def submit():

    # Initialize errors and results array (add one slot for each freight company)
    errors = [None, None]
    results = [None, None]
    header_error = [None, None]

    # Get the headers for the API requests
    braspress_headers, header_error[0] = asyncio.run(get_headers("braspress"))
    patrus_headers, header_error[1] = asyncio.run(get_headers("patrus"))

    # GET DATA FROM FORM

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
        cubic_weight = (altura * largura * comprimento) * \
            CUBIC_FACTOR * volumes
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

    display_data = {
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

    braspress_list = [braspress_data, braspress_headers]
    patrus_list = [patrus_data, patrus_headers]

    responses = asyncio.run(fetch_data(braspress_list, patrus_list))

    for i, response in enumerate(responses):

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
    # Response defaut format: {'id': 287242456, 'prazo': 4, 'totalFrete': 1.485,68}
    if results[0]:
        value_result = results[0]['totalFrete']
        delivery_date, delivery_time = format_datetime(results[0]['prazo'])
        results[0]['entrega'] = delivery_date
        results[0]['prazo'] = delivery_time
        results[0]['totalFrete'] = format_currency(value_result)  

    # Patrus
    # Response defaut format: {'ValorFrete': 1485.68, 'EntregaPrevista': '2021-09-30T00:00:00'}
    if results[1]:
        value_result = results[1]['ValorFrete']
        delivery_date, delivery_time = format_datetime(results[1]['EntregaPrevista'])
        results[1]['entrega'] = delivery_date
        results[1]['prazo'] = delivery_time
        results[1]['ValorFrete'] = format_currency(value_result)

    # SENDING EMAIL
    recipient_email = email_envio
    date = datetime.now().strftime("%d/%m/%Y às %H:%M")
    price = f"{vlr_mercadoria:.2f}"
    subject = f"Cotação para {nome_fantasia} | valor do pedido: R$ {price} | {date}"
    html_content = render_template('email_result.html', results=results, errors=errors, data=display_data, header_error=header_error, date=date)

    email_success, email_error = send_email(
        subject, recipient_email, html_content)

    return render_template('result.html', results=results, errors=errors, data=display_data, header_error=header_error, email_success=email_success, email_error=email_error)


# Register the Blueprint
app.register_blueprint(cotacao_bp)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

if __name__ == '__main__':
    app.run(debug=True)
