from pydantic import BaseModel, Field
from typing import Optional

class ClassificacaoSchema(BaseModel):
    tipo: str = Field(description="reclamacao|duvida|elogio|sugestao")
    urgencia: str = Field(description="alta|media|baixa")
    tema: str

class ProcessamentoSchema(BaseModel):
    dados_extraidos: dict
    analise: str
    sentimento: Optional[str] = None

class RespostaSchema(BaseModel):
    resposta: str
    confianca: str = Field(description="alta|media|baixa")
    acao_sugerida: str