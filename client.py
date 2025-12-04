import requests
import json
import time

API_URL = "http://127.0.0.1:5000"
logged_in = False

def send_post_request(json_data: json, url_string: str):
    """
    Docstring for send_post_request
    
    :param json_data: Data to send to the server
    :type json_data: json
    :param url_string: url string example: signup, do not add / or anything before that
    :type url_string: str
    """


    print(f"Sending a request to {API_URL}/{url_string}")
    try:
        response = requests.post(f"{API_URL}/{url_string}", json=json_data)
        response.raise_for_status()

        return response.json(), response.status_code
    
    except requests.exceptions.HTTPError as e:
        error_msg = e.response.json().get('error')
        print(f"Failed to send requests to server. (Status {e.response.status_code}): {error_msg}")

        return None, response.status_code
    
    except requests.exceptions.ConnectionError:
        print("Could not connect to the server...")

        return None, 0
        


def register(username: str, password: str):
    """
    Docstring for register
    
    :param username: Username, it has to be unique but this gets checked
    :type username: str
    :param password: Just the password to register with, this will be hashed before storing into the server
    :type password: str
    """
    
    print(f"\nAttempting to register user '{username}'...")
    
    json_data = {
        "username": username,
        "password": password,
    }

    return send_post_request(json_data=json_data, url_string="register")

def check_username_exists(username: str):
    """
    Docstring for check_username_exists
    
    :param username: Username to check with the server if it exists
    :type username: str
    """

    print("Checking if the username exists...")

    json_data = {
        "username": username,
    }

    response = send_post_request(json_data=json_data, url_string="check_username")

    if response[1] == 200:
        return response[0]["exists"]
    

def main():
    
    if logged_in == False:
        print("Looks like you are not logged in. Make an account!")
        
        username = ""
        password = ""
        
        # --- Username Input Loop ---
        while True:
            # Get username and keep reasking for a username if its already used
            username = input("Enter your username: ")
            
            if check_username_exists(username=username):
                print("That username already exists! Please try a different one.")
                # FIX: Loop continues back to the start of the while loop
                continue 
            else:
                break # Exit the username loop if the username is available
            
        # --- Password Input Loop ---
        while True:
            # Check for a password, keep reasking if it got the password again prompt wrong
            password = input("Enter a password: ")
            chck_password = input("Input the password again: ")
            
            if chck_password != password:
                print("Passwords don't match... Please try again.")
                # FIX: Loop continues back to the start of the while loop
                continue 

            break # Exit the password loop if passwords match
        
        # --- Registration ---
        response_data, status_code = register(username=username, password=password)
        
        if status_code == 201:
            print("🎉 Registration successful!")
        elif status_code != 0:
            print("Registration failed.")
     

if __name__ == "__main__": 
    main()