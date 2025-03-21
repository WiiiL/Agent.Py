"""
Módulo de inicialização para o Agente de Inteligência
"""

import os
import json
import logging
from typing import Dict, Any

from google import genai
from config import AGENT_CONFIG, TRAINING_DATA, LOGGING_CONFIG

# Configurar logger
logger = logging.getLogger("agent_initializer")

class AgentInitializer:
    """Classe responsável por inicializar o agente"""
    
    def initialize_agent(self) -> Dict[str, Any]:
        """
        Inicializa o agente carregando todos os dados necessários
        
        Returns:
            Dicionário com os dados do agente inicializado
        """
        logger.info("Iniciando carregamento dos dados do agente")
        
        # Garantir que os diretórios necessários existem
        self._ensure_directories()
        
        # Carregar esquemas do banco de dados
        db_schema = self._load_db_schema()
        
        # Carregar regulamentos (se necessário)
        regulations = self._load_regulations()
        
        # Carregar referências de API (se necessário)
        api_references = self._load_api_references()
        
        # Configurar o cliente Gemini (se aplicável)
        if "gemini" in AGENT_CONFIG.get("model_name", "").lower():
            gemini_api_key = os.getenv("GEMINI_API_KEY", "")
            if not gemini_api_key:
                logger.warning("Chave da API Gemini não encontrada. Verifique as variáveis de ambiente.")
            else:
                genai.configure(api_key=gemini_api_key)
                logger.info("Cliente Gemini configurado com sucesso")
        
        # Construir os dados do agente
        agent_data = {
            "model_name": AGENT_CONFIG.get("model_name", ""),
            "language": AGENT_CONFIG.get("language", "pt-BR"),
            "db_schema": db_schema,
            "regulations": regulations,
            "api_references": api_references
        }
        
        logger.info("Agente inicializado com sucesso")
        return agent_data
    
    def _ensure_directories(self) -> None:
        """
        Garante que todos os diretórios necessários existam
        """
        directories = [
            TRAINING_DATA["base_path"],
            TRAINING_DATA["schemas_path"],
            TRAINING_DATA["regulations_path"],
            TRAINING_DATA["api_references_path"]
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                logger.info(f"Criando diretório: {directory}")
                os.makedirs(directory, exist_ok=True)
    
    def _load_db_schema(self) -> Dict[str, Any]:
        """
        Carrega os esquemas de banco de dados
        
        Returns:
            Dicionário com os esquemas carregados
        """
        schema = {}
        schemas_path = TRAINING_DATA["schemas_path"]
        
        try:
            # Tentar carregar o arquivo db_schema.json
            schema_file = os.path.join(schemas_path, "db_schema.json")
            if os.path.exists(schema_file):
                with open(schema_file, 'r', encoding='utf-8') as file:
                    schema = json.load(file)
                    logger.info(f"Esquema de banco carregado de {schema_file}")
            else:
                # Procurar outros arquivos JSON na pasta
                for filename in os.listdir(schemas_path):
                    if filename.endswith('.json') and filename != "queries.json":
                        file_path = os.path.join(schemas_path, filename)
                        with open(file_path, 'r', encoding='utf-8') as file:
                            schema_part = json.load(file)
                            schema.update(schema_part)
                        logger.info(f"Esquema de banco parcial carregado de {file_path}")
        except Exception as e:
            logger.error(f"Erro ao carregar esquemas de banco: {str(e)}")
        
        if not schema:
            # Criar um esquema padrão simples
            schema = {
                "Cadastro": {
                    "nome": "Cadastro",
                    "descricao": "Tabela de cadastros",
                    "campos": [
                        {"nome": "Id", "tipo": "int", "descricao": "ID do cadastro"},
                        {"nome": "Nome", "tipo": "varchar", "descricao": "Nome da pessoa"},
                        {"nome": "Email", "tipo": "varchar", "descricao": "Email da pessoa"},
                        {"nome": "Ativo", "tipo": "boolean", "descricao": "Status do cadastro (1 = Ativo, 0 = Inativo)"},
                        {"nome": "DataInclusao", "tipo": "datetime", "descricao": "Data de inclusão"}
                    ]
                }
            }
            logger.warning("Esquema de banco padrão criado devido a erro ou ausência de arquivos")
        
        return schema
    
    def _load_regulations(self) -> Dict[str, Any]:
        """
        Carrega regulamentos e documentação
        
        Returns:
            Dicionário com os regulamentos carregados
        """
        regulations = {}
        regulations_path = TRAINING_DATA["regulations_path"]
        
        try:
            for filename in os.listdir(regulations_path):
                if filename.endswith('.json'):
                    file_path = os.path.join(regulations_path, filename)
                    with open(file_path, 'r', encoding='utf-8') as file:
                        reg_data = json.load(file)
                        regulations.update(reg_data)
                    logger.info(f"Regulamento carregado de {file_path}")
        except Exception as e:
            logger.error(f"Erro ao carregar regulamentos: {str(e)}")
        
        return regulations
    
    def _load_api_references(self) -> Dict[str, Any]:
        """
        Carrega referências de API
        
        Returns:
            Dicionário com as referências de API carregadas
        """
        api_references = {}
        api_references_path = TRAINING_DATA["api_references_path"]
        
        try:
            for filename in os.listdir(api_references_path):
                if filename.endswith('.json'):
                    file_path = os.path.join(api_references_path, filename)
                    with open(file_path, 'r', encoding='utf-8') as file:
                        api_data = json.load(file)
                        api_references.update(api_data)
                    logger.info(f"Referência de API carregada de {file_path}")
        except Exception as e:
            logger.error(f"Erro ao carregar referências de API: {str(e)}")
        
        return api_references 