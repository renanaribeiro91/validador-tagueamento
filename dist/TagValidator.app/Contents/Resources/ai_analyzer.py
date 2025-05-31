"""
AIAnalyzer - Módulo para análise de tags usando Flow AI
Este módulo fornece funcionalidades para analisar dados de validação usando a API Flow AI.
"""

import requests
import time

class FlowAIClient:
    """Cliente para comunicação com a API do Flow AI"""
    
    def __init__(self, client_id, client_secret, tenant, app_to_access="llm-api"):
        """
        Inicializa o cliente do Flow AI
        
        Args:
            client_id: ID do cliente para autenticação
            client_secret: Senha do cliente para autenticação
            tenant: Nome do tenant do Flow AI
            app_to_access: Aplicação a ser acessada (padrão: 'llm-api')
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant = tenant
        self.app_to_access = app_to_access
        self.token = None
        self.token_expiry = 0  # Token inicial expirado
        self.token_lifespan = 3500  # Pouco menos que 1h, em segundos

    def get_token(self):
        """
        Obtém ou renova o token de autenticação
        
        Returns:
            String contendo o token de acesso
        """
        # Verifica se o token atual ainda é válido
        if self.token and time.time() < self.token_expiry:
            return self.token
            
        # Caso contrário, solicita um novo token
        url = "https://flow.ciandt.com/auth-engine-api/v1/api-key/token"
        
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "FlowTenant": self.tenant
        }
        
        payload = {
            "clientId": self.client_id,
            "clientSecret": self.client_secret,
            "appToAccess": self.app_to_access
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()  # Levanta exceção para códigos de erro
            
            response_data = response.json()
            self.token = response_data.get("access_token")  # Corrigido para access_token
            
            if not self.token:
                raise Exception(f"Token não encontrado na resposta: {response_data}")
                
            self.token_expiry = time.time() + self.token_lifespan
            return self.token
            
        except requests.exceptions.RequestException as e:
            # Captura e relança exceções de requisição com detalhes
            if hasattr(e, 'response') and e.response:
                raise Exception(f"Falha na autenticação: {e.response.status_code} - {e.response.text}")
            else:
                raise Exception(f"Falha na conexão com o serviço de autenticação: {str(e)}")
    
    class ChatCompletions:
        """Classe interna para manter compatibilidade com a estrutura original"""
        
        def __init__(self, parent_client):
            self.parent_client = parent_client
            
        def create(self, model, messages, temperature=0, max_tokens=1500):
            """
            Cria uma resposta de chat usando a API do Flow AI
            
            Args:
                model: Modelo de linguagem a ser usado
                messages: Lista de mensagens para o chat
                temperature: Temperatura para geração (0-1)
                max_tokens: Número máximo de tokens na resposta
                
            Returns:
                Objeto compatível com a resposta OpenAI
            """
            try:
                token = self.parent_client.get_token()
                
                url = "https://flow.ciandt.com/ai-orchestration-api/v1/openai/chat/completions"
                
                headers = {
                    "FlowTenant": self.parent_client.tenant,
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "FlowAgent": "tag-validator",  # Nome do agente
                    "Authorization": f"Bearer {token}"
                }
                
                payload = {
                    "stream": False,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "model": model,
                    "temperature": temperature
                }
                
                response = requests.post(url, headers=headers, json=payload)
                response.raise_for_status()  # Levanta exceção para códigos de erro
                
                response_data = response.json()
                
                # Criando um objeto de resposta compatível com a estrutura esperada
                class ResponseStruct:
                    class ChoiceStruct:
                        class MessageStruct:
                            def __init__(self, content):
                                self.content = content
                                
                        def __init__(self, message_content):
                            self.message = self.MessageStruct(message_content)
                            
                    def __init__(self, choices_data):
                        self.choices = []
                        for choice in choices_data:
                            message_content = choice.get('message', {}).get('content', '')
                            self.choices.append(self.ChoiceStruct(message_content))
                
                return ResponseStruct(response_data.get('choices', []))
                
            except requests.exceptions.RequestException as e:
                # Captura e relança exceções de requisição com detalhes
                if hasattr(e, 'response') and e.response:
                    error_details = f"{e.response.status_code} - {e.response.text}"
                else:
                    error_details = str(e)
                    
                raise Exception(f"Erro na chamada da API: {error_details}")

class AIAnalyzer:
    """Manipula análises baseadas em IA dos resultados de validação"""
    
    def __init__(self, api_key=None):
        """
        Inicializa cliente Flow AI para análise
        
        Args:
            api_key: Parâmetro mantido por compatibilidade, mas não é usado
        """
        # Configuração específica do Flow AI
        client = FlowAIClient(
            client_id="3a785a75-3795-4f64-8345-53903f0042a4",
            client_secret="pqC8Q~uKs3HAb8qkNvGA-CfewQw03GZ4AERgdcuy",
            tenant="cit"
        )
        
        # Adiciona a classe chat.completions para manter compatibilidade com a estrutura original
        client.chat = type('ChatModule', (), {})
        client.chat.completions = client.ChatCompletions(client)
        
        self.client = client

    def suggest_corrections(self, differences):
        """
        Usa IA para analisar diferenças e sugerir correções
        
        Args:
            differences: Lista de diferenças entre dados esperados e reais
            
        Returns:
            String contendo análise e sugestões da IA
        """
        import json
        
        messages = [
            {"role": "system", "content": "Você é um especialista em sistemas de QA."},
            {"role": "user", "content": f"Analise as diferenças abaixo e explique o que pode estar errado ou mal preenchido:\n\n{json.dumps(differences, indent=2, ensure_ascii=False)}"}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Usando modelo disponível no Flow AI
                messages=messages,
                temperature=0.2,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[Erro ao consultar IA: {str(e)}]"
            
    def generate_comprehensive_analysis(self, missing, wrong_properties, correct, total_events):
        """
        Gera análise abrangente dos resultados da validação
        
        Args:
            missing: Lista de eventos ausentes
            wrong_properties: Lista de eventos com propriedades incorretas
            correct: Lista de eventos corretos
            total_events: Número total de eventos
            
        Returns:
            String contendo análise abrangente
        """
        import json
        
        # Prepara dados do resumo
        missing_ids = [event.get('ID', 'N/A') for event in missing]
        error_ids = [error.get('ID', 'N/A') for error in wrong_properties]
        
        # Coleta padrões de erro
        error_fields = {}
        for error in wrong_properties:
            for field in error.get('diferencas', {}):
                if field not in error_fields:
                    error_fields[field] = 0
                error_fields[field] += 1
        
        # Cria solicitação de análise
        analysis_request = {
            "resumo": {
                "total_eventos": total_events,
                "eventos_corretos": len(correct),
                "eventos_ausentes": len(missing),
                "eventos_com_erro": len(wrong_properties)
            },
            "ids_ausentes": missing_ids[:20],  # Limita aos primeiros 20 para brevidade
            "ids_com_erro": error_ids[:20],    # Limita aos primeiros 20 para brevidade
            "campos_com_erro": error_fields,
            "exemplos_erros": wrong_properties[:3] if wrong_properties else []  # Primeiros 3 exemplos
        }
        
        messages = [
            {"role": "system", "content": """Você é um especialista em QA especializado em análise de tags.
             Forneça análise detalhada e insights sobre os problemas encontrados."""},
            {"role": "user", "content": f"""
             Analise os resultados de validação de tags abaixo e forneça:
             
             1. Um resumo geral da situação
             2. Padrões ou problemas sistemáticos que você identificou
             3. Possíveis causas raiz para eventos ausentes
             4. Possíveis causas raiz para campos com erros
             5. Recomendações específicas para corrigir os problemas
             6. Uma conclusão sobre a qualidade geral das tags
             
             Dados de validação:
             {json.dumps(analysis_request, indent=2, ensure_ascii=False)}
             
             Importante: Sua resposta deve ser em português. Se não houver problemas, faça uma análise positiva ressaltando a boa qualidade da implementação.
             """}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Usando modelo disponível no Flow AI
                messages=messages,
                temperature=0.2,
                max_tokens=1500,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[Erro ao gerar análise abrangente: {str(e)}]"