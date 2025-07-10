import requests
import base64

# --- SUAS CREDENCIAIS DE TESTE ---
client_id = "app6647123671"
client_secret = "50BAB33B0D1330F77454BF85C40A1E3E"
# -----------------------------------------

url = "https://sandbox.api.pagseguro.com/oauth2/token"

# Criando a autorização 'Basic'
auth_string = f"{client_id}:{client_secret}"
auth_bytes = auth_string.encode('ascii')
base64_bytes = base64.b64encode(auth_bytes)
base64_auth_string = base64_bytes.decode('ascii')

# Headers, agora sem o content-type, pois a biblioteca requests fará isso por nós
headers = {
    "accept": "application/json",
    "Authorization": f"Basic {base64_auth_string}"
}

# --- A GRANDE MUDANÇA: O PAYLOAD AGORA É UM DICIONÁRIO PYTHON ---
payload = {
    "grant_type": "client_credentials",
    "scope": "write:orders read:orders"
}

try:
    print("--- Buscando o Access Token no Sandbox (Falando JSON)... ---")
    
    # --- A MUDANÇA NA CHAMADA: Usamos o parâmetro 'json' em vez de 'data' ---
    response = requests.post(url, json=payload, headers=headers)
    
    response.raise_for_status()

    resposta_json = response.json()
    access_token = resposta_json.get("access_token")

    if access_token:
        print("\n🎉 TOKEN DE TESTE OBTIDO COM SUCESSO! 🎉\n")
        print("Seu Bearer Token de Sandbox é:\n")
        print(access_token)
        print("\nGuarde este token! É ele que vamos usar para os testes.")
    else:
        print("\n!!! Erro: Access Token não encontrado na resposta. !!!")
        print("Resposta recebida:", response.text)

except requests.exceptions.RequestException as e:
    print(f"\n!!! Erro ao fazer a requisição: {e} !!!")
    if e.response is not None:
        print("Resposta do servidor:", e.response.text)