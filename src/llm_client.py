import os
from ollama import Client
from dotenv import load_dotenv

class LLMClient:
    def __init__(self, model_name="gpt-oss:120b"):
        self.model_name = model_name

        # Carrega as variáveis do .env localizado na raiz do projeto
        caminho_env = os.path.join(os.path.dirname(__file__), '..', '.env')
        load_dotenv(caminho_env)

        api_key = os.getenv('OLLAMA_API_KEY', '')

        # Configuração Ollama Cloud 
        self.client = Client(
            host="https://ollama.com",
            headers={'Authorization': 'Bearer ' + api_key}
        )

    def gerar_resposta(self, prompt: str, system_prompt: str = "") -> str:
        try:
            response = self.client.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                options={"temperature": 0.3},
                format="json", # Mantemos forçado para não quebrar o Pydantic
                stream=False
            )
            return response['message']['content'].strip()
        except Exception as e:
            print(f"\n Erro de conexão com a nuvem: {e}")
            return "{}"