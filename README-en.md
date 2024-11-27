<h1 align="center" style="font-weight: bold;">Freight Quotation Project</h1>


  <div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white&style=for-the-badge" alt="Python Badge">
  <img src="https://img.shields.io/badge/Javascript-F7DF1E?logo=javascript&logoColor=white&style=for-the-badge" alt="JavaScript Badge">
  <img src="https://img.shields.io/badge/Flask-000000?logo=flask&logoColor=white&style=for-the-badge" alt="Flask Badge">
</div>


###### _Other versions:_ [_Clique aqui para Português_](./README-ptBR.md)

<h4 align="center"> 
     Status: Usable – Features in Progress 🚧
</h4>

<p align="center">
 <a href="#about-ℹ️">About</a> •
 <a href="#use-case-📦">Use Case</a> •
 <a href="#features-🌟">Features</a> •
 <a href="#layout-🎨">Layout</a> • 
 <a href="#project-demo-🖥️">Project Demo</a> •
 <a href="#app-architecture-🏗️">App Architecture</a> •
 <a href="#connected-freight-apis-🚛">Connected Freight APIs</a> •
 <a href="#setup-⚙️">Setup</a> • 
<a href="#future-work-and-known-limitations-🛠️">Future Work And Known Limitations</a> •
 <a href="#author-👨🏻‍💻">Author</a> • 
 <a href="#license-📝">License</a>
</p>

## About ℹ️
This project is a web application for freight quotation, which allows users from a specific company to input freight details and get quotations from different freight companies at once, instead of contacting the companies one by one.

It was built using Flask and Asyncio for the backend and JavaScript, CSS and html for the frontend.

## Use Case 📦

This web application was developed for Estrela D'Água, a small cooperative based in Aiuruoca, Brazil, that produces statues and sells them to stores across the country. The app simplifies and optimizes the freight quotation process by automating interactions with their primary freight providers, saving time and reducing manual effort.


## Features 🌟

- **Multi-company Freight Quotation**: Get quotes from several freight companies with a single submission, saving time and effort.
- **Asynchronous API Integration**: Efficient real-time cost and delivery time outputs via asynchronous API calls. Easily extendable to add new freight companies or services.
- **User Authentication**: Ensures secure access with login functionality, supporting hashed passwords for user verification. Only authorized users from the company can access the system.
- **Data Sanitization & Validation**: Input data is sanitized and validated to prevent errors and ensure accurate processing, helping to eliminate invalid or malicious inputs.
- **Email Notification**: Upon receiving a quotation, the system sends a confirmation email with the quote details to ensure proper tracking and record-keeping.
- **Scalability**: Designed to be easily scalable by integrating additional APIs for new freight companies or expanding functionality.


## Layout 🎨
![Home Page](./assets/home_page.png)
![Login Page](./assets/login_page.png)
![Quotation Page](./assets/quotation_page.png)


## Project Demo 🖥️
[Click here to watch the recorded demo](url-here)

##### Since the application uses private credentials, only a recorded demo is available for viewing.


## App Architecture 🏗️

1. **Backend (Flask)**:  
   - Handles user authentication, form submissions, and API requests to various freight companies;
   - Communicates with external APIs via asynchronous HTTP requests to fetch real-time data (costs, delivery times, etc.);
   - Data is processed, validated, and sanitized before being sent to the frontend or stored.
   
2. **Frontend (HTML, CSS, JavaScript)**:  
   - Provides an intuitive, user-friendly interface for entering shipment details (e.g., source, destination, weight);
   - Dynamically adds shipment volumes with a single click and automatically calculates their cubic weight.
   - Displays the results from multiple freight companies in a clean and organized manner;
   - The frontend is designed to be responsive, ensuring compatibility across devices, including mobile

3. **External APIs**:  
   - The application currently integrates with two freight company APIs(the two most used by Estrela D'Água, the company that uses it), fetching and parsing real-time freight information; 
   - Asynchronous calls ensure that the time taken is as short as possible (yet it still depends on the API response times).

4. **Database (Future Scalability)**:  
   - While the current version doesn’t include a database, the architecture is designed to be easily extendable to include one for storing user data, quotations, and shipping records by adding one or more functions related to this feature.

   ### **Workflow**:  
    1. **User Login**: Users authenticate via the backend.
    2. **Freight Quote Request**: The user enters shipment details via the frontend.
    3. **API Calls**: The backend fetches data from external APIs.
    4. **Result Handling**: Quotes are processed and displayed to the user.
    5. **Email Confirmation**: A confirmation email is sent to the user.


## Connected Freight APIs 🚛

The app connects to external APIs to fetch real-time shipping rates and delivery times:
##### Note that all the comments inside the json examples should be removed, as they are only explaining each field.

### Freight Company: Braspress
[Braspress Website](https://www.braspress.com/acesso-rapido/cotacao-online/)

- **Purpose**: Provides shipping costs and estimated delivery times.

- **Example Request**:
```json
{
    "cnpjRemetente": 60701190000104, # int
    "cnpjDestinatario": 30539356867, # int
    "modal": "R", # str
    "tipoFrete": "1", # str
    "cepOrigem": 2323000, # int
    "cepDestino": 7093090, # int
    "vlrMercadoria": 100.00, # float
    "peso": 50.55, # float
    "volumes": 10, # int
    "cubagem": [
        {
            "altura": 0.46, # float
            "largura": 0.67, # float
            "comprimento": 0.67, # float
            "volumes": 10 # int
        }
    ]
}
```

- **Example Response**:
```json
{
'id': 287242456, # int
'prazo': 4, # int
'totalFrete': 1.485,68 # float
}
```

### Freight Company: Patrus
[Patrus API Website](https://api-patrus.developer.azure-api.net/)

- **Purpose**: Provides the access token.
- **Example Request**:
```json

data=
{
  'username': "example", # input your 'str' user here
  'password': "example", # input your 'str' password here
  'grant_type': "password" # use 'password', fixed as it is
},

headers=
{
    'Content-Type': 'application/x-www-form-urlencoded',
    'Subscription': "example" # replace with your subscription token
}  
```

- **Example Response**:
```json
{
  "access_token": "example", # str
  "token_type": "example", # str
  "username": "example", # str
  "expires_in": 0 # int
}
```

- **Purpose**: Provides shipping costs and estimated delivery times.
- **Example of POST request**:

```json headers
{
  'Content-Type': 'application/json',
  'Authorization': f'Bearer access_token', # replace 'access_token' your access token
  'Subscription': "example" # replace with your subscription token
}
```

```json payload
{
  "CnpjTomador": "04.790.854/0001-70", # str
  "CepDestino": "88032-005", # str
  "CnpjCpf": "48.053.457/0001-90",  # or "000.000.000-00" for CPF (str)
  "Carga": {
      "Volumes": 1, # int
      "Peso": 20, # int
      "ValorMercadoria": 200.00 # float
  },
}
```


- **Example Response**:
```json
{
  'ValorFrete': 1485.68,
  'EntregaPrevista': '2021-09-30T00:00:00'
}
```


## Setup ⚙️
```bash
# Clone the repository
git clone <repository-url>

# Navigate to the project directory
cd <project-directory>

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install the dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env

# Edit the .env file with your credentials
# Defaut user is main_user
# Defaut password is 123456
# It is recommended to change the password through the app. (The user can be hardcoded in the .env file).

# Run the application
flask run
```

## Future Work and Known Limitations 🛠️

- **Database Integration:**
Currently, the app does not store user or quotation data. Future updates will include a database to enable record-keeping and improve data management.

- **Integration with Additional Freight Companies:**
The app is designed to scale and integrate more freight providers, making it even more versatile for logistics operations.

- **Address Validation via CEP (Zip Code):**
A planned feature will dynamically validate and retrieve address information based on the provided CEP. This will allow users to confirm the accuracy of the entered ZIP codes.

- **CNPJ/CPF Validation and Information Retrieval:**
Future updates will include automatic validation and retrieval of business (CNPJ) or personal (CPF) information. This feature will help users confirm the correctness of the provided data.

- **Result Generation Speed:**
Although asynchronous code is used to minimize delays, the speed of generating results is affected by the response times of the APIs from freight providers. As these external APIs are sometimes slow, the app must wait for their responses, causing a slight delay.

- **User Access Limitation:**
As this project was developed for a small company, it includes a single-user authentication mechanism. This feature prevents unauthorized access by external web users but is not designed for multi-user environments.

- **Restricted Access to Credentials and Demo:**
The app uses credentials that are specific to Estrela D'Água's service contracts with the freight companies Patrus and Braspress. Due to the sensitive nature of these credentials, they cannot be shared publicly. Additionally, the live website cannot be made public, but a recorded demonstration of the app is available.

## Author 👨🏻‍💻

This project was designed and developed by Rafael Meller

[![Linkedin Badge](https://img.shields.io/badge/-Rafael_Meller-blue?style=flat-square&logo=Linkedin&logoColor=white&link=https://www.linkedin.com/in/tgmarinho/)](https://www.linkedin.com/in/rafaelmeller/) 
[![Gmail Badge](https://img.shields.io/badge/-rafaelmeller.dev@gmail.com-c14438?style=flat-square&logo=Gmail&logoColor=white&link=rafaelmeller.dev@gmail.com)](mailto:rafaelmeller.dev@gmail.com)

## License 📝

This project is licensed under the [MIT](./LICENSE) license.