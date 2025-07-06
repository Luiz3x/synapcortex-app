import requests
import base64

# --- COLOQUE SUAS CREDENCIAIS AQUI ---
client_id = "SEU_CLIENT_ID"
client_secret = "SEU_CLIENT_SECRET"
# -----------------------------------------

# URL para obter o token no ambiente de teste
url = "https://sandbox.api.pagseguro.com/oauth2/token"

# O cabeçalho de autorização é 'Basic' e uma combinação do seu client_id e secret
# O código abaixo cria isso para você automaticamente
auth_string = f"{client_id}:{client_secret}"
auth_bytes = auth_string.encode('ascii')
base64_bytes = base64.b64encode(auth_bytes)
base64_auth_string = base64_bytes.decode('ascii')

headers = {
    "accept": "application/json",
    "Authorization": f"Basic {base64_auth_string}",
    "content-type": "application/x-www-form-urlencoded"
}

# O corpo da requisição para este tipo de autenticação
payload = "grant_type=client_credentials&scope=write:orders read:orders"

try:
    print("--- Buscando o Access Token... ---")
    response = requests.post(url, data=payload, headers=headers)
    response.raise_for_status()  # Isso vai gerar um erro se a resposta for 4xx ou 5xx

    resposta_json = response.json()
    access_token = resposta_json.get("access_token")

    if access_token:
        print("\n🎉 TOKEN OBTIDO COM SUCESSO! 🎉\n")
        print("Seu Bearer Token é:\n")
        print(access_token)
        print("\nGuarde este token com segurança! É ele que vamos usar no nosso app.")
    else:
        print("\n!!! Erro: Access Token não encontrado na resposta. !!!")
        print("Resposta recebida:", response.text)

except requests.exceptions.RequestException as e:
    print(f"\n!!! Erro ao fazer a requisição: {e} !!!")
    if e.response is not None:
        print("Resposta do servidor:", e.response.text)