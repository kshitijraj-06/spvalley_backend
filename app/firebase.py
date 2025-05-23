import firebase_admin
import requests
from firebase_admin import credentials, auth
import os

FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")
def initialize_firebase():
    cred = credentials.Certificate(os.path.join(os.getcwd(), 'spvalley_serviceaccountkey.json'))
    firebase_admin.initialize_app(cred)

def generate_custom_token(email):
    user = auth.get_user_by_email(email)
    token = auth.create_custom_token(user.uid)
    return token.decode("utf-8")  # 🔥 Decode right here



def get_id_token(custom_token):
    """Exchange a custom token for an ID token."""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={FIREBASE_API_KEY}"
    payload = {
        "token": custom_token,
        "returnSecureToken": True,
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        id_token = response.json().get("idToken")
        print("Generated ID Token:", id_token)
        return id_token
    else:
        print("Error:", response.json())
        print("Custom Token:", custom_token)
        return None
