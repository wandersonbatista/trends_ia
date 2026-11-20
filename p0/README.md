# Analisador e Extrator de Textos Curtos com LLM (P0)

Aplicação em Python que utiliza a interface programática do **Google Gemini** para analisar mensagens curtas e extrair informações principais (tipo de texto, intenção e dados relevantes) de forma estruturada.

## Ambiente e Tecnologias
* **Linguagem:** Python 3.12+ (testado localmente com Python 3.12)
* **Principais Bibliotecas:**
  * `google-genai==3.0.0` (SDK oficial do Google Gemini)
  * `python-dotenv==1.2.4` (gerenciamento de variáveis de ambiente)
  * `unittest` (biblioteca padrão do Python para testes automatizados locais)

## Estrutura do Projeto
* `app.py`: fluxo principal dividido em carregamento de configuração, captura/validação de entrada, preparação de prompt, chamada ao modelo, tratamento de resposta e exibição.
* `config.json`: parâmetros externos do LLM (`modelo`, `temperatura`, `max_output_tokens`, `timeout_ms` e `instrucao_sistema`), editáveis sem alterar o código-fonte.
* `test_app.py`: suíte de testes unitários da lógica local (sem consumo da API).
* `.env.example`: modelo das variáveis de ambiente necessárias.
* `requirements.txt`: dependências exatas do projeto.

## Instalação e Configuração

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/wandersonbatista/trends_ia

   cd trends_ia/p0
   ```
2. **Crie e ative um ambiente virtual:**
    ```bash
        Windows: python -m venv venv e venv\Scripts\activate

        Linux/macOS: python3 -m venv venv e source venv/bin/activate
    ```
3. Instale as dependências:
    
    ```bash

    pip install -r requirements.txt
    ```
4. Configure a credencial de acesso:
    
    * Renopeie .env.example para .env:
    * Insira sua chave gerada no Google AI Studio no arquivo .env:
        ```
        API_KEY=sua_chave_aqui
        ```
    * Personalização do LLM (Opcional):
        ```
        Edite config.json para ajustar o limite de tokens (max_output_tokens), criatividade (temperatura), timeout_ms ou a instrucao_sistema sem modificar app.py.
        ```

## Execução e Exemplos

1. Rodar a aplicação:
    ```Bash
    python app.py
    ```

* Exemplo de Entrada:
    ``` 
        Digite o texto que deseja analisar: Agendar dentista sexta-feira às 10h na clínica central.
    ```
* Exemplo de Saída:
    ```
    === RESULTADO DA ANÁLISE ===
    - Tipo de texto: Solicitação de agendamento.
    - Intenção: Registrar um compromisso futuro.
    - Dados relevantes:
    - Evento: Consulta ao dentista
    - Data: Sexta-feira
    - Horário: 10h
    - Local: Clínica central
    ============================
    ```
## Logs e Privacidade

A aplicação gera registros técnicos no arquivo execucao.log (ignorado pelo Git) contendo apenas data/hora, nível do evento, parâmetros técnicos utilizados e tamanho em caracteres das mensagens. Nenhuma chave de API, token, dado pessoal ou texto digitado pelo usuário é armazenado nos logs.
1. Testes Automatizados e Reais

    Testes Locais Automatizados (sem chamada real ao LLM):
    Execute:
    Bash

    python -m unittest -v

    Cobre validação de entrada vazia/válida, montagem do prompt, falha por credencial ausente, tratamento de resposta simulada (válida e vazia) e simulação de erros de timeout e autenticação (403).

    Testes Reais de Integração:
    Validados diretamente contra a API do Gemini (gemini-3.5-flash), cobrindo envio de mensagens reais, rejeição de credencial inválida (API_KEY incorreta) e tratamento de indisponibilidade temporária do serviço (503 UNAVAILABLE).

## Validação em Ambiente Limpo

O projeto foi clonado em um diretório separado e executado em um ambiente virtual novo (venv_limpo) seguindo exclusivamente as etapas deste README.md. Todos os testes unitários e a chamada real ao modelo funcionaram conforme esperado.
## Decisões Técnicas e Uso de IA

* Modelo e Parâmetros: Escolhido gemini-3.5-flash pela baixa latência e estabilidade. A temperatura baixa (0.2) prioriza respostas objetivas e consistentes.

* Declaração de Uso de IA: Ferramentas de IA generativa foram utilizadas como apoio técnico para depurar erros de versão do SDK (google-genai), estruturar o tratamento de exceções, elaborar os testes unitários com unittest.mock e revisar a documentação.

