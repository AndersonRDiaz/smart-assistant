import os

class PromptManager:
    def __init__(self):
        # Localiza o arquivo de system prompt defensivo (Aula 10)
        self.caminho_system_prompt = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'system_prompt.txt')

    def get_system_prompt(self) -> str:
        try:
            with open(self.caminho_system_prompt, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return "Você é um assistente útil e responde apenas em JSON."

    # --- TEMPLATE PATTERN (AULA 11) ---
    
    def get_classificacao_prompt(self, texto_usuario: str) -> str:
        template = """
        Classifique a solicitação do usuário. Responda APENAS com um JSON válido e estruturado.
        Opções obrigatórias para 'tipo': reclamacao, duvida, elogio, sugestao.
        Opções obrigatórias para 'urgencia': alta, media, baixa.
        
        REGRA VITAL: Se a mensagem do usuário for FORA DO ESCOPO da loja (ex: capitais, receitas, política), obrigatoriamente classifique como:
        {{"tipo": "duvida", "urgencia": "baixa", "tema": "fora do escopo"}}
        
        EXEMPLO PERFEITO DE SAÍDA:
        {{"tipo": "reclamacao", "urgencia": "alta", "tema": "atraso na entrega"}}
        
        [MENSAGEM_DO_USUARIO]
        "{texto}"
        """
        return template.format(texto=texto_usuario)

    def get_processamento_prompt(self, instrucao: str, texto_original: str) -> str:
        template = """
        Analise a solicitação. Responda APENAS com um JSON válido.
        
        [INSTRUCAO_ESPECIFICA_POR_TIPO]
        {instrucao}
        
        Se o tema for "fora do escopo", analise como "assunto não relacionado à loja".
        
        EXEMPLO PERFEITO DE SAÍDA:
        {{"dados_extraidos": {{"foco": "detalhe principal"}}, "analise": "descrição da análise", "sentimento": "negativo/positivo/neutro"}}
        
        [MENSAGEM_ORIGINAL]
        "{texto}"
        """
        return template.format(instrucao=instrucao, texto=texto_original)

    def get_resposta_prompt(self, analise_previa: str) -> str:
        template = """
        Gere uma resposta educada para o usuário. Responda APENAS com um JSON válido.
        Opções obrigatórias para 'confianca': alta, media, baixa.
        
        REGRA VITAL: O campo 'acao_sugerida' DEVE ser um texto. NUNCA use null.
        Se a análise indicar "assunto não relacionado à loja", recuse educadamente informando que só pode ajudar com produtos da TechStore e defina acao_sugerida como "recusar_atendimento".
        
        EXEMPLO PERFEITO DE SAÍDA:
        {{"resposta": "Sinto muito pelo problema. Vamos resolver.", "confianca": "alta", "acao_sugerida": "reembolso"}}
        
        [ANALISE_DO_SISTEMA]
        {analise}
        """
        return template.format(analise=analise_previa)