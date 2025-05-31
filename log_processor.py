"""
Este arquivo contém classes e funções para processamento de logs de tagueamento.
Responsabilidades:
- Processamento e estruturação de logs capturados
- Conversão de logs para formato CSV
- Agrupamento de logs por funcionalidade
- Filtros e manipulação de dados de logs

Esta classe é central para a análise e processamento dos eventos de tagueamento
capturados de diversas fontes, incluindo dispositivos Android.
"""

import json
import re
import csv
from io import StringIO

class LogProcessor:
    """
    Responsável pelo processamento e manipulação de logs de tagueamento.
    """

    def process_logs_to_csv(self, logs):
        """
        Converte logs de tagueamento para formato CSV estruturado.

        Args:
            logs (list): Lista de strings contendo os logs capturados
            
        Returns:
            str: Conteúdo CSV formatado pronto para ser salvo em arquivo
        """
        # Cabeçalho do CSV
        header_fields = [
            "NOME DO EVENTO", "AMBIENTE", "PRODUTO", "FUNCIONALIDADE", "SUBFUNCIONALIDADE",
            "CATEGORIA", "TELA", "ACAO", "ELEMENTO", "ROTULO", "USER_ID", "TIPO_USUARIO",
            "OPCAO_SELECIONADA_1", "OPCAO_SELECIONADA_2", "OPCAO_SELECIONADA_3",
            "OPCAO_SELECIONADA_4", "OPCAO_SELECIONADA_5", "OPCAO_SELECIONADA_6"
        ]

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(header_fields)

        for log in logs:
            try:
                # Verifica se o log contém methodData
                method_data_match = re.search(r'methodData:\s*(\{.*\})', log)
                if method_data_match:
                    method_data_str = method_data_match.group(1)

                    # Tenta carregar os dados do método
                    try:
                        method_data = json.loads(method_data_str)

                        # Extrai os campos necessários do JSON
                        nome_evento = method_data.get("name", "")
                        params = method_data.get("params", {})
                        
                        # Adicionando a extração dos campos necessários
                        user_id = params.get("userId", "")
                        tipo_usuario = params.get("tipo_usuario", "")
                        
                        # Monta a linha do CSV
                        row = [
                            nome_evento,
                            params.get("ambiente", ""),
                            params.get("produto", ""),
                            params.get("funcionalidade", ""),
                            params.get("subFuncionalidade", ""),
                            "",  # SUBFUNCIONALIDADE
                            params.get("categoria", ""),
                            params.get("tela", ""),
                            params.get("acao", ""),
                            params.get("elemento", ""),
                            params.get("rotulo", ""),
                            user_id,  # USER_ID
                            tipo_usuario,  # TIPO_USUARIO
                            params.get("opcao1", ""),  # OPCAO_SELECIONADA_1
                            params.get("opcao2", ""),  # OPCAO_SELECIONADA_2
                            params.get("opcao3", ""),  # OPCAO_SELECIONADA_3
                            params.get("opcao4", ""),  # OPCAO_SELECIONADA_4
                            params.get("opcao5", ""),  # OPCAO_SELECIONADA_5
                            params.get("opcao6", ""),  # OPCAO_SELECIONADA_6
                        ]

                        writer.writerow(row)

                    except json.JSONDecodeError:
                        print(f"Erro ao decifrar JSON: {method_data_str}")
            except Exception as e:
                print(f"Erro ao processar log: {str(e)}")

        return output.getvalue()

    def group_logs_by_functionality(self, logs):
        """
        Agrupa logs por funcionalidade para organizar a exportação.

        Args:
            logs (list): Lista de strings contendo os logs capturados
            
        Returns:
            dict: Dicionário com funcionalidades como chaves e listas de logs como valores
        """
        logs_by_functionality = {}

        for log in logs:
            try:
                # Verifica se o log contém methodData
                method_data_match = re.search(r'methodData:\s*(\{.*\})', log)
                if method_data_match:
                    method_data_str = method_data_match.group(1)
                    
                    # Tenta carregar os dados do método
                    try:
                        method_data = json.loads(method_data_str)
                        params = method_data.get("params", {})
                        
                        # Pega a funcionalidade do próprio log
                        functionality = params.get("funcionalidade", "sem_funcionalidade")
                        
                        # Adiciona o log à lista da respectiva funcionalidade
                        if functionality not in logs_by_functionality:
                            logs_by_functionality[functionality] = []
                        logs_by_functionality[functionality].append(log)
                    except json.JSONDecodeError:
                        # Se não conseguir decodificar o JSON, coloca no grupo sem_funcionalidade
                        if "sem_funcionalidade" not in logs_by_functionality:
                            logs_by_functionality["sem_funcionalidade"] = []
                        logs_by_functionality["sem_funcionalidade"].append(log)
            except Exception as e:
                print(f"Erro ao processar log: {str(e)}")
                # Também coloca no grupo sem_funcionalidade em caso de erro
                if "sem_funcionalidade" not in logs_by_functionality:
                    logs_by_functionality["sem_funcionalidade"] = []
                logs_by_functionality["sem_funcionalidade"].append(log)

        return logs_by_functionality
    
    def format_logs_for_csv(self, logs):
        """
        Alias para process_logs_to_csv para compatibilidade com FileHelper.
        
        Args:
            logs (list): Lista de logs para processar
            
        Returns:
            list: Dados formatados para CSV como lista de listas
        """
        # Converte o resultado de process_logs_to_csv para o formato esperado pelo FileHelper
        csv_string = self.process_logs_to_csv(logs)
        
        # Como process_logs_to_csv retorna uma string CSV, precisamos convertê-la para o formato
        # esperado pelo método save_csv do FileHelper, que provavelmente espera uma lista de listas
        csv_reader = csv.reader(StringIO(csv_string))
        return list(csv_reader)  # Converte o leitor CSV para lista de listas