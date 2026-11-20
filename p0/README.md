# Analisador e Extrator de Textos Curtos com LLM (P0)

Aplicação de linha de comando em Python que utiliza a interface programática do **Google Gemini** (`gemini-3.5-flash`) para analisar mensagens curtas e extrair suas informações principais de forma estruturada.

## Arquitetura do Código (`app.py`)
O fluxo foi dividido em seis funções com responsabilidades isoladas:
1. `carregar_configuracao()`: lê o `.env`, valida a existência da chave e instancia o cliente com timeout de 15s.
2. `capturar_entrada()`: coleta o texto no terminal e bloqueia entradas vazias.
3. `preparar_solicitacao()`: monta o prompt estruturado de extração.
4. `chamar_modelo()`: realiza a chamada ao LLM e traduz exceções de API, autenticação, rede e timeout.
5. `tratar_resposta()`: verifica se a resposta não está vazia ou malformada.
6. `apresentar_resultado()`: exibe a saída formatada ao usuário.

## Instalação e Configuração

1. **Clone o repositório e acesse a pasta:**
   ```bash
   git clone https://github.com/wandersonbatista/trends_ia
   cd trends_ia/p0
2. Crie e ative o ambiente virtual:

        Windows: python -m venv venv e venv\Scripts\activate

        Linux/macOS: python3 -m venv venv e source venv/bin/activate

3. Instale as dependências:
    
    ```Bash

    pip install -r requirements.txt

4. Configure a credencial de acesso:

        renomeie o arquivo .env.example para .env.

        Obtenha uma chave no Google AI Studio e preencha no .env:         API_KEY=sua_chave_aqui

## Execução e Exemplos

1. Execute o programa com:
    ```

    python app.py
    ```
2. Exemplo de Entrada:
    ```
    Digite o texto que deseja analisar: Agendar dentista sexta-feira às 10h na clínica central.
    ```
3. Exemplo de Saída:
    ```
    === RESULTADO DA ANÁLISE ===
    - Tipo de texto: Lembrete / Solicitação de agendamento.
    - Intenção: Registrar um compromisso futuro.
    - Dados relevantes:
      - Evento: Consulta ao dentista
      - Data/Dia: Sexta-feira
      - Horário: 10h
      - Local: Clínica central
    ============================
    ```
## Testes Realizados (Reais vs. Simulados)

1. Testes Reais (integração direta com a API do Gemini):

    ```
        -   Fluxo normal: envio de textos válidos retornando a análise estruturada.

        Entrada vazia: bloqueio imediato no terminal antes de consumir a API.

        -   Credencial ausente (API_KEY vazia): encerramento controlado com aviso de configuração.

        -   Credencial inválida (API_KEY incorreta): captura do erro HTTP 400/403 da API com mensagem amigável, sem expor chaves.

        -   Indisponibilidade do serviço: validação do tratamento para erro real 503 UNAVAILABLE (sobrecarga temporária do servidor).
    ```
2. Testes Simulados (ambiente local):

        -   Falha de comunicação e Timeout: simulados pela desconexão da rede local e redução do parâmetro timeout na configuração do cliente HTTP, confirmando o encerramento seguro sem rastros técnicos brutos.