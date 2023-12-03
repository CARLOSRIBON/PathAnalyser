import requests
import datetime
import os


URL = "https://nuug6fk6jrj7utq2tnsgnyj4iy.apigateway.us-ashburn-1.oci.customer-oci.com/pocbancolombia"


def send_message(message) -> None:
    timestamp = datetime.datetime.now().strftime("%b %d %H:%M:%S")
    hostname = os.uname().nodename
    print(f"Enviando mensaje: {message}")
    try:
        response = requests.post(
            URL,
            data={"timestamp": timestamp, "hostname": hostname, "message": message},
            timeout=5,
        )
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar mensaje: {e}")
        return e
