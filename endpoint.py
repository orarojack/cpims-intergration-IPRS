import json
import tkinter as tk
from tkinter import messagebox
from zeep import Client
from zeep.exceptions import Fault
from zeep.helpers import serialize_object

# WSDL service URL
wsdl_url = 'https://dev.cpims.net/IPRSServerwcf?wsdl'

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")

        # Username input
        tk.Label(root, text="Username").pack()
        self.username_entry = tk.Entry(root)
        self.username_entry.pack()

        # Password input
        tk.Label(root, text="Password").pack()
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack()

        # Login button
        self.login_button = tk.Button(root, text="Login", command=self.login)
        self.login_button.pack()

        # ID number input (hidden initially)
        tk.Label(root, text="ID Number").pack()
        self.id_entry = tk.Entry(root)
        self.id_entry.pack()
        self.id_entry.pack_forget()  # Hide ID entry

        # Fetch data button (hidden initially)
        self.fetch_button = tk.Button(root, text="Fetch Data", command=self.fetch_data)
        self.fetch_button.pack()
        self.fetch_button.pack_forget()  # Hide fetch button

        # Initialize client
        self.client = None
        self.session_token = None

    def check_wsdl_connection(self):
        try:
            self.client = Client(wsdl=wsdl_url)
            print("Connection to WSDL service successful!")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")

    def create_login_payload(self, username, password):
        return {
            'log': username,
            'pass': password
        }

    def perform_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        login_payload = self.create_login_payload(username, password)

        try:
            response = self.client.service.Login(**login_payload)
            print("Raw response:", response)  # Debugging line
            response_dict = serialize_object(response)

            if response_dict and response_dict.get('LoginSuccess', False):
                print("Login successful!")
                self.session_token = response_dict.get('SessionToken')
                self.show_id_entry()
            else:
                messagebox.showerror("Login Failed", "Invalid credentials, please try again.")

        except Fault as fault:
            messagebox.showerror("SOAP Fault", str(fault))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_id_entry(self):
        self.id_entry.pack()  # Show ID entry
        self.fetch_button.pack()  # Show fetch button
        self.login_button.pack_forget()  # Hide login button

    def fetch_data(self):
        id_number = self.id_entry.get()

        input_payload = {
            'id_number': id_number,
            'session_token': self.session_token
        }

        try:
            response = self.client.service.GetDataByIdCard(**input_payload)
            print("Raw response:", response)  # Debugging line
            response_dict = serialize_object(response)

            if not response_dict.get('ErrorOccurred', True):
                print("Person's Data Retrieved Successfully:")
                print(json.dumps(response_dict, indent=4))
                messagebox.showinfo("Data Retrieved", json.dumps(response_dict, indent=4))
            else:
                messagebox.showerror("Error", response_dict.get('ErrorMessage', 'Unknown error'))

        except Fault as fault:
            messagebox.showerror("SOAP Fault", str(fault))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def login(self):
        self.check_wsdl_connection()
        if self.client:
            self.perform_login()

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
