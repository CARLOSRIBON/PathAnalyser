import requests
import datetime
import os


URL = "https://nuug6fk6jrj7utq2tnsgnyj4iy.apigateway.us-ashburn-1.oci.customer-oci.com/cloud_to_webex"


def send_message(message, path) -> None:
    timestamp = datetime.datetime.now().strftime("%b %d %H:%M:%S")
    hostname = os.uname().nodename

    try:
        response = requests.post(
            URL,
            data={"timestamp": timestamp, "hostname": hostname, "message": message, "path":str(path)},
            timeout=5,
        )
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar mensaje: {e}")
        return e
