import json
import os
import re
from schemas import ClassificacaoSchema, ProcessamentoSchema, RespostaSchema
from prompts import PromptManager  # Requisito da Aula 11

class AssistantChain:
    def __init__(self, llm_client):
        self.llm = llm_client
        self.prompt_manager = PromptManager()
        self.system_prompt = self.prompt_manager.get_system_prompt()

    def _extrair_json(self, texto: str) -> str:
        inicio = texto.find('{')
        fim = texto.rfind('}')
        if inicio != -1 and fim != -1:
            return texto[inicio:fim+1]
        return "{}"

    def etapa1_classificar(self, texto: str) -> ClassificacaoSchema:
        prompt = self.prompt_manager.get_classificacao_prompt(texto)
        resposta_llm = self.llm.gerar_resposta(prompt, self.system_prompt)
        json_limpo = self._extrair_json(resposta_llm)
        
        try:
            return ClassificacaoSchema.model_validate_json(json_limpo)
        except Exception as e:
            print(f"\n[FALHA ETAPA 1] JSON inválido recebido da IA: {json_limpo}")
            return ClassificacaoSchema(tipo="duvida", urgencia="baixa", tema="erro de leitura")

    def etapa2_processar(self, classificacao: ClassificacaoSchema, texto_original: str) -> ProcessamentoSchema:
        
        # --- CRITÉRIO ESSENCIAL DA AULA 09: LÓGICA CONDICIONAL VISÍVEL ---
        if classificacao.tipo == "reclamacao":
            instrucao = "Atenção: O usuário fez uma RECLAMAÇÃO. Extraia qual é o problema relatado."
        elif classificacao.tipo == "duvida":
            instrucao = "Atenção: O usuário tem uma DÚVIDA. Foque em extrair a pergunta principal."
        elif classificacao.tipo == "elogio":
            instrucao = "Atenção: O usuário fez um ELOGIO. Extraia qual foi o ponto positivo."
        elif classificacao.tipo == "sugestao":
            instrucao = "Atenção: O usuário fez uma SUGESTÃO. Extraia a ideia central."
        else:
            instrucao = "Analise o pedido do usuário."

        # Passamos a instrução escolhida para o gerenciador (Aula 11)
        prompt = self.prompt_manager.get_processamento_prompt(instrucao, texto_original)
        
        resposta_llm = self.llm.gerar_resposta(prompt, self.system_prompt)
        json_limpo = self._extrair_json(resposta_llm)
        
        try:
            return ProcessamentoSchema.model_validate_json(json_limpo)
        except Exception as e:
            print(f"\n[FALHA ETAPA 2] JSON inválido recebido da IA: {json_limpo}")
            return ProcessamentoSchema(dados_extraidos={}, analise="Falha no processamento", sentimento="neutro")

    def etapa3_responder(self, processamento: ProcessamentoSchema) -> RespostaSchema:
        prompt = self.prompt_manager.get_resposta_prompt(processamento.analise)
        resposta_llm = self.llm.gerar_resposta(prompt, self.system_prompt)
        json_limpo = self._extrair_json(resposta_llm)
        
        try:
            return RespostaSchema.model_validate_json(json_limpo)
        except Exception as e:
            print(f"\n[FALHA ETAPA 3] JSON inválido recebido da IA: {json_limpo}")
            return RespostaSchema(resposta="Desculpe, ocorreu um erro interno de processamento.", confianca="baixa", acao_sugerida="encaminhar_humano")