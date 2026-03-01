# En la Raspberry Pi
import serial

# Usualmente es /dev/serial0, pero puede ser /dev/ttyS0 o /dev/ttyAMA0
puerto = serial.Serial('/dev/serial0', baudrate=9600, timeout=1)

print("Esperando datos...")

while True:
    if puerto.in_waiting:
        data = puerto.readline().decode('utf-8').strip()
        if data:
            print("Recibido:", data)
