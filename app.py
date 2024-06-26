from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

@app.route('/quote', methods=['POST'])
def get_quote():
    data = request.json
    response = requests.post('https://api.braspress.com/v1/cotacao/calcular/json', json=data, headers={'Authorization': 'Basic YOUR_AUTH'})
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True)