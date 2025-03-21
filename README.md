# Sistema de Agentes SQL Inteligentes

Sistema que permite converter consultas em linguagem natural para consultas SQL ou chamadas de API, utilizando o modelo Google Gemini.

## Visão Geral

Este sistema é composto por módulos independentes que trabalham juntos para:

1. **Interpretar** consultas em linguagem natural
2. **Gerar** consultas SQL válidas ou chamadas de API
3. **Executar** as consultas com segurança
4. **Processar** os resultados e apresentá-los de forma compreensível

## Arquitetura

O sistema segue uma arquitetura modular:

### Módulos Principais

- **Agent Initializer** (`agent_initializer.py`): Inicializa o agente carregando configurações, esquemas de banco e outros recursos necessários.
- **Intent Analyzer** (`agent_analyzer.py`): Analisa a intenção do usuário e identifica entidades, campos e condições.
- **Query Generator** (`query_generator.py`): Gera consultas SQL ou chamadas de API com base na análise de intenção.
- **Executor Agent** (`executor_agent.py`): Executa as consultas SQL ou chamadas de API com segurança.
- **Result Processor** (`result_processor.py`): Processa os resultados e gera respostas em linguagem natural.
- **Intelligence Agent** (`intelligence_agent.py`): Orquestra todos os módulos acima.

### Dados e Configurações

- **config.py**: Configurações gerais do sistema
- **data/schemas/**: Esquemas de banco e instruções para geração de consultas

## Características-chave

- Conversão de linguagem natural para SQL Server com suporte completo à sintaxe
- Inclusão automática da cláusula WITH (NOLOCK) para evitar bloqueios de tabela
- Detecção inteligente de filtros temporais ("último mês", "última semana", etc.)
- Fallback para casos em que o modelo de linguagem falha
- Simulação de execução para ambiente de desenvolvimento
- Utiliza o Google Gemini para processamento de linguagem natural

## Exemplos de Uso

O arquivo `exemplo_uso.py` contém exemplos de como utilizar o sistema:

```python
from intelligence_agent import IntelligenceAgent
from executor_agent import ExecutorAgent
from result_processor import ResultProcessor

# Inicializar agentes
agente_inteligencia = IntelligenceAgent()
agente_executor = ExecutorAgent()

# Processar consulta
consulta = "Quais são os cadastros ativos registrados no último mês?"
resultado_analise = agente_inteligencia.process_query(consulta)

# Executar consulta
resultado_execucao = agente_executor.execute_query(
    resultado_analise["query_type"], 
    resultado_analise["generated_query"]
)

# Processar resultado
processador = ResultProcessor(agente_inteligencia.agent_data)
resposta = processador.process_result(
    consulta, 
    resultado_execucao["result"], 
    resultado_analise["generated_query"]
)

print(resposta)
```

## Consultas Suportadas

Exemplos de consultas que o sistema pode processar:

- "Quais são os cadastros ativos registrados no último mês?"
- "Mostre os cadastros inativos da última semana"
- "Quantos cadastros foram feitos hoje?"
- "Liste todos os cadastros com email gmail"
- "Quem são os cadastros mais recentes?"

## Requisitos

- Python 3.7+
- Google Gemini API Key (para uso dos modelos Gemini)

## Instalação

1. Clone o repositório
2. Instale as dependências: `pip install -r requirements.txt`
3. Copie o arquivo `.env.example` para `.env` e configure sua API key do Gemini
4. Execute o exemplo: `python exemplo_uso.py`

## Configurações Personalizadas

Para personalizar o comportamento do sistema, edite os seguintes arquivos:

- `config.py`: Configurações gerais, incluindo parâmetros do modelo Gemini
- `data/schemas/queries.json`: Instruções para geração de consultas SQL

## Status do Projeto

Este projeto está em desenvolvimento ativo. Funcionalidades futuras incluem:

- Suporte a mais tipos de consultas complexas
- Integração com diferentes bancos de dados
- Interface web para interação direta 