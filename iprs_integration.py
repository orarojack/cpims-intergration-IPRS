import json
from zeep import Client
from zeep.exceptions import Fault
from zeep.helpers import serialize_object

# WSDL service URL
wsdl_url = 'https://dev.cpims.net/IPRSServerwcf?wsdl'


def check_wsdl_connection():
    try:
        client = Client(wsdl=wsdl_url)
        print("Connection to WSDL service successful!")
        return client
    except Exception as e:
        print(f"Failed to connect to WSDL service: {e}")
        return None


def create_login_payload(username, password):
    return {
        'log': username,
        'pass': password
    }


def perform_login(client):
    username = input("Enter username: ")
    password = input("Enter password: ")

    # Create login payload
    login_payload = create_login_payload(username, password)

    try:
        # Login credentials
        response = client.service.Login(**login_payload)
        print("Raw response:", response)  # Debugging line
        response_dict = serialize_object(response)

        if response_dict and response_dict.get('LoginSuccess', False):
            print("Login successful!")
            return response_dict.get('SessionToken')  # Or relevant token/session id
        else:
            print("Invalid credentials, please try again.")
            return None

    except Fault as fault:
        print(f"SOAP Fault during login: {fault}")
        return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def get_data_by_id(client, token):
    id_number = input("Enter ID number: ")

    input_payload = {
        'id_number': id_number,
        'session_token': token  # Assuming session token or similar is needed
    }

    try:
        response = client.service.GetDataByIdCard(**input_payload)
        print("Raw response:", response)  # Debugging line
        response_dict = serialize_object(response)

        if not response_dict.get('ErrorOccurred', True):
            print("Person's Data Retrieved Successfully in JSON Format:")
            print(json.dumps(response_dict, indent=4))
        else:
            print(f"Error: {response_dict.get('ErrorMessage', 'Unknown error')}")

    except Fault as fault:
        print(f"SOAP Fault: {fault}")
    except Exception as e:
        print(f"An error occurred: {e}")


# Main program
client = check_wsdl_connection()

if client:  # Proceed only if the WSDL connection was successful
    while True:
        # Perform login
        session_token = perform_login(client)

        # Fetch data
        if session_token:
            get_data_by_id(client, session_token)
            break
        else:
            print("Login failed. Please try again.")
