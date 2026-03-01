import serial
import requests
API_URL="192.168.1.40:5000/API"
ser = serial.Serial(port='/dev/ttyS0',
                    baudrate=9600,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=1)
try:
    ser.reset_input_buffer()
    print("Esperando mensaje...")
    while True:    
        try:
            if ser.in_waiting>0:
                mensaje_recibido=ser.readline.decode('utf-8', errors='ignore')
                #mensaje_recibido=ser.read(100)
                if mensaje_recibido:
                    print(f"mensaje recibido: {mensaje_recibido}")
                    payload = {'dato':mensaje_recibido}
                    response = requests.post(API_URL, json=payload)
                    print("respuesta del servidor:", response.status_code, response.text)
        except Exception as e:
            print(e) 
except KeyboardInterrupt:
    print("Finalizando programa...")
except serial.SerialException as e:
    print(f"Error en el puerto serie: {e}")
finally:
    if ser and ser.is_open:
        ser.close()
    print("Puerto cerrado.")
