import requests
import json
import os
import getpass
import questionary
import sys
import random

API_URL = "http://127.0.0.1:5000"
USER_LOGIN_DATA_FILE = ".login_data.json"
USER_CREDENTIALS = {}
LOGGED_IN = False


def save_credentials_to_file(USER_CREDENTIALS):
    if questionary.confirm("Would you like to save login information to a json file? It will make logging in quicker next time.", default=True).ask():
        try:
            with open(USER_LOGIN_DATA_FILE, "w") as file:
                json.dump(USER_CREDENTIALS, file, indent=4)
        except IOError as e:
            print(f"An error occured while trying write to file. {e}")


def auto_login_check():
    print("Checking if login json data exists...")

    if os.path.exists(USER_LOGIN_DATA_FILE):
        try:
            with open(USER_LOGIN_DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                print("save file exists")
                login(json_data=data)
        except IOError as e:
            print("Error reading file, ")


def check_username_exists(username: str) -> bool:
    """
    Docstring for check_username_exists

    :param username: Username to check with the server if it exists
    :type username: str
    """

    print("Checking if the username exists...")

    json_data = {
        "username": username,
    }

    response = send_post_request(
        json_data=json_data, url_string="check_username")

    if response[1] == 200:
        return response[0]["exists"]
    else:
        print(response)
        sys.exit()


def check_email_exists(email: str) -> bool:
    print("Checking if email exists")

    json_data = {
        "email": email,
    }

    response = send_post_request(
        json_data=json_data, url_string="check_email")

    if response[1] == 200:
        return response[0]["exists"]
    else:
        print(response)
        sys.exit()


def username_suggestion(used_username: str) -> str:
    while True:
        random_number = random.randint(0, 999999)
        suggested_username = f"{used_username}.{random_number}"

        if not check_username_exists(suggested_username):
            return suggested_username


def send_post_request(json_data: json, url_string: str):
    """
    Docstring for send_post_request

    :param json_data: Data to send to the server
    :type json_data: json
    :param url_string: url string example: signup, do not add /
    :type url_string: str
    """

    print(f" -- Sending a request to {API_URL}/{url_string}")
    try:
        response = requests.post(f"{API_URL}/{url_string}", json=json_data)
        response.raise_for_status()

        return response.json(), response.status_code

    except requests.exceptions.HTTPError as e:
        error_msg = e.response.json().get('error')
        print(f"Failed to send requests to server. (Status {
              e.response.status_code}): {error_msg}")

        return None, response.status_code

    except requests.exceptions.ConnectionError:
        print("Could not connect to the server...")

        return None, 0


def register():
    """
    Docstring for register
    Justs starts a registation form to register
    """
    global USER_CREDENTIALS, LOGGED_IN

    while True:
        username = questionary.text("What is your name?: ").ask()

        if check_username_exists(username):
            suggested_username = username_suggestion(username)
            print("Username is not available.")
            print(f"Suggestion: You could try '{suggested_username}' instead.")

            if questionary.confirm(f"Do you want to use {suggested_username}?",
                                   default=True).ask():
                username = suggested_username
                break
        else:
            break

    while True:
        email = questionary.text("What is your email?").ask()

        if not check_email_exists(email=email):
            break
        else:
            print("That email is used. Maybe you put in the wrong email?")
            

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
        "email": email,
        "password": password,
    }

    response = send_post_request(json_data=json_data, url_string="register")

    if response[1] == 201:
        print("Registration Successful!")
        USER_CREDENTIALS = json_data
        LOGGED_IN = True
        save_credentials_to_file(USER_CREDENTIALS)
    elif response[1] != 0:
        print("Registration successful")


def login(json_data=None):
    """
    Logs user in
    """
    global USER_CREDENTIALS, LOGGED_IN

    print("Attempting to login...")
    auto_login = True

    if json_data is None:
        auto_login = False

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

        USER_CREDENTIALS = json_data
        LOGGED_IN = True

        if auto_login is False:
            save_credentials_to_file(USER_CREDENTIALS)

    elif response != 0:
        print(response[0])


def logout() -> bool:
    global LOGGED_IN, USER_CREDENTIALS
    if questionary.confirm("Are you sure you want to logout?",
                           default=True).ask():
        try:
            os.remove(USER_LOGIN_DATA_FILE)
        except FileNotFoundError:
            pass
        LOGGED_IN = False
        USER_CREDENTIALS = None
        print("Successfully logged out!")
        return True
    else:
        return False


def view_user_data() -> json:
    pass


def main():
    while True:
        if LOGGED_IN:
            print(f"Welcome {USER_CREDENTIALS["username"]}")

            action = questionary.select("What would you like to do?",
                choices=[
                    "See my notes",
                    "See my data",
                    "Logout",
                    "Exit"
                ]).ask()
            
            match action:
                case "Logout":
                    logout()
                case "See my notes":
                    print("Still in production")
                case "See my data":
                    print("Still in production")
                case "Exit":
                    sys.exit()
                case _:
                    sys.exit()

        else:
            action = questionary.select("To continue you must signup or login.",
                choices=[
                    "Login",
                    "Signup"
            ]).ask()

            match action:
                case "Signup":
                    register()
                case "Login":
                    login()
                case _:
                    sys.exit()

if __name__ == "__main__":
    auto_login_check()
    main()
