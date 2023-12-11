# Import necessary libraries
import requests
import datetime
import os

# Import custom logger configuration
from logger_config import setup_logger

# Define the URL for the API endpoint
URL = "https://nuug6fk6jrj7utq2tnsgnyj4iy.apigateway.us-ashburn-1.oci.customer-oci.com/cloud_to_webex"


# Function to send a message to the specified URL
def send_message(message, tittle, hop, path):
    # Setup logger
    logger = setup_logger()

    # Get current timestamp and hostname
    timestamp = datetime.datetime.now().strftime("%b %d %H:%M:%S")
    hostname = os.uname().nodename

    try:
        # Send a POST request to the URL with the specified data
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
        # Return the response from the request
        return response
    except requests.exceptions.RequestException as e:
        # Log any exceptions that occur
        logger.error(e)