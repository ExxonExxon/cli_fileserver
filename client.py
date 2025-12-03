import requests
import json
import time

API_URL = "http://127.0.0.1:5000"
logged_in = False

def register(username, password):
    print(f"\nAttempting to register user '{username}'...")
    try:
        response = requests.post(f"{API_URL}/register", json={
            "username": username,
            "password": password,
        })
        response.raise_for_status() # Raise an exception for 4xx or 5xx errors
        return response.json(), response.status_code
    except requests.exceptions.HTTPError as e:
        error_msg = e.response.json().get('error', 'Unknown error')
        print(f"Registration failed (Status {e.response.status_code}): {error_msg}")
        return None, e.response.status_code
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the Flask server. Is app.py running?")
        return None, 0

def check_username_exists(username):
    try:
        response = requests.post(f"{API_URL}/check_username", json={
            "username": username,
        })
        
        # Check if the response was successful
        if response.status_code == 200:
            # FIX: Extract the boolean value 'exists' from the server's JSON response
            return response.json().get("exists", False)
        
        # Handle non-200 status codes (e.g., 400 if no username was sent)
        print(f"Server check failed (Status {response.status_code}): {response.json().get('error', 'Unknown error')}")
        return False

    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the Flask server. Is app.py running?")
        return True # Return True to prevent registration attempt if server is down

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