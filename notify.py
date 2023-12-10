import requests
import datetime
import os

from requests import Response

from logger_config import setup_logger


URL = "https://nuug6fk6jrj7utq2tnsgnyj4iy.apigateway.us-ashburn-1.oci.customer-oci.com/cloud_to_webex"


def send_message(message, tittle, hop, path) -> Response:
    logger = setup_logger()
    timestamp = datetime.datetime.now().strftime("%b %d %H:%M:%S")
    hostname = os.uname().nodename

    try:
        response = requests.post(

            URL,
            data={
                "timestamp": timestamp,
                "hostname": hostname,
                "titulo": tittle,
                "message": message,
                "hop": hop,
                "path": str(path),
            },
            timeout=5,
        )
        return response
    except requests.exceptions.RequestException as e:
        logger.error(e)
