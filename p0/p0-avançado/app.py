import json
import logging
import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

# Configuração de logs simples e seguros (apenas metadados operacionais)
logging.basicConfig(
    filename="execucao.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)


class ErroAplicacao(Exception):
    """Exceção base para erros controlados e compreensíveis da aplicação."""
    pass


# 1. Carregamento da configuração (credencial + parâmetros externos do LLM)
def carregar_configuracao(caminho_config: str = "config.json") -> tuple[genai.Client, dict]:
    """Carrega o .env e o config.json, valida credenciais e inicializa o cliente."""
    logging.info("Iniciando carregamento de configurações.")
    load_dotenv(override=True)
    chave_api = os.getenv("API_KEY")

    if chave_api is None:
        logging.warning("Falha de configuração: variável API_KEY ausente.")
        raise ErroAplicacao(
            "Configuração ausente: a variável 'API_KEY' não foi encontrada. "
            "Crie um arquivo '.env' na raiz do projeto usando o '.env.example' como modelo."
        )

    chave_limpa = chave_api.strip()
    if not chave_limpa or chave_limpa == "sua_chave_aqui":
        logging.warning("Falha de configuração: credencial API_KEY vazia ou padrão.")
        raise ErroAplicacao(
            "Credencial ausente: a variável 'API_KEY' está vazia ou com o valor de exemplo. "
            "Preencha sua chave real no arquivo '.env'."
        )

    try:
        with open(caminho_config, "r", encoding="utf-8") as arquivo:
            config_llm = json.load(arquivo)
    except FileNotFoundError:
        logging.error("Arquivo de configuração '%s' não encontrado.", caminho_config)
        raise ErroAplicacao(
            f"Configuração ausente: o arquivo '{caminho_config}' não foi encontrado."
        )
    except json.JSONDecodeError:
        logging.error("Arquivo de configuração '%s' com JSON inválido.", caminho_config)
        raise ErroAplicacao(
            f"Configuração inválida: o arquivo '{caminho_config}' não contém um JSON válido."
        )

    campos_obrigatorios = ("modelo", "temperatura", "max_output_tokens", "timeout_ms", "instrucao_sistema")
    for campo in campos_obrigatorios:
        if campo not in config_llm:
            logging.error("Campo obrigatório '%s' ausente em '%s'.", campo, caminho_config)
            raise ErroAplicacao(
                f"Configuração inválida: o campo '{campo}' está ausente em '{caminho_config}'."
            )

    try:
        cliente = genai.Client(
            api_key=chave_limpa,
            http_options=types.HttpOptions(
                api_version="v1beta",
                timeout=int(config_llm["timeout_ms"]),
            ),
        )
        logging.info(
            "Configuração carregada com sucesso (modelo=%s, max_tokens=%s, temperatura=%s).",
            config_llm["modelo"],
            config_llm["max_output_tokens"],
            config_llm["temperatura"],
        )
        return cliente, config_llm
    except Exception:
        logging.error("Erro inesperado ao instanciar o cliente do LLM.")
        raise ErroAplicacao(
            "Configuração inválida: não foi possível inicializar o cliente do serviço de LLM."
        )


# 2. Captura e validação da entrada
def validar_entrada(texto: str) -> str:
    """Valida se o texto fornecido não é vazio."""
    if not texto or not texto.strip():
        logging.warning("Entrada rejeitada: texto vazio ou apenas espaços.")
        raise ErroAplicacao(
            "Entrada inválida: o texto não pode ser vazio. "
            "Execute novamente e informe uma mensagem válida."
        )
    texto_limpo = texto.strip()
    logging.info("Entrada validada com sucesso (tamanho=%d caracteres).", len(texto_limpo))
    return texto_limpo


def capturar_entrada() -> str:
    """Lê a entrada pelo terminal."""
    try:
        texto = input("Digite o texto que deseja analisar: ")
    except (KeyboardInterrupt, EOFError):
        logging.info("Execução interrompida pelo usuário durante a leitura da entrada.")
        raise ErroAplicacao("Execução interrompida pelo usuário.")

    return validar_entrada(texto)


# 3. Preparação da solicitação
def preparar_solicitacao(texto_usuario: str) -> str:
    """Estrutura o prompt a partir da entrada validada do usuário."""
    logging.info("Preparando solicitação textual para o modelo.")
    return f"Texto para análise:\n\"{texto_usuario}\""


# 4. Chamada ao modelo
def chamar_modelo(cliente: genai.Client, prompt: str, config_llm: dict):
    """Envia a solicitação ao LLM usando os parâmetros externos e traduz falhas."""
    modelo = config_llm["modelo"]
    logging.info("Enviando requisição ao modelo '%s'.", modelo)

    geracao_config = types.GenerateContentConfig(
        system_instruction=config_llm["instrucao_sistema"],
        temperature=float(config_llm["temperatura"]),
        max_output_tokens=int(config_llm["max_output_tokens"]),
    )

    try:
        return cliente.models.generate_content(
            model=modelo,
            contents=prompt,
            config=geracao_config,
        )
    except errors.APIError as e:
        logging.error("Erro da API do LLM (código HTTP=%s).", e.code)
        detalhe = str(e).lower()
        if e.code in (401, 403) or (e.code == 400 and "api key" in detalhe):
            raise ErroAplicacao(
                "Credencial inválida: a chave de API informada foi recusada pelo Google Gemini. "
                "Verifique se o valor em 'API_KEY' no arquivo '.env' está correto."
            )
        if e.code == 404:
            raise ErroAplicacao(
                f"Configuração inválida: o modelo '{modelo}' não foi encontrado ou não está habilitado."
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
        logging.error("Timeout na comunicação com o LLM.")
        raise ErroAplicacao(
            "Timeout: o serviço de LLM excedeu o tempo limite configurado para resposta."
        )
    except ConnectionError:
        logging.error("Falha de conexão de rede ao acessar o LLM.")
        raise ErroAplicacao(
            "Falha de comunicação: não foi possível conectar ao servidor. Verifique sua conexão com a internet."
        )
    except Exception as e:
        logging.error("Exceção não prevista na chamada ao modelo (%s).", type(e).__name__)
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
    """Valida se a resposta recebida contém texto útil e no formato esperado."""
    if resposta is None:
        logging.error("Resposta nula recebida do serviço de LLM.")
        raise ErroAplicacao("Resposta inesperada: o serviço não retornou dados.")

    texto_saida = getattr(resposta, "text", None)
    if not texto_saida or not isinstance(texto_saida, str) or not texto_saida.strip():
        logging.warning("Resposta vazia ou em formato inesperado recebida do LLM.")
        raise ErroAplicacao(
            "Resposta vazia ou em formato inesperado: o modelo não gerou texto válido."
        )

    resultado_limpo = texto_saida.strip()
    logging.info("Resposta tratada com sucesso (tamanho=%d caracteres).", len(resultado_limpo))
    return resultado_limpo


# 6. Apresentação do resultado
def apresentar_resultado(resultado: str) -> None:
    """Exibe o resultado final formatado no terminal."""
    print("\n=== RESULTADO DA ANÁLISE ===")
    print(resultado)
    print("============================\n")


def main() -> None:
    """Orquestra o fluxo completo com tratamento centralizado de erros."""
    logging.info("=== Nova execução iniciada ===")
    try:
        cliente, config_llm = carregar_configuracao()
        texto_usuario = capturar_entrada()
        prompt = preparar_solicitacao(texto_usuario)

        print("\nProcessando solicitação com o LLM...\n")
        resposta_bruta = chamar_modelo(cliente, prompt, config_llm)
        resultado_final = tratar_resposta(resposta_bruta)
        apresentar_resultado(resultado_final)
        logging.info("=== Execução concluída com sucesso ===")

    except ErroAplicacao as erro:
        logging.warning("Execução encerrada por erro controlado: %s", erro)
        print(f"\n[AVISO] {erro}\n", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        logging.critical("Falha crítica inesperada: %s", type(exc).__name__)
        print(
            "\n[ERRO] Ocorreu uma falha inesperada na aplicação.\n",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()