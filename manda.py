c# En tu PC
import serial
import time

# Cambiá COM3 por el puerto correcto que te asigne Windows
puerto = serial.Serial(
    port="COM6",
        baudrate=19200,
        bytesize=serial.EIGHTBITS,  # 8 bits de datos.
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,  # 1 bit de parada.  
        timeout=1,

)

while True:
    mensaje = input("Ingrese el mensaje a enviar (o 'exit' para salir): ")
    if mensaje.lower() == 'exit':
        break
    puerto.write((mensaje + '\n').encode('utf-8'))
    print("Mensaje enviado:", mensaje)

puerto.close()
