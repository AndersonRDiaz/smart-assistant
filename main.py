import sys
import os

# Adiciona a pasta src ao caminho do sistema para podermos importar os módulos
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from guardrails import GuardrailSystem
from chain import AssistantChain
from llm_client import LLMClient

def interagir():
    print("=== Smart Assistant Iniciado ===")
    print("Digite 'sair' para encerrar.\n")

    # Inicializa os módulos
    llm = LLMClient()
    guardrails = GuardrailSystem()
    chain = AssistantChain(llm)

    while True:
        usuario_input = input("Você: ")
        if usuario_input.lower() == 'sair':
            print("Encerrando assistente...")
            break

        # Input Guard (Segurança inicial)
        is_safe, motivo = guardrails.validar_input(usuario_input)
        if not is_safe:
            print(f"Assistente (Bloqueado): {motivo}\n")
            continue

        try:
            # Pipeline Multi-etapa (Chain)
            classificacao = chain.etapa1_classificar(usuario_input)
            processamento = chain.etapa2_processar(classificacao, usuario_input)
            resposta_final = chain.etapa3_responder(processamento)

            # Output Guard (Segurança final)
            is_safe_out, motivo_out = guardrails.validar_output(resposta_final.resposta)
            if not is_safe_out:
                print(f"Assistente (Bloqueado interno): {motivo_out}\n")
                continue

            # Exibe a resposta final validada
            print(f"Assistente: {resposta_final.resposta}")
            print(f"  [Info: Tipo={classificacao.tipo} | Confiança={resposta_final.confianca} | Ação={resposta_final.acao_sugerida}]\n")

        except Exception as e:
            print(f"Erro no processamento: {e}\n")

if __name__ == "__main__":
    interagir()