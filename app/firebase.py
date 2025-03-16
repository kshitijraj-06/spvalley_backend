import firebase_admin
import requests
from firebase_admin import credentials, auth
import os

FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")
def initialize_firebase():
    cred = credentials.Certificate(os.path.join(os.getcwd(), 'spvalley_serviceaccountkey.json'))
    firebase_admin.initialize_app(cred)

def generate_custom_token(email):
    """Generate a custom token for a user."""
    user = auth.get_user_by_email(email)
    return auth.create_custom_token(user.uid).decode("utf-8")


def get_id_token(custom_token):
    """Exchange a custom token for an ID token."""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={FIREBASE_API_KEY}"
    payload = {"token": custom_token, "returnSecureToken": True}

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        id_token = response.json().get("idToken")
        print("Generated ID Token:", id_token)  # Print ID Token
        return id_token
    else:
        print("Error:", response.json())
        return None