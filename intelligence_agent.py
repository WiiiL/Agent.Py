"""
Agente de Inteligência para conversão de linguagem natural em consultas SQL/API
"""

import logging
import os
from typing import Dict, Any

from agent_initializer import AgentInitializer
from agent_analyzer import IntentAnalyzer
from query_generator import QueryGenerator
from result_processor import ResultProcessor
from executor_agent import ExecutorAgent
from config import AGENT_CONFIG, LOGGING_CONFIG

# Configurar logger
logging.basicConfig(
    level=LOGGING_CONFIG.get("level", logging.INFO),
    format=LOGGING_CONFIG.get("format", '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
    filename=LOGGING_CONFIG.get("file_path"),
)

logger = logging.getLogger("intelligence_agent")

class IntelligenceAgent:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or AGENT_CONFIG
        logger.info("Inicializando Agente de Inteligência")
        
        initializer = AgentInitializer()
        self.agent_data = initializer.initialize_agent()
        
        self.analyzer = IntentAnalyzer(self.agent_data)
        self.query_generator = QueryGenerator(self.agent_data)
        self.result_processor = ResultProcessor(self.agent_data)
        self.executor = ExecutorAgent(self.agent_data)

        logger.info("Agente de Inteligência inicializado com sucesso")
    
    def process_query(self, query: str, execute_query: bool = False) -> Dict[str, Any]:
        logger.info(f"Processando consulta: {query}")

        result = {
            "query": query,
            "query_type": None,
            "generated_query": None,
            "result": None,
            "response": None,
            "error": None
        }
        
        try:
            query_type, intent_data = self.analyzer.analyze_intent(query)
            result["query_type"] = query_type
            result["intent_data"] = intent_data
            
            if query_type == "sql":
                generated_query = self.query_generator.generate_sql_query(query, intent_data)
                result["generated_query"] = generated_query
                result["result"] = self.executor.execute_query(query_type, generated_query)
            
                response = self.result_processor.process_result(
                    query, 
                    result["result"], 
                    result["generated_query"]
                )
                result["response"] = response
                
        except Exception as e:
            logger.error(f"Erro ao processar consulta: {str(e)}", exc_info=True)
            result["error"] = str(e)
        
        return result


# Para testes locais
if __name__ == "__main__":
    # Exemplo de uso
    agent = IntelligenceAgent()
    
    # Teste com uma consulta de exemplo
    test_query = "Quais são os cadastros ativos registrados no último mês?"
    
    result = agent.process_query(test_query) 
    
    """ print(json.dumps(result, indent=2, ensure_ascii=False))  """