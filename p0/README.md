# Processador de Texto com LLM (Projeto P0)

Uma aplicação em Python que utiliza a interface programática do Google Gemini para interpretar textos curtos e extrair ou analisar suas informações principais.

## O Problema
Pessoas lidam diariamente com mensagens desestruturadas e precisam extrair o contexto ou dados importantes rapidamente. Este projeto resolve o problema de **analisar e extrair informações de um texto curto** utilizando um Modelo de Linguagem, convertendo uma entrada textual livre em uma análise categorizada.

## Pré-requisitos
* Python 3.8+ instalado.
* Uma chave de API do Google Gemini (Google AI Studio).

## Como Instalar e Configurar

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/wandersonbatista/trends_ia.git
2. **Crie e ative o ambiente virtual:**
    ```bash
        - Windows: python -m venv venv e depois venv\Scripts\activate

        - Mac/Linux: python3 -m venv venv e depois source venv/bin/activate
3. **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
4. **Configure a chave de API:**
    - Renomeie o arquivo ".env.example" para ".env".

    - Abra o .env e insira sua chave do Google Gemini:
    ```bash
        API_KEY=sua_chave_aqui

## Como Executar:
- Com o ambiente ativado, rode o script principal:
```bash
    python app.py
```
O terminal solicitará que você digite um texto. Após pressionar Enter, a aplicação enviará a entrada ao LLM e retornará a análise.