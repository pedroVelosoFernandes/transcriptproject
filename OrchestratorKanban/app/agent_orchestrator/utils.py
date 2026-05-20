from boto3.session import Session
import requests
import time
import boto3
import base64
import hashlib
import hmac

def calculate_secret_hash(username: str, client_id: str, client_secret: str) -> str:
    message = (username + client_id).encode("utf-8")
    key = client_secret.encode("utf-8")
    digest = hmac.new(key, message, digestmod=hashlib.sha256).digest()
    return base64.b64encode(digest).decode()


def get_token(
    user_pool_id: str,
    client_id: str,
    client_secret: str,
    REGION: str,
    username: str | None = None,
) -> dict:
    try:
        user_pool_id_without_underscore = user_pool_id.replace("_", "")
        url = f"https://{user_pool_id_without_underscore}.auth.{REGION}.amazoncognito.com/oauth2/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        }
        if username:
            data["SECRET_HASH"] = calculate_secret_hash(username, client_id, client_secret)
            print(data["SECRET_HASH"])
        print(client_id)
        print(client_secret)
        
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as err:
        return {"error": str(err)}

def get_cognito_token() -> str:
    """
    Obtém o token de acesso do Cognito usando os parâmetros armazenados no SSM
    """
    boto_session = Session()
    region = boto_session.region_name
    
    # Recupera os parâmetros do SSM
    user_pool_id = get_ssm_parameter("/app/kanban/agentcore/user_pool_id")
    client_id = get_ssm_parameter("/app/kanban/agentcore/client_id")
    client_secret = get_ssm_parameter("/app/kanban/agentcore/client_secret")
    username = get_ssm_parameter("/app/kanban/agentcore/username")
    # Obtém o token
    token_response = get_token(user_pool_id, client_id, client_secret, region, username)
    
    if "error" in token_response:
        raise Exception(f"Erro ao obter token: {token_response['error']}")
    
    return token_response["access_token"]

def get_ssm_parameter(name: str, with_decryption: bool = True) -> str:
    ssm = boto3.client("ssm")

    response = ssm.get_parameter(Name=name, WithDecryption=with_decryption)

    return response["Parameter"]["Value"]


def put_ssm_parameter(
    name: str, value: str, parameter_type: str = "String", with_encryption: bool = False
) -> None:
    ssm = boto3.client("ssm")

    put_params = {
        "Name": name,
        "Value": value,
        "Type": parameter_type,
        "Overwrite": True,
    }

    if with_encryption:
        put_params["Type"] = "SecureString"

    ssm.put_parameter(**put_params)

print(get_cognito_token())