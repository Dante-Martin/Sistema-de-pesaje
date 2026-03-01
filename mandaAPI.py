
import requests
API_URL="http://192.168.1.40:5000/api/endpoint"
headers = {
    'Content-Type': 'application/json',
    # 'Authorization': 'Bearer TU_TOKEN',  # Si necesitas autorización
}
 
try:

        mensaje_recibido="prpe"

        if mensaje_recibido:
            print(f"mensaje recibido: {mensaje_recibido}")
            payload = {'dato':mensaje_recibido}
            response = requests.post(API_URL, json=payload, headers=headers)
            print("respuesta del servidor:", response.status_code, response.text)
except Exception as e:
    print(e) 
