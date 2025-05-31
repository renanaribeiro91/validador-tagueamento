"""
Este arquivo contém utilidades para manipulação de arquivos e diretórios.
Responsabilidades:
- Criação e verificação de diretórios
- Salvamento de logs em arquivos
- Organização de arquivos por funcionalidade

Estas funções são usadas para persistir os logs capturados dos dispositivos
e organizar a estrutura de diretórios para armazenamento dos dados.
"""

from datetime import datetime
import os

class FileHelper:
    """
    Utilitário para operações com arquivos e diretórios.
    """

    @staticmethod
    def ensure_directory_exists(directory_path):
        """
        Garante que um diretório exista, criando-o se necessário.

        Args:
            directory_path (str): Caminho do diretório a ser verificado/criado
        """
        os.makedirs(directory_path, exist_ok=True)

    @staticmethod
    def sanitize_name(name):
        """
        Sanitiza nome para uso em caminhos de diretório.
        
        Args:
            name (str): Nome para sanitizar
            
        Returns:
            str: Nome sanitizado
        """
        if not name:
            return "default_funcionalidade"
            
        sanitized = ''.join(c for c in name if c.isalnum() or c in ' _-')
        return sanitized.strip().replace(' ', '_')

    @staticmethod
    def create_functionality_directory(base_dir, functionality, subfunctionality=None):
        """
        Cria diretório seguindo o padrão: relatorio-validacoes/eventos/nome_da_funcionalidade/[nome_da_subfuncionalidade]
        
        Args:
            base_dir (str): Diretório base
            functionality (str): Nome da funcionalidade
            subfunctionality (str, optional): Nome da subfuncionalidade
            
        Returns:
            str: Caminho do diretório criado
        """
        functionality_name = FileHelper.sanitize_name(functionality)
        
        if subfunctionality and subfunctionality.strip():
            subfunctionality_name = FileHelper.sanitize_name(subfunctionality)
            output_dir = os.path.join(
                base_dir, 
                "relatorio-validacoes", 
                "eventos", 
                functionality_name, 
                subfunctionality_name
            )
        else:
            output_dir = os.path.join(
                base_dir, 
                "relatorio-validacoes", 
                "eventos", 
                functionality_name
            )
            
        FileHelper.ensure_directory_exists(output_dir)
        return output_dir

    @staticmethod
    def save_logs_to_directory(logs_by_functionality, base_dir, log_processor):
        """
        Salva logs em arquivos CSV organizados por funcionalidade e subfuncionalidade.
        
        Args:
            logs_by_functionality: Dicionário de logs agrupados
            base_dir: Diretório base onde salvar
            log_processor: Processador de logs para formatação
            
        Returns:
            Lista de caminhos de arquivos salvos
        """
        saved_files = []
        
        for functionality, data in logs_by_functionality.items():
            if not functionality or functionality.lower() == "undefined":
                functionality = "sem_funcionalidade"
            
            # Sanitiza o nome da funcionalidade
            safe_functionality = FileHelper.sanitize_name(functionality)
            
            # Verifica se temos subfuncionalidades agrupadas
            if isinstance(data, dict) and "logs" not in data:
                # Caso com subfuncionalidades
                for subfunc, subfunc_data in data.items():
                    if not subfunc or subfunc.lower() == "undefined":
                        subfunc = "sem_subfuncionalidade"
                    
                    safe_subfunc = FileHelper.sanitize_name(subfunc)
                    
                    # Cria diretório para subfuncionalidade
                    func_dir = os.path.join(base_dir, safe_functionality, safe_subfunc)
                    os.makedirs(func_dir, exist_ok=True)
                    
                    # Nome do arquivo com timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{safe_functionality}_{safe_subfunc}_{timestamp}.csv"
                    filepath = os.path.join(func_dir, filename)
                    
                    # Formata e salva logs
                    formatted_logs = log_processor.format_logs_for_csv(subfunc_data["logs"])
                    FileHelper.save_csv(filepath, formatted_logs)  
                    saved_files.append(filepath)
            else:
                # Caso sem subfuncionalidade
                logs_to_save = data.get("logs", data) if isinstance(data, dict) else data
                
                # Cria diretório para funcionalidade
                func_dir = os.path.join(base_dir, safe_functionality)
                os.makedirs(func_dir, exist_ok=True)
                
                # Nome do arquivo com timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{safe_functionality}_{timestamp}.csv"
                filepath = os.path.join(func_dir, filename)
                
                # Formata e salva logs
                formatted_logs = log_processor.format_logs_for_csv(logs_to_save)
                FileHelper.save_csv(filepath, formatted_logs)  
                saved_files.append(filepath)
        
        return saved_files

    @staticmethod
    def save_csv(filepath, data):
        """
        Salva dados em formato CSV.
        
        Args:
            filepath: Caminho do arquivo
            data: Dados a serem salvos
        """
        # Implementar método para salvar dados em CSV
        # Este método precisa ser implementado também como estático
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            if data:
                # Assumindo que data é uma lista de listas ou similar
                import csv
                writer = csv.writer(f)
                writer.writerows(data)