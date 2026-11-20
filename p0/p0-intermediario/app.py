import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types


class ErroAplicacao(Exception):
    pass


# 1. Carregamento da configuração
def carregar_configuracao() -> genai.Client:
    load_dotenv(override=True)
    chave_api = os.getenv("API_KEY")

    if chave_api is None:
        raise ErroAplicacao(
            "Configuração ausente: a variável 'API_KEY' não foi encontrada. "
            "Crie um arquivo '.env' na raiz do projeto usando o '.env.example' como modelo."
        )

    chave_limpa = chave_api.strip()
    if not chave_limpa or chave_limpa == "sua_chave_aqui":
        raise ErroAplicacao(
            "Credencial ausente: a variável 'API_KEY' está vazia ou com o valor de exemplo. "
            "Preencha sua chave real no arquivo '.env'."
        )

    try:
        # Configura a API v1beta e define timeout de 15 segundos (15000 ms)
        cliente = genai.Client(
            api_key=chave_limpa,
            http_options=types.HttpOptions(api_version="v1beta", timeout=15000),
        )
        return cliente
    except Exception:
        raise ErroAplicacao(
            "Configuração inválida: não foi possível inicializar o cliente do serviço de LLM."
        )


# 2. Captura da entrada
def capturar_entrada() -> str:
    try:
        texto = input("Digite o texto que deseja analisar: ")
    except (KeyboardInterrupt, EOFError):
        raise ErroAplicacao("Execução interrompida pelo usuário.")

    if not texto or not texto.strip():
        raise ErroAplicacao(
            "Entrada inválida: o texto não pode ser vazio. "
            "Execute novamente e informe uma mensagem válida."
        )

    return texto.strip()


# 3. Preparação da solicitação
def preparar_solicitacao(texto_usuario: str) -> str:
    return (
        "Analise o seguinte texto curto e extraia as informações principais "
        "(tipo de texto, intenção e dados relevantes) de forma clara e objetiva:\n\n"
        f"Texto: \"{texto_usuario}\""
    )


# 4. Chamada ao modelo
def chamar_modelo(cliente: genai.Client, prompt: str):
    try:
        return cliente.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
        )
    except errors.APIError as e:
        detalhe = str(e).lower()
        if e.code in (401, 403) or (e.code == 400 and "api key" in detalhe):
            raise ErroAplicacao(
                "Credencial inválida: a chave de API informada foi recusada pelo Google Gemini. "
                "Verifique se o valor em 'API_KEY' no arquivo '.env' está correto."
            )
        if e.code == 404:
            raise ErroAplicacao(
                "Configuração inválida: o modelo 'gemini-3.5-flash' não foi encontrado ou não está habilitado."
            )
        if e.code == 429:
            raise ErroAplicacao(
                "Indisponibilidade temporária: limite de requisições (cota) atingido. Aguarde e tente novamente."
            )
        if e.code in (500, 502, 503, 504):
            raise ErroAplicacao(
                "Indisponibilidade do LLM: o servidor do modelo está sobrecarregado no momento. Tente mais tarde."
            )
        raise ErroAplicacao(
            f"Erro de comunicação com o serviço de LLM (código {e.code}). Tente novamente mais tarde."
        )
    except TimeoutError:
        raise ErroAplicacao(
            "Timeout: o serviço de LLM demorou mais de 15 segundos para responder."
        )
    except ConnectionError:
        raise ErroAplicacao(
            "Falha de comunicação: não foi possível conectar ao servidor. Verifique sua conexão com a internet."
        )
    except Exception as e:
        detalhe = str(e).lower()
        if "timeout" in detalhe or "timed out" in detalhe:
            raise ErroAplicacao(
                "Timeout: o tempo limite de espera pela resposta do LLM foi excedido."
            )
        if "connect" in detalhe or "network" in detalhe or "getaddrinfo" in detalhe:
            raise ErroAplicacao(
                "Falha de comunicação: erro de rede ao acessar a API. Verifique sua internet."
            )
        raise ErroAplicacao(
            "Falha inesperada durante a chamada ao modelo. Tente novamente."
        )


# 5. Tratamento da resposta
def tratar_resposta(resposta) -> str:
    if resposta is None:
        raise ErroAplicacao(
            "Resposta inesperada: o serviço não retornou dados."
        )

    texto_saida = getattr(resposta, "text", None)
    if not texto_saida or not isinstance(texto_saida, str) or not texto_saida.strip():
        raise ErroAplicacao(
            "Resposta vazia ou em formato inesperado: o modelo não gerou texto válido."
        )

    return texto_saida.strip()


# 6. Apresentação do resultado
def apresentar_resultado(resultado: str) -> None:
    print("\n=== RESULTADO DA ANÁLISE ===")
    print(resultado)
    print("============================\n")


def main() -> None:
    try:
        cliente = carregar_configuracao()
        texto_usuario = capturar_entrada()
        prompt = preparar_solicitacao(texto_usuario)

        print("\nProcessando solicitação com o LLM...\n")
        resposta_bruta = chamar_modelo(cliente, prompt)
        resultado_final = tratar_resposta(resposta_bruta)
        apresentar_resultado(resultado_final)

    except ErroAplicacao as erro:
        print(f"\n[AVISO] {erro}\n", file=sys.stderr)
        sys.exit(1)
    except Exception:
        print(
            "\n[ERRO] Ocorreu uma falha inesperada na aplicação.\n",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()