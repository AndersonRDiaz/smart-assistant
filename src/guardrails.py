import re

class GuardrailSystem:
    def __init__(self):
        # 5 padrões de ataque (Prompt Injection) exigidos [cite: 145]
        self.padroes_bloqueados = [
            r"(?i)ignore\s+(all\s+)?instructions",
            r"(?i)forget\s+(all\s+)?rules",
            r"(?i)jailbreak",
            r"(?i)dan\s+mode",
            r"(?i)reveal\s+(your\s+)?prompt"
        ]
        self.caracteres_proibidos = ["<", ">", "{", "}"] # [cite: 144]

    def validar_input(self, texto: str) -> tuple[bool, str]:
        # Verifica tamanho (máx 500 chars) [cite: 144]
        if len(texto) > 500:
            return False, "Input bloqueado: Excede o limite de 500 caracteres."

        # Verifica caracteres proibidos [cite: 144]
        for char in self.caracteres_proibidos:
            if char in texto:
                return False, f"Input bloqueado: Caracter proibido encontrado ({char})."

        # Verifica ataques usando RegEx [cite: 145]
        for padrao in self.padroes_bloqueados:
            if re.search(padrao, texto):
                return False, "Input bloqueado: Tentativa de Prompt Injection."

        return True, "Input seguro."

    def validar_output(self, resposta: str) -> tuple[bool, str]:
        # Verifica se o modelo não vazou o próprio system prompt [cite: 154]
        termos_internos = ["Você é", "regras", "system prompt", "instruções"]
        for termo in termos_internos:
            if termo in resposta:
                return False, "Output bloqueado: Vazamento de dados internos."

        return True, "Output seguro."