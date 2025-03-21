"""
Módulo de processamento de resultados para o Agente de Inteligência
"""

import json
import logging
from typing import Dict, Any, List, Union

from google import genai
from google.genai import types
from config import NLP_CONFIG, GEMINI_CONFIG

logger = logging.getLogger("result_processor")

class ResultProcessor:
    def __init__(self, agent_config: Dict[str, Any]):
        self.model_name = agent_config["model_name"]
        self.language = agent_config.get("language", "pt-BR")
    
    def process_result(self, query: str, result: Union[List[Dict[str, Any]], Dict[str, Any]], 
                      sql_query: str = None) -> str:
        if not result:
            return "Não foram encontrados resultados para sua consulta."
        
        # Verificar qual modelo usar
        return self._process_with_gemini(query, result, sql_query)
    
    def _process_with_gemini(self, query: str, result: Union[List[Dict[str, Any]], Dict[str, Any]], 
                           sql_query: str = None) -> str:
        system_message = (
            "Você é um assistente especializado em explicar resultados de consultas de banco de dados. "
            "Sua tarefa é responder a pergunta do usuário com base nos resultados fornecidos. "
            "Seja conciso e direto, focando apenas nas informações relevantes para a pergunta."
        )
        
        # Formatar o resultado como JSON para o modelo
        if isinstance(result, list):
            formatted_result = json.dumps(result[:20], ensure_ascii=False, indent=2)  # Limitamos a 20 registros
            result_count = len(result)
        else:
            formatted_result = json.dumps(result, ensure_ascii=False, indent=2)
            result_count = 1
        
        sql_context = f"\nConsulta SQL executada: {sql_query}" if sql_query else ""
        
        user_content = (
            f"Pergunta do usuário: {query}\n\n"
            f"Resultados da consulta ({result_count} registros encontrados):{sql_context}\n{formatted_result}\n\n"
            f"Por favor, responda à pergunta do usuário com base nestes resultados. "
            f"Seja direto e claro, evitando explicações desnecessárias. "
            f"Resuma os dados de forma útil e relevante para a pergunta."
        )
        
        try:
            client = genai.Client(
                api_key="",
            )
            
            content = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=user_content)]
                )
            ]
            
            generate_config = types.GenerateContentConfig(
                temperature=NLP_CONFIG["temperature"],
                top_p=NLP_CONFIG["top_p"],
                top_k=NLP_CONFIG["top_k"],
                max_output_tokens=NLP_CONFIG["max_tokens"],
                response_mime_type=GEMINI_CONFIG["response_mime_type"],
                system_instruction=[
                    types.Part.from_text(text=system_message)
                ]
            )
            
            response_text = ""
            for chunk in client.models.generate_content_stream(
                model="gemini-2.0-flash",
                contents=content,
                config=generate_config,
            ):
                if chunk.text:
                    response_text += chunk.text
            
            answer = response_text.strip()
            print(f"Resposta gerada para os resultados: {answer[:100]}...")
            return answer
            
        except Exception as e:
            logger.error(f"Erro ao processar resultado com Gemini: {str(e)}")
            return None