"""
Exemplo de uso do sistema de agentes SQL inteligentes com Gemini
"""

import json
import logging
import os
from intelligence_agent import IntelligenceAgent
from executor_agent import ExecutorAgent
from result_processor import ResultProcessor
from config import LOGGING_CONFIG

# Configurar logger
logging.basicConfig(
    level=LOGGING_CONFIG.get("level", logging.INFO),
    format=LOGGING_CONFIG.get("format", '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
    filename=LOGGING_CONFIG.get("file_path"),
)

logger = logging.getLogger("exemplo_uso")

def verificar_configuracao():
    """Verifica se as configurações necessárias estão presentes"""
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("AVISO: A variável de ambiente GEMINI_API_KEY não está definida.")
        print("Configure essa variável para que o sistema funcione corretamente.")
        return False
    return True

def processar_consulta_natural(consulta: str, executar: bool = True):
    """
    Processa uma consulta em linguagem natural completa
    
    Args:
        consulta: Consulta em linguagem natural
        executar: Se True, executa a consulta gerada
    """
    print("\n" + "="*80)
    print(f"Processando consulta: '{consulta}'")
    print("="*80)
    
    # Inicializar o agente de inteligência
    agente_inteligencia = IntelligenceAgent()
    
    # Analisar a consulta e gerar SQL/API
    resultado_analise = agente_inteligencia.process_query(consulta, execute_query=False)
    
    tipo_consulta = resultado_analise["query_type"]
    consulta_gerada = resultado_analise["generated_query"]
    
    # Exibir o resultado da análise
    print(f"\nTipo de consulta identificado: {tipo_consulta}")
    
    if tipo_consulta == "sql":
        print(f"\nSQL gerado:")
        print(f"  {consulta_gerada}")
    elif tipo_consulta == "api":
        print(f"\nChamada de API gerada:")
        print(f"  Endpoint: {consulta_gerada['endpoint']}")
        print(f"  Parâmetros: {json.dumps(consulta_gerada['params'], indent=2, ensure_ascii=False)}")
    
    # Se solicitado, executar a consulta gerada
    if executar:
        # Inicializar o agente executor
        agente_executor = ExecutorAgent()
        
        print("\nExecutando consulta...")
        resultado_execucao = agente_executor.execute_query(tipo_consulta, consulta_gerada)
        
        if resultado_execucao["error"]:
            print(f"\nErro na execução: {resultado_execucao['error']}")
        else:
            print(f"\nConsulta executada em: {resultado_execucao['execution_time']:.2f} segundos")
            print(f"Registros encontrados: {len(resultado_execucao['result'])}")
            
            # Processar o resultado em linguagem natural
            processador = ResultProcessor(agente_inteligencia.agent_data)
            resposta = processador.process_result(
                consulta, 
                resultado_execucao["result"], 
                consulta_gerada if tipo_consulta == "sql" else None
            )
            
            print("\nResposta:")
            print(f"  {resposta}")
            
            # Exibir os dados (limitado a 3 registros)
            if resultado_execucao["result"] and len(resultado_execucao["result"]) > 0:
                print("\nPrimeiros registros:")
                for i, registro in enumerate(resultado_execucao["result"][:3], 1):
                    print(f"  {i}. {json.dumps(registro, ensure_ascii=False)}")
                
                if len(resultado_execucao["result"]) > 3:
                    print(f"  ... e mais {len(resultado_execucao['result']) - 3} registros")

# Exemplos de consultas para testar
exemplos = [
    "Quais são os cadastros ativos registrados no último mês?",
    "Mostre os cadastros inativos da última semana",
    "Quantos cadastros foram feitos hoje?",
    "Liste todos os cadastros com email gmail",
    "Quem são os cadastros mais recentes?"
]

# Executar os exemplos
if __name__ == "__main__":
    print("\nSISTEMA DE AGENTES SQL INTELIGENTES COM GEMINI - DEMONSTRAÇÃO")
    print("\nEste exemplo demonstra o uso de agentes inteligentes com Gemini para interpretar")
    print("consultas em linguagem natural e convertê-las em comandos SQL ou chamadas de API.")
    
    # Verificar configuração
    if not verificar_configuracao():
        print("\nConfigure a variável de ambiente GEMINI_API_KEY e tente novamente.")
        exit(1)
    
    for i, exemplo in enumerate(exemplos, 1):
        print(f"\n\nEXEMPLO {i}/{len(exemplos)}")
        processar_consulta_natural(exemplo)
        
        if i < len(exemplos):
            input("\nPressione ENTER para continuar para o próximo exemplo...")
    
    print("\n\nDemonstração concluída!") 