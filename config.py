"""
Configurações para o sistema de Agentes SQL Inteligentes
"""

import os
import logging
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações de logging
LOGGING_CONFIG = {
    "level": logging.INFO,
    "format": '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    "file_path": os.getenv("LOG_FILE_PATH", "agent_log.log")
}

# Configurações do Agente de Inteligência
AGENT_CONFIG = {
    "model_name": os.getenv("MODEL_NAME", "gemini-2.0-flash"),
    "language": "pt-BR",
    "max_tokens": 8192
}

# Configurações de IA (Gemini/OpenAI)
NLP_CONFIG = {
    "temperature": 0.2,
    "max_tokens": 8192,
    "top_p": 0.95,
    "top_k": 64,
    "system_instruction": "Você é um assistente especializado em gerar consultas SQL precisas e seguras a partir de linguagem natural."
}

# Configurações específicas do Gemini
GEMINI_CONFIG = {
    "model": "gemini-2.0-flash",
    "response_mime_type": "text/plain",
}

# Configurações do banco de dados
DB_CONFIG = {
    "driver": os.getenv("DB_DRIVER", "{SQL Server}"),
    "server": os.getenv("DB_SERVER", "localhost"),
    "database": os.getenv("DB_NAME", "Cadastro"),
    "username": os.getenv("DB_USER", ""),
    "password": os.getenv("DB_PASS", ""),
    "trusted_connection": os.getenv("DB_TRUSTED_CONNECTION", "yes").lower() == "yes"
}

# Configurações da API
API_CONFIG = {
    "host": os.getenv("API_HOST", "localhost"),
    "port": int(os.getenv("API_PORT", "5000")),
    "debug": os.getenv("API_DEBUG", "False").lower() == "true",
    "base_url": os.getenv("API_BASE_URL", "/api"),
    "auth_token": os.getenv("API_AUTH_TOKEN", "")
}

# Configurações do Executor
EXECUTOR_CONFIG = {
    "timeout": int(os.getenv("EXECUTOR_TIMEOUT", "30")),
    "max_rows": int(os.getenv("EXECUTOR_MAX_ROWS", "1000")),
    "simulate": os.getenv("EXECUTOR_SIMULATE", "True").lower() == "true"
}

# Caminhos para dados de treinamento
TRAINING_DATA = {
    "base_path": os.getenv("TRAINING_DATA_PATH", "data"),
    "schemas_path": os.getenv("SCHEMAS_PATH", "data/schemas"),
    "regulations_path": os.getenv("REGULATIONS_PATH", "data/regulations"),
    "api_references_path": os.getenv("API_REFERENCES_PATH", "data/api_references")
}

# Configurações de segurança
SECURITY_CONFIG = {
    "blocked_keywords": [
        "DROP", "DELETE", "TRUNCATE", "ALTER", "xp_", "sp_", "UPDATE", "INSERT", "MERGE", 
        "CREATE", "EXEC", "EXECUTE"
    ],
    "allowed_tables": ["Cadastro"],
    "max_query_length": 4000,
    "require_nolock": True
} 