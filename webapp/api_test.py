import requests

# Definir la URL y los datos JSON a enviar
url = 'https://unirnavitzamna.azurewebsites.net/api/question'
#datos = {"pregunta": "¿Que peso tiene un electrón?", "identificador": "test-vector-index"}
#datos = {"pregunta": "¿Que son los rayos de luz?", "identificador": "test-vector-index"}
datos = {"pregunta": "En que se diferencia la reflexión de la refracción", "identificador": "test-vector-index"}

# Realizar la solicitud POST
response = requests.post(url, json=datos)

# Verificar el código de estado de la respuesta
if response.status_code == 200:
    # Extraer y mostrar el texto de la respuesta en formato JSON
    respuesta_json = response.json()
    if 'respuesta' in respuesta_json:
        print(respuesta_json['respuesta'])
    else:
        print("No se encontró la respuesta en el JSON de la respuesta.")
else:
    print(f"Se ha producido un error. Código: {response.status_code} Mensaje: {response.json['error']}")
