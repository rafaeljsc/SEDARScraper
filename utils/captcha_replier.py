# IMPORTAÇÕES PADRÃO
import os
import logging
from typing import Optional

# IMPORTAÇÕES DO LANGCHAIN E AZURE OPENAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from pathlib import Path

# Obtém o caminho da pasta onde o script atual está
env_path = Path(__file__).parent.parent / ".env"

# Carrega especificando o caminho
load_dotenv(dotenv_path=env_path)

# CONFIGURAÇÃO DE LOGGER
logger = logging.getLogger(__name__)

class CaptchaResponse(BaseModel):
    answer: str = Field(description="A resposta curta para a pergunta do captcha")

class AzureLLM():
    
    # FUNÇÃO RESPONSÁVEL POR CONFIGURAR O MODELO E RETORNAR UMA CADEIA ESTRUTURADA
    def setup_structured_output_model(
            self,
            output_schema: type[BaseModel],
            system_prompt: Optional[str] = None,
            model_name: str = "gpt-4o",
            max_tokens: int = os.getenv('DEFAULT_LLM_MAX_TOKENS'),
            temperature: float = os.getenv('LLM_TEMPERATURE'),
            azure_deployment_name: Optional[str] = os.getenv('AZURE_GPT_PREMIUM_DEPLOYMENT_NAME'),
            azure_endpoint: Optional[str] = os.getenv('AZURE_OPENAI_ENDPOINT'),
            api_version: Optional[str] = os.getenv('AZURE_OPENAI_API_VERSION'),
        ):
            """
            CONFIGURA MODELO AZURE OPENAI COM PARSER JSON BASEADO EM SCHEMA Pydantic
            """

            # INICIALIZA O MODELO
            model = AzureChatOpenAI(
                model_name=model_name,
                deployment_name=azure_deployment_name,
                azure_endpoint=azure_endpoint,
                api_version=api_version,
                max_tokens=max_tokens,
                temperature=temperature,
            ).with_config({"run_name": "__ignore"})

            # CRIA PARSER JSON
            parser = JsonOutputParser(pydantic_object=output_schema)

            # DEFINE TEMPLATE DE PROMPT
            prompt = PromptTemplate(
                template=f"{system_prompt}.\n" + "{format_instructions}\n{query}\n",
                input_variables=["query"],
                partial_variables={"format_instructions": parser.get_format_instructions()},
            )

            return prompt | model | parser

    def captcha_replier(self, txt: dict) -> dict:
        """
        Interage com o captcha para liberação do acesso à página
        """
        
        captcha_chain = self.setup_structured_output_model(
            temperature=0,
            output_schema=CaptchaResponse,
            system_prompt="Você é um assistente que responde perguntas genéricas apenas com 'sim' ou 'não'.",
        )
        
        try:
            result = captcha_chain.invoke({"query": txt})
            return result.get("answer","")
        except:  # noqa: E722
            return ""