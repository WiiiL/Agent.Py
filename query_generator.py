"""
Módulo de geração de consultas SQL para o Agente de Inteligência
"""

import os
import json
import logging
from typing import Dict, Any, List

from google import genai
from google.genai import types
from config import TRAINING_DATA, NLP_CONFIG, GEMINI_CONFIG

logger = logging.getLogger("query_generator")

class QueryGenerator:
    def __init__(self, agent_config: Dict[str, Any]):
        self.model_name = agent_config["model_name"]
        self.db_schema = agent_config["db_schema"]
        self.sql_instructions = self._load_sql_instructions()
    
    def _load_sql_instructions(self) -> Dict[str, Any]:
        try:
            file_path = os.path.join(TRAINING_DATA["schemas_path"], "queries.json")
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    return json.load(file).get("sql_instructions", {})
            else:
                logger.warning(f"Arquivo de instruções SQL não encontrado: {file_path}")
                return {}
        except Exception as e:
            logger.error(f"Erro ao carregar instruções SQL: {str(e)}")
            return {}
    
    def generate_sql_query(self, query: str, intent_data: Dict[str, Any]) -> str:
        return self._generate_with_gemini(query, intent_data)
    
    def _generate_with_gemini(self, query: str, intent_data: Dict[str, Any]) -> str:
        instructions = []
        
        # Instruções gerais
        general_instructions = self.sql_instructions.get("general", [
            "Ao gerar consultas SQL, use o formato SQL Server",
            "Sempre inclua a cláusula WITH (NOLOCK) após cada tabela nas consultas SELECT",
            "Exemplo: SELECT * FROM Tabela WITH (NOLOCK)",
        ])
        
        instructions.append("INSTRUÇÕES GERAIS:")
        for i, instruction in enumerate(general_instructions, 1):
            instructions.append(f"{i}. {instruction}")
        
        # Campos da tabela
        table_fields = self.sql_instructions.get("table_fields", [
            "DataInclusao: Data em que o registro foi incluído no sistema (datetime)",
            "Ativo: Status (1 = Ativo, 0 = Inativo)"
        ])
        
        instructions.append("\nCAMPOS DA TABELA:")
        for i, field in enumerate(table_fields, 1):
            instructions.append(f"{i}. {field}")
        
        # Filtros de data
        date_filters = self.sql_instructions.get("date_filters", [
            "Quando o usuário mencionar 'último mês', use: WHERE DataInclusao BETWEEN DATEADD(month, -1, GETDATE()) AND GETDATE()",
            "Quando o usuário mencionar 'última semana', use: WHERE DataInclusao BETWEEN DATEADD(week, -1, GETDATE()) AND GETDATE()",
            "Quando o usuário mencionar 'hoje', use: WHERE CONVERT(date, DataInclusao) = CONVERT(date, GETDATE())"
        ])
        
        instructions.append("\nFILTROS DE DATA:")
        for i, filter_instruction in enumerate(date_filters, 1):
            instructions.append(f"{i}. {filter_instruction}")
        
        # Filtros de status
        status_filters = self.sql_instructions.get("status_filters", [
            "Quando o usuário mencionar 'ativos', adicione: AND Ativo = 1",
            "Quando o usuário mencionar 'inativos', adicione: AND Ativo = 0"
        ])
        
        instructions.append("\nFILTROS DE STATUS:")
        for i, filter_instruction in enumerate(status_filters, 1):
            instructions.append(f"{i}. {filter_instruction}")
        
        # Buscar exemplos relevantes do arquivo de instruções
        all_examples = self.sql_instructions.get("examples", [])
        relevant_examples = []
        
        # Identificar palavras-chave na consulta do usuário
        keywords = {
            "último mês": False, 
            "ultima semana": False,
            "hoje": False,
            "ativo": False, 
            "inativo": False
        }
        
        query_lower = query.lower()
        for keyword in keywords:
            if keyword in query_lower:
                keywords[keyword] = True
        
        # Selecionar exemplos relevantes baseado nas palavras-chave
        for example in all_examples:
            example_query = example.get("query", "").lower()
            example_relevance = 0
            
            for keyword, is_present in keywords.items():
                if is_present and keyword in example_query:
                    example_relevance += 1
            
            if example_relevance > 0:
                relevant_examples.append(example)
        
        # Adicionar exemplos relevantes ao contexto
        if relevant_examples:
            instructions.append("\nEXEMPLOS RELEVANTES:")
            for i, example in enumerate(relevant_examples, 1):
                instructions.append(f"Exemplo {i}:")
                instructions.append(f"Query: {example.get('query')}")
                instructions.append(f"SQL: {example.get('sql')}")
                instructions.append("")
        
        # Montar o sistema de instruções
        system_instruction = "\n".join(instructions)
        
        # Incluir o schema da tabela e a consulta do usuário
        user_content = (
            f"Esquema da tabela: {json.dumps(self.db_schema, ensure_ascii=False)}\n\n"
            f"Consulta do usuário: {query}\n\n"
            f"Gere uma consulta SQL válida baseada nesta consulta. "
            f"Certifique-se de incluir a cláusula WITH (NOLOCK) após a tabela."
        )
        
        print(user_content)

        try:
            # Criar cliente Gemini
            client = genai.Client(
                api_key="",
            )
            
            print(client)

            # Preparar o conteúdo
            content = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=user_content)]
                )
            ]
            
            # Configurar a geração
            generate_config = types.GenerateContentConfig(
                temperature=NLP_CONFIG["temperature"],
                top_p=NLP_CONFIG["top_p"],
                top_k=NLP_CONFIG["top_k"],
                max_output_tokens=NLP_CONFIG["max_tokens"],
                response_mime_type=GEMINI_CONFIG["response_mime_type"],
                system_instruction=[
                    types.Part.from_text(text=system_instruction)
                ]
            )
            
            # Gerar a consulta SQL
            response_text = ""
            for chunk in client.models.generate_content_stream(
                model="gemini-2.0-flash",
                contents=content,
                config=generate_config,
            ):
                if chunk.text:
                    response_text += chunk.text

            print(response_text)
            sql_query = response_text.strip()

            if "```" in sql_query:
                blocks = sql_query.split("```")
                for block in blocks:
                    if "SELECT" in block.upper() or "WITH" in block.upper():
                        sql_query = block.strip()
                        break
            
            # Verificar e corrigir filtros importantes
            if "último mês" in query.lower() or "ultimo mes" in query.lower():
                if "DATEADD(month, -1" not in sql_query:
                    if "WHERE" in sql_query:
                        sql_query = sql_query.replace("WHERE", "WHERE DataInclusao BETWEEN DATEADD(month, -1, GETDATE()) AND GETDATE() AND ")
                    else:
                        sql_query += " WHERE DataInclusao BETWEEN DATEADD(month, -1, GETDATE()) AND GETDATE()"
            
            if "ativo" in query.lower() and "Ativo = 1" not in sql_query and "Status = 'Ativo'" not in sql_query:
                if "WHERE" in sql_query:
                    sql_query += " AND Ativo = 1"
                else:
                    sql_query += " WHERE Ativo = 1"
            
            print(f"SQL gerado: {sql_query}")
            return sql_query
            
        except Exception as e:
            logger.error(f"Erro ao gerar SQL com Gemini: {str(e)}")