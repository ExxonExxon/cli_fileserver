import requests
import json, os
import getpass, questionary

API_URL = "http://127.0.0.1:5000"
USER_LOGIN_DATA_FILE = ".login_data.json"
logged_in = False

def auto_login_check():
    """
    """
    
    print("Checking if login json data exists...")

    if os.path.exists(USER_LOGIN_DATA_FILE):
        try:
            with open(USER_LOGIN_DATA_FILE)
        login()
        
    


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
        


def register():
    """
    Docstring for register
    Justs starts a registation form to register
    """
    
    system_username = getpass.getuser()
    
    while True:
        username = input("Please enter a username: ")
            
        if username == "" or username.startswith(" "):
            print("Invalid username.")
            return
            
        if not check_username_exists(username):
            print("Username does not exist! Lucky!")
            break
        else:
            print("Username exists... ")                
    
    while True:
        password = getpass.getpass("Enter your password: ")
        password_two = getpass.getpass("Re enter your password: ")
        
        if password == password_two:
            break
        else:
            print("Passwords do not match.")
            
    
    print(f"\nAttempting to register {username}...")
    
    json_data = {
        "username": username,
        "password": password,
    }

    response = send_post_request(json_data=json_data, url_string="register")
    
    if response[1] == 201:
        print("Registration Successful!")
    elif response[1] != 0:
        print("Registration successful")    
    
def login(json_data):
    print("Attempting to login...")
    
    if json_data is None:
    
        while True:
            username = input("Enter your username: ")

            if username == "" or username.startswith(" "):
                print("Please enter a valid username.")
                return
            
            if not check_username_exists(username=username):
                print("User does not exist...")
                return
            
            break    
        
        password = getpass.getpass("Enter your password: ")
        
        
        json_data = {
            "username": username,
            "password": password,
        }
        
        
    response = send_post_request(json_data=json_data, url_string="login")
    
    if response[1] == 200:
        print("Logged in successfully!")
        
        # Save username and password to json
        if questionary.confirm("Would you like to save login information to a json file? It will make logging in quicker next time.", default=True).ask():
            try:
                with open(USER_LOGIN_DATA_FILE, "w") as file:
                    json.dump(json_data, file, indent=4)
            except IOError as e:
                print(f"An error occured while trying write to file. {e}")
                
        
    elif response != 0:
        print(response[0])
        
    
        
        
        
            
    
        
    

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
    else:
        print(response)
        exit()
    


def main():
    
    if logged_in == False:
        print("Looks like you are not logged in. Make an account!")
        
        login()

if __name__ == "__main__": 
    main()