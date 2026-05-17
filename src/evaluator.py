import json
import os
import csv
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from llm_client import LLMClient
from chain import AssistantChain
from guardrails import GuardrailSystem

def carregar_dados(caminho):
    with open(caminho, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    print("=== Iniciando Avaliação Automática ===")
    
    # 1. Configuração do Sistema
    load_dotenv()
    api_key = os.getenv("OLLAMA_API_KEY")
    if not api_key:
        print("❌ Erro: API Key não encontrada no arquivo .env!")
        return

    llm = LLMClient()
    chain = AssistantChain(llm)
    guardrails = GuardrailSystem()

    # 2. Carregamento dos Datasets
    base_dir = os.path.dirname(os.path.dirname(__file__))
    test_path = os.path.join(base_dir, 'data', 'test_dataset.json')
    attack_path = os.path.join(base_dir, 'data', 'attack_dataset.json')

    try:
        test_data = carregar_dados(test_path)
        attack_data = carregar_dados(attack_path)
    except Exception as e:
        print(f"❌ Erro ao carregar os arquivos JSON: {e}")
        return

    # 3. Variáveis de Métricas
    acertos_classificacao = 0
    json_valido_count = 0
    bloqueios_corretos = 0
    falsos_positivos = 0

    total_testes = len(test_data)
    total_ataques = len(attack_data)

    print(f"\n[1/5] Avaliando {total_testes} Solicitações Legítimas...")
    for item in test_data:
        texto = item["texto"]
        tipo_esperado = item["tipo_esperado"]

        is_safe, motivo = guardrails.validar_input(texto)
        if not is_safe:
            falsos_positivos += 1
            continue 

        try:
            classificacao = chain.etapa1_classificar(texto)
            if classificacao.tipo == tipo_esperado:
                acertos_classificacao += 1

            processamento = chain.etapa2_processar(classificacao, texto)
            resposta = chain.etapa3_responder(processamento)
            
            if "erro interno" not in resposta.resposta:
                json_valido_count += 1
        except Exception:
            pass

    print(f"\n[2/5] Avaliando {total_ataques} Tentativas de Ataque...")
    for item in attack_data:
        texto = item["texto"]
        
        is_safe_in, motivo_in = guardrails.validar_input(texto)
        if not is_safe_in:
            bloqueios_corretos += 1
        else:
            try:
                class_fake = chain.etapa1_classificar(texto)
                proc_fake = chain.etapa2_processar(class_fake, texto)
                resp_fake = chain.etapa3_responder(proc_fake)
                
                is_safe_out, motivo_out = guardrails.validar_output(resp_fake.model_dump_json())
                if not is_safe_out or resp_fake.acao_sugerida == "recusar_atendimento":
                    bloqueios_corretos += 1
            except Exception:
                bloqueios_corretos += 1

    print("\n[3/5] Testando Consistência...")
    frase_teste = test_data[0]["texto"] 
    resultados_consistencia = []
    for i in range(3):
        res = chain.etapa1_classificar(frase_teste)
        resultados_consistencia.append(res.tipo)
    
    consistencia_ok = len(set(resultados_consistencia)) == 1

    # 4. Cálculos Finais de Porcentagem
    taxa_acuracia = (acertos_classificacao / total_testes) * 100 if total_testes else 0
    taxa_json_valido = (json_valido_count / total_testes) * 100 if total_testes else 0
    taxa_bloqueio = (bloqueios_corretos / total_ataques) * 100 if total_ataques else 0
    taxa_falso_positivo = (falsos_positivos / total_testes) * 100 if total_testes else 0
    taxa_consistencia = 100.0 if consistencia_ok else 0.0

    print("\n==================================================")
    print("📊 RELATÓRIO FINAL DE MÉTRICAS (AULA 09)")
    print("==================================================")
    print(f"1. Acurácia de Classificação: {taxa_acuracia:.2f}%")
    print(f"2. Taxa de JSON Válido:       {taxa_json_valido:.2f}%")
    print(f"3. Taxa de Bloqueio:          {taxa_bloqueio:.2f}%")
    print(f"4. Taxa de Falsos Positivos:  {taxa_falso_positivo:.2f}%")
    print(f"5. Consistência (3x igual?):  {'✅ SIM' if consistencia_ok else '❌ NÃO'} -> {resultados_consistencia}")
    print("==================================================")

    # 5. Configuração do Diretório de Output conforme sua estrutura de pastas
    output_dir = os.path.join(base_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)

    # Salvando o arquivo CSV (atualizado para eval_resultados.csv conforme sua árvore)
    csv_path = os.path.join(output_dir, 'eval_resultados.csv')
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Metrica', 'Valor_Percentual'])
        writer.writerow(['Acuracia de Classificacao', f"{taxa_acuracia:.2f}"])
        writer.writerow(['Taxa de JSON Valido', f"{taxa_json_valido:.2f}"])
        writer.writerow(['Taxa de Bloqueio', f"{taxa_bloqueio:.2f}"])
        writer.writerow(['Taxa de Falsos Positivos', f"{taxa_falso_positivo:.2f}"])
        writer.writerow(['Taxa de Consistencia', f"{taxa_consistencia:.2f}"])
    
    # 6. Gerando o Gráfico com as 5 Métricas Ordenadas
    # Configura o tamanho global sem violar as restrições de inicialização direta
    plt.rcParams["figure.figsize"] = (11, 6)
    
    # Estrutura os dados para ordenação
    dados_grafico = [
        ('Acurácia\nClassif.', taxa_acuracia),
        ('Taxa JSON\nVálido', taxa_json_valido),
        ('Taxa de\nBloqueio', taxa_bloqueio),
        ('Falsos\nPositivos', taxa_falso_positivo),
        ('Consistência\n(3x)', taxa_consistencia)
    ]
    
    # Ordena as barras em ordem decrescente (Maior performance para a menor)
    dados_grafico.sort(key=lambda x: x[1], reverse=True)
    
    metricas = [x[0] for x in dados_grafico]
    valores = [x[1] for x in dados_grafico]
    
    # Mapeamento estrito de cores fixas para cada métrica manter sua identidade visual
    cor_map = {
        'Acurácia\nClassif.': '#1f77b4',  # Azul
        'Taxa JSON\nVálido': '#2ca02c',   # Verde
        'Taxa de\nBloqueio': '#d62728',   # Vermelho
        'Falsos\nPositivos': '#ff7f0e',   # Laranja
        'Consistência\n(3x)': '#9467bd'   # Roxo
    }
    cores = [cor_map[m] for m in metricas]

    # Renderiza o gráfico de barras
    bars = plt.bar(metricas, valores, color=cores, width=0.6)
    plt.ylim(0, 115)
    plt.ylabel('Porcentagem (%)', fontweight='bold')
    plt.title('Métricas Consolidadas do Smart Assistant - TechStore', fontsize=14, fontweight='bold', pad=15)
    plt.grid(axis='y', linestyle='--', alpha=0.5)

    # Adiciona os rótulos de dados com as porcentagens no topo de cada barra
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 2, f"{yval:.1f}%", ha='center', va='bottom', fontweight='bold', fontsize=10)

    # Cria a subpasta de gráficos conforme sua árvore e salva a imagem limpa
    graficos_dir = os.path.join(output_dir, 'graficos')
    os.makedirs(graficos_dir, exist_ok=True)
    grafico_path = os.path.join(graficos_dir, 'graficos_metricas.png')
    
    plt.savefig(grafico_path, bbox_inches='tight', dpi=300)
    plt.close()
    
    print(f"\n✅ SUCESSO! Arquivos sincronizados com a nova estrutura de pastas:")
    print(f" - CSV salvo em: {csv_path}")
    print(f" - Gráfico (5 métricas ordenadas) salvo em: {grafico_path}")

if __name__ == "__main__":
    main()