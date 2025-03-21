"""
Módulo de análise de intenção para o Agente de Inteligência
"""

import json
import re
import logging
from typing import Dict, Any, Tuple

from google import genai
from google.genai import types
from config import NLP_CONFIG, GEMINI_CONFIG

logger = logging.getLogger("agent_analyzer")

class IntentAnalyzer:
    def __init__(self, agent_config: Dict[str, Any]):
        self.model_name = agent_config["model_name"]
        self.db_schema = agent_config["db_schema"]
    
    def analyze_intent(self, query: str) -> Tuple[str, Dict[str, Any]]:
        return self._analyze_with_gemini(query)
    
    def _analyze_with_gemini(self, query: str) -> Tuple[str, Dict[str, Any]]:
        system_message = (
            "Você é um assistente especializado em analisar consultas e identificar a intenção do usuário. "
            "Para cada consulta, determine:\n"
            "1. O tipo de operação (consulta, inserção, atualização)\n"
            "2. As entidades mencionadas (tabelas, campos)\n"
            "3. Os filtros ou condições mencionados\n"
            "4. Retorne sempre um JSON com type (sql ou api), entities, conditions e fields.\n\n"
        )
        
        context = f"Esquema do banco: {json.dumps(self.db_schema, ensure_ascii=False)}"
        
        prompt = f"{context}\n\nConsulta: {query}"
        
        print(prompt)

        try:
            client = genai.Client(
                api_key="",
            )
            
            content = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)]
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

            try:
                intent_data = json.loads(response_text)
            except json.JSONDecodeError:
                match = re.search(r'({.*})', response_text, re.DOTALL)
                if match:
                    intent_data = json.loads(match.group(1))
                else:
                    raise Exception("Falha ao extrair JSON da resposta")

            query_type = intent_data.get("type", "sql")

            print(f"Intenção analisada: {json.dumps(intent_data, ensure_ascii=False, indent=2)}")
            return query_type, intent_data
        except Exception as e:
            print(f"Erro ao analisar intenção com Gemini: {str(e)}")