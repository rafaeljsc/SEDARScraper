import os
import requests
from dotenv import load_dotenv
load_dotenv(".env")

def graph() -> dict[str, str]:
    """Retorna um dicionário com Baerer Token para requests na Graph API."""

    url = f"https://login.microsoftonline.com/{os.getenv('AZURE_TENANT_ID')}/oauth2/v2.0/token"
    body = {
        "grant_type": "client_credentials",
        "client_id": os.getenv("AZURE_CLIENT_ID"),
        "client_secret": os.getenv("AZURE_CLIENT_SECRET"),
        "scope": "https://graph.microsoft.com/.default",
    }

    response = requests.post(url, data=body)  # noqa: S113
    response.raise_for_status()
    access_token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }