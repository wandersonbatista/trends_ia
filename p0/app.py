import os
from dotenv import load_dotenv
from google import genai

# Carrega as variáveis de ambiente
load_dotenv()
CHAVE_API = os.getenv("API_KEY")

# Inicializa o cliente com a versão v1beta da API para garantir acesso aos modelos mais recentes
cliente = genai.Client(api_key=CHAVE_API, http_options={'api_version': 'v1beta'})

def processar_texto(entrada_usuario):
    prompt = f"Analise o seguinte texto e extraia os dados principais de forma clara: {entrada_usuario}"
    
    try:
        # ATENÇÃO: Verifique se a string abaixo é a mesma exigida pela sua conta
        resposta = cliente.models.generate_content(
            model='gemini-3.5-flash', 
            contents=prompt
        )
        return resposta.text
    except Exception as e:
        return f"ERRO: Falha na comunicação com a API. Detalhes: {e}"

if __name__ == "__main__":
    texto_usuario = input("Digite o texto que deseja processar: ")
    
    if texto_usuario.strip():
        print("\nProcessando com o LLM (isso deve levar apenas alguns segundos)...\n")
        resultado = processar_texto(texto_usuario)
        print("=== RESULTADO ===")
        print(resultado)
    else:
        print("Entrada vazia. Tente novamente.")