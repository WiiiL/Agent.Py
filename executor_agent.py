"""
Agente Executor para execução de consultas SQL/API
"""

import json
import logging
import time
from typing import Dict, Any, List, Union

import requests
from config import EXECUTOR_CONFIG, DB_CONFIG, API_CONFIG, LOGGING_CONFIG

logging.basicConfig(
    level=LOGGING_CONFIG.get("level", logging.INFO),
    format=LOGGING_CONFIG.get("format", '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
    filename=LOGGING_CONFIG.get("file_path"),
)

logger = logging.getLogger("executor_agent")

class ExecutorAgent:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or EXECUTOR_CONFIG
        self.db_config = DB_CONFIG
        self.api_config = API_CONFIG
        logger.info("Agente Executor inicializado")
        
    def execute_query(self, query_type: str, query_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        logger.info(f"Executando consulta do tipo {query_type}")
        result = {
            "query_type": query_type,
            "query_data": query_data,
            "execution_time": None,
            "result": None,
            "error": None
        }
        
        try:
            start_time = time.time()
            
            if query_type == "sql":
                result["result"] = self._execute_sql(query_data)
            elif query_type == "api":
                result["result"] = self._execute_api(query_data)
            else:
                raise ValueError(f"Tipo de consulta não suportado: {query_type}")
            
            result["execution_time"] = time.time() - start_time
            logger.info(f"Consulta executada em {result['execution_time']:.2f} segundos")
            
        except Exception as e:
            logger.error(f"Erro ao executar consulta: {str(e)}", exc_info=True)
            result["error"] = str(e)
            
        return result
    
    def _execute_sql(self, sql_query: str) -> List[Dict[str, Any]]:
        logger.info(f"Executando SQL: {sql_query}")
        
        import pyodbc

        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={self.db_config['server']};"
            f"DATABASE={self.db_config['database']};"
            f"UID={self.db_config['username']};"
            f"PWD={self.db_config['password']}"
        )

        try:
            with pyodbc.connect(conn_str) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql_query)
                    columns = [column[0] for column in cursor.description]
                    results = []
                    for row in cursor.fetchall():
                        results.append(dict(zip(columns, row)))
                    return results
        except Exception as e:
            logger.error(f"Erro ao executar SQL: {str(e)}", exc_info=True)
    
    def _execute_api(self, api_data: Dict[str, Any]) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        logger.info(f"Executando chamada de API: {json.dumps(api_data)}")
        
        endpoint = api_data.get("endpoint", "/api/cadastro")
        params = api_data.get("params", {})
        
        if endpoint == "/api/cadastro":
            return [
                {"Id": 1, "Nome": "João Silva", "Email": "joao@email.com", "DataInclusao": "2023-04-01T10:30:00", "Status": "Ativo"},
                {"Id": 2, "Nome": "Maria Souza", "Email": "maria@email.com", "DataInclusao": "2023-05-05T14:20:00", "Status": "Ativo"},
                {"Id": 3, "Nome": "Pedro Santos", "Email": "pedro@gmail.com", "DataInclusao": "2023-05-10T09:15:00", "Status": "Ativo"}
            ]
        else:
            raise ValueError(f"Endpoint não suportado: {endpoint}")

if __name__ == "__main__":
    executor = ExecutorAgent()
    
    # Teste com uma consulta SQL de exemplo
    test_sql = "SELECT * FROM Cadastro WITH (NOLOCK) WHERE DataInclusao BETWEEN DATEADD(month, -1, GETDATE()) AND GETDATE() AND Status = 1"
    
    result = executor.execute_query("sql", test_sql)
    
    print(json.dumps(result, indent=2, ensure_ascii=False)) 