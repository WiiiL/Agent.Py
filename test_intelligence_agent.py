"""
Testes para o Agente de Inteligência
"""

import json
import unittest
from unittest.mock import patch, MagicMock, mock_open
import os

# Importar o Agente de Inteligência
from intelligence_agent import IntelligenceAgent

class TestIntelligenceAgent(unittest.TestCase):
    
    def setUp(self):
        """Preparar ambiente para testes"""
        # Mock para os diretórios de dados
        self.mock_schema = {
            "Cadastro": {
                "tabela": "Cadastro",
                "colunas": {
                    "CadastroId": {"tipo": "int", "primaryKey": True, "autoIncrement": True},
                    "Nome": {"tipo": "varchar(100)", "nullable": False},
                    "Email": {"tipo": "varchar(100)", "nullable": True},
                    "Celular": {"tipo": "varchar(20)", "nullable": True},
                    "DataCadastro": {"tipo": "datetime", "nullable": False},
                    "Status": {"tipo": "varchar(20)", "nullable": False},
                    "DataInclusao": {"tipo": "datetime", "nullable": False}
                }
            }
        }
        
        # Configurar patches para os métodos que carregam dados
        self.schema_patcher = patch.object(IntelligenceAgent, '_load_db_schema', return_value=self.mock_schema)
        self.regulations_patcher = patch.object(IntelligenceAgent, '_load_regulations', return_value=[])
        self.api_ref_patcher = patch.object(IntelligenceAgent, '_load_api_references', return_value={
            "endpoints": {
                "/api/cadastro": {
                    "metodos": ["GET", "POST"],
                    "descricao": "Gerenciamento de cadastros",
                    "parametros": {
                        "nome": "Filtrar por nome (pesquisa parcial)",
                        "email": "Filtrar por email exato",
                        "status": "Filtrar por status (Ativo, Inativo)",
                        "dataInclusao": "Filtrar por data de cadastro inicial"
                    },
                    "permissoes": ["administrativo"],
                    "exemplo": "/api/cadastro?status=Ativo&dataInclusao=2023-01-01"
                }
            }
        })
        
        # Patch para o método de análise de intenção
        self.intent_patcher = patch.object(IntelligenceAgent, '_analyze_intent')
        
        # Patch para o método de envio ao executor
        self.executor_patcher = patch.object(IntelligenceAgent, '_send_to_executor')
        
        # Iniciar os patches
        self.mock_schema_loader = self.schema_patcher.start()
        self.mock_regulations_loader = self.regulations_patcher.start()
        self.mock_api_ref_loader = self.api_ref_patcher.start()
        self.mock_intent_analyzer = self.intent_patcher.start()
        self.mock_executor_sender = self.executor_patcher.start()
        
        # Configurar o comportamento do analisador de intenção
        self.mock_intent_analyzer.return_value = ("sql", {
            "entities": ["Cadastro"],
            "conditions": ["DataInclusao >= '2023-01-01'", "DataInclusao <= '2023-01-31'"],
            "fields": ["*"]
        })
        
        # Configurar o comportamento do sender do executor
        self.mock_executor_sender.return_value = {
            "status": "success",
            "results": [
                {"CadastroId": 1, "Nome": "João Silva", "Email": "joao@exemplo.com", "Status": "Ativo"},
                {"CadastroId": 2, "Nome": "Maria Santos", "Email": "maria@exemplo.com", "Status": "Ativo"}
            ]
        }
    
    def tearDown(self):
        """Limpar ambiente após testes"""
        # Parar todos os patches
        self.schema_patcher.stop()
        self.regulations_patcher.stop()
        self.api_ref_patcher.stop()
        self.intent_patcher.stop()
        self.executor_patcher.stop()
    
    @patch('openai.ChatCompletion.create')
    def test_process_query_sql(self, mock_openai):
        """Testar processamento de consulta que gera SQL"""
        # Configurar o comportamento simulado do OpenAI
        mock_openai.return_value.choices = [
            MagicMock(message={"content": "SELECT * FROM Cadastro WHERE DataInclusao BETWEEN '2023-01-01' AND '2023-01-31'"})
        ]
        
        # Criar instância do agente
        agent = IntelligenceAgent()
        
        # Executar método a ser testado
        result = agent.process_query("Mostrar cadastros de janeiro de 2023")
        
        # Verificar resultados
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["query_type"], "sql")
        self.assertTrue(isinstance(result["result"], dict))
        
        # Verificar chamadas aos métodos mockados
        self.mock_intent_analyzer.assert_called_once()
        self.mock_executor_sender.assert_called_once()
    
    @patch('openai.ChatCompletion.create')
    def test_process_query_api(self, mock_openai):
        """Testar processamento de consulta que gera chamada API"""
        # Alterar o comportamento do analisador de intenção para retornar API
        self.mock_intent_analyzer.return_value = ("api", {
            "endpoint": "/api/cadastro",
            "params": {"status": "Ativo", "dataInclusao": "2023-01-01"}
        })
        
        # Configurar o comportamento simulado do OpenAI
        mock_openai.return_value.choices = [
            MagicMock(message={"content": json.dumps({
                "endpoint": "/api/cadastro",
                "params": {"status": "Ativo", "dataInclusao": "2023-01-01"}
            })})
        ]
        
        # Criar instância do agente
        agent = IntelligenceAgent()
        
        # Executar método a ser testado
        result = agent.process_query("Mostrar cadastros ativos de janeiro de 2023")
        
        # Verificar resultados
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["query_type"], "api")
        
        # Verificar chamadas aos métodos mockados
        self.mock_intent_analyzer.assert_called_once()
        self.mock_executor_sender.assert_called_once()
    
    def test_handle_error(self):
        """Testar tratamento de erro durante processamento"""
        # Fazer com que o analisador de intenção lance uma exceção
        self.mock_intent_analyzer.side_effect = ValueError("Consulta não reconhecida")
        
        # Criar instância do agente
        agent = IntelligenceAgent()
        
        # Executar método a ser testado
        result = agent.process_query("Consulta com formato irreconhecível")
        
        # Verificar resultados
        self.assertEqual(result["status"], "error")
        self.assertTrue("message" in result)
        self.assertTrue("Consulta não reconhecida" in result["message"])

if __name__ == '__main__':
    unittest.main() 