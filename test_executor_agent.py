"""
Testes para o Agente Executor
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import datetime

# Importar classes do Agente Executor
from executor_agent import QueryValidator, DatabaseConnector, ExecutorAgent, app

class TestQueryValidator(unittest.TestCase):
    
    def setUp(self):
        """Preparar ambiente para testes"""
        self.validator = QueryValidator()
        
    def test_validate_query_success(self):
        """Testar validação de consulta SQL válida"""
        query = "SELECT * FROM Cadastro WHERE Status = 'Ativo'"
        is_valid, reason = self.validator.validate_query(query)
        self.assertTrue(is_valid)
    
    def test_validate_query_blocked_keyword(self):
        """Testar bloqueio de palavra-chave proibida"""
        query = "DROP TABLE Cadastro"
        is_valid, reason = self.validator.validate_query(query)
        self.assertFalse(is_valid)
        self.assertTrue("DROP" in reason)
    
    def test_validate_query_length(self):
        """Testar limite de tamanho de consulta"""
        query = "SELECT * FROM Cadastro" * 100  # Consulta muito grande
        is_valid, reason = self.validator.validate_query(query)
        self.assertFalse(is_valid)
        self.assertTrue("tamanho máximo" in reason.lower())
    
    def test_extract_tables_from_query(self):
        """Testar extração de tabelas da consulta"""
        query = "SELECT c.Nome, c.Email FROM Cadastro c WHERE c.Status = 'Ativo'"
        tables = self.validator._extract_tables_from_query(query)
        self.assertEqual(len(tables), 1)
        self.assertTrue("Cadastro" in tables)
    
    def test_sanitize_query(self):
        """Testar sanitização de consulta"""
        query = "SELECT * FROM Cadastro -- Comentário a ser removido"
        sanitized = self.validator.sanitize_query(query)
        self.assertEqual(sanitized, "SELECT * FROM Cadastro")

class TestDatabaseConnector(unittest.TestCase):
    
    def setUp(self):
        """Preparar ambiente para testes"""
        # Patch para pyodbc.connect
        self.pyodbc_patcher = patch('pyodbc.connect')
        self.mock_pyodbc = self.pyodbc_patcher.start()
        
        # Mock para a conexão e cursor
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cursor
        self.mock_pyodbc.return_value = self.mock_conn
        
        # Configurar cursor para retornar resultados simulados
        self.mock_cursor.description = [
            ["CadastroId"], ["Nome"], ["Email"], ["Status"]
        ]
        self.mock_cursor.fetchall.return_value = [
            (1, "João Silva", "joao@exemplo.com", "Ativo"),
            (2, "Maria Santos", "maria@exemplo.com", "Ativo")
        ]
        
        # Patch para QueryValidator
        self.validator_patcher = patch.object(QueryValidator, 'validate_query')
        self.mock_validator = self.validator_patcher.start()
        self.mock_validator.return_value = (True, "Consulta válida")
        
        # Inicializar o conector
        self.connector = DatabaseConnector()
    
    def tearDown(self):
        """Limpar ambiente após testes"""
        self.pyodbc_patcher.stop()
        self.validator_patcher.stop()
    
    def test_execute_query_select(self):
        """Testar execução de consulta SELECT"""
        query = "SELECT * FROM Cadastro WHERE DataInclusao >= '2023-01-01'"
        
        result = self.connector.execute_query(query)
        
        # Verificar resultados
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["operation"], "SELECT")
        
        # Verificar chamadas aos métodos mockados
        self.mock_validator.assert_called_once()
        self.mock_cursor.execute.assert_called_once_with(query)
        self.mock_cursor.fetchall.assert_called_once()
    
    def test_execute_query_insert(self):
        """Testar execução de consulta INSERT"""
        # Configurar comportamento para INSERT
        self.mock_cursor.rowcount = 1
        self.mock_cursor.description = None
        
        query = "INSERT INTO Cadastro (Nome, Email, Celular, Status) VALUES ('Carlos Oliveira', 'carlos@exemplo.com', '11987654321', 'Ativo')"
        
        result = self.connector.execute_query(query)
        
        # Verificar resultados
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["operation"], "INSERT")
        self.assertEqual(result["results"][0]["affected_rows"], 1)
        
        # Verificar chamadas aos métodos mockados
        self.mock_conn.commit.assert_called_once()
    
    def test_execute_query_validation_fail(self):
        """Testar falha na validação da consulta"""
        # Alterar comportamento do validador para rejeitar a consulta
        self.mock_validator.return_value = (False, "Consulta contém palavras-chave bloqueadas")
        
        query = "DROP TABLE Cadastro"
        
        result = self.connector.execute_query(query)
        
        # Verificar resultados
        self.assertEqual(result["status"], "error")
        self.assertTrue("segurança" in result["message"].lower())
        
        # Verificar que execute não foi chamado
        self.mock_cursor.execute.assert_not_called()

class TestExecutorAgent(unittest.TestCase):
    
    def setUp(self):
        """Preparar ambiente para testes"""
        # Patch para DatabaseConnector.execute_query
        self.db_patcher = patch.object(DatabaseConnector, 'execute_query')
        self.mock_db = self.db_patcher.start()
        
        # Configurar comportamento do conector
        self.mock_db.return_value = {
            "status": "success",
            "results": [{"CadastroId": 1, "Nome": "João Silva", "Email": "joao@exemplo.com", "Status": "Ativo"}]
        }
        
        # Inicializar o agente
        self.agent = ExecutorAgent()
    
    def tearDown(self):
        """Limpar ambiente após testes"""
        self.db_patcher.stop()
    
    def test_execute_sql(self):
        """Testar execução de consulta SQL"""
        query = "SELECT * FROM Cadastro"
        
        result = self.agent.execute("sql", query)
        
        # Verificar resultados
        self.assertEqual(result["status"], "success")
        
        # Verificar chamadas aos métodos mockados
        self.mock_db.assert_called_once_with(query, None)
    
    def test_execute_api(self):
        """Testar execução de chamada API"""
        result = self.agent.execute("api", "/api/cadastro", {"status": "Ativo"})
        
        # APIHandler ainda não está completamente implementado
        self.assertEqual(result["status"], "error")
    
    def test_execute_invalid_type(self):
        """Testar tipo de consulta inválido"""
        result = self.agent.execute("invalid", "consulta")
        
        # Verificar resultados
        self.assertEqual(result["status"], "error")
        self.assertTrue("não suportado" in result["message"].lower())

class TestFlaskAPI(unittest.TestCase):
    
    def setUp(self):
        """Preparar ambiente para testes"""
        # Configurar cliente de teste Flask
        app.testing = True
        self.client = app.test_client()
        
        # Patch para ExecutorAgent.execute
        self.agent_patcher = patch.object(ExecutorAgent, 'execute')
        self.mock_agent = self.agent_patcher.start()
        
        # Configurar comportamento do agente
        self.mock_agent.return_value = {
            "status": "success",
            "results": [{"CadastroId": 1, "Nome": "João Silva", "Email": "joao@exemplo.com", "Status": "Ativo"}]
        }
    
    def tearDown(self):
        """Limpar ambiente após testes"""
        self.agent_patcher.stop()
    
    def test_health_check(self):
        """Testar endpoint de health check"""
        response = self.client.get('/health')
        
        # Verificar resultados
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "healthy")
    
    def test_execute_query(self):
        """Testar endpoint de execução de consulta"""
        payload = {
            "query_type": "sql",
            "query": "SELECT * FROM Cadastro",
            "params": {}
        }
        
        response = self.client.post('/execute', 
                                   data=json.dumps(payload),
                                   content_type='application/json')
        
        # Verificar resultados
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        
        # Verificar chamadas aos métodos mockados
        self.mock_agent.assert_called_once_with("sql", "SELECT * FROM Cadastro", {})
    
    def test_execute_query_missing_fields(self):
        """Testar endpoint com campos obrigatórios ausentes"""
        payload = {
            "query": "SELECT * FROM Cadastro"
            # query_type ausente
        }
        
        response = self.client.post('/execute', 
                                   data=json.dumps(payload),
                                   content_type='application/json')
        
        # Verificar resultados
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "error")

if __name__ == '__main__':
    unittest.main() 