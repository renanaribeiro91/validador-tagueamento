"""
TagValidator - Uma ferramenta para validar e comparar tags de eventos entre planilhas e logs.
Este módulo fornece funcionalidades para carregar, comparar, analisar e gerar relatórios de validação de tags.
"""

import csv
import json
import os
import sys
import shutil
from collections import Counter
from ai_analyzer import AIAnalyzer

# Constantes
API_KEY = ""  # Substitua pela sua chave da Flow AI
KEY_FIELDS = [
    "NOME DO EVENTO", "AMBIENTE", "PRODUTO", "FUNCIONALIDADE", "SUBFUNCIONALIDADE",
    "CATEGORIA", "TELA", "ACAO", "ELEMENTO", "ROTULO", "USER_ID", "TIPO_USUARIO",
    "OPCAO_SELECIONADA_1", "OPCAO_SELECIONADA_2", "OPCAO_SELECIONADA_3",
    "OPCAO_SELECIONADA_4", "OPCAO_SELECIONADA_5", "OPCAO_SELECIONADA_6"
]

# Funções utilitárias
def get_resource_path(relative_path):
    """
    Obtém o caminho absoluto para um recurso, funcionando tanto em desenvolvimento quanto no PyInstaller
    
    Args:
        relative_path: Caminho relativo para o recurso
        
    Returns:
        String contendo o caminho absoluto para o recurso
    """
    try:
        # PyInstaller cria uma pasta temporária e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)


class FileHandler:
    """Manipula operações de arquivo para carregar e salvar dados"""
    
    @staticmethod
    def find_header_line(file_path):
        """
        Encontra a linha contendo os campos de cabeçalho necessários em um arquivo CSV
        
        Args:
            file_path: Caminho para o arquivo CSV
            
        Returns:
            Índice da linha onde os cabeçalhos são encontrados
            
        Raises:
            ValueError: Se os cabeçalhos não forem encontrados
        """
        with open(file_path, newline='', encoding='utf-8') as f:
            for idx, line in enumerate(csv.reader(f)):
                if set(KEY_FIELDS).issubset(set(line)):
                    return idx
            raise ValueError("Cabeçalho com colunas obrigatórias não encontrado.")

    @staticmethod
    def load_events_from_csv(file_path):
        """
        Carrega eventos de um arquivo CSV
        
        Args:
            file_path: Caminho para o arquivo CSV
            
        Returns:
            Lista de dicionários contendo dados de eventos
        """
        events = []
        with open(file_path, newline='', encoding='utf-8') as f:
            header_line = FileHandler.find_header_line(file_path)
            f.seek(0)
            for _ in range(header_line):
                next(f)
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, 1):
                row['ID'] = i
                events.append(row)
        return events
    
    @staticmethod
    def save_json(file_path, data):
        """
        Salva dados como JSON no caminho especificado
        
        Args:
            file_path: Caminho para salvar o arquivo JSON
            data: Dados a serem salvos como JSON
        """
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def save_text(file_path, text_content):
        """
        Salva conteúdo de texto no caminho especificado
        
        Args:
            file_path: Caminho para salvar o arquivo de texto
            text_content: Conteúdo a ser salvo
        """
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text_content)
            
    @staticmethod
    def create_directory(directory_path):
        """
        Cria diretório se não existir
        
        Args:
            directory_path: Caminho a ser criado
        """
        os.makedirs(directory_path, exist_ok=True)
        
    @staticmethod
    def copy_file(source, destination):
        """
        Copia um arquivo da origem para o destino
        
        Args:
            source: Caminho do arquivo de origem
            destination: Caminho do arquivo de destino
        """
        if os.path.exists(source):
            shutil.copy2(source, destination)


class EventComparator:
    """Compara eventos entre dados de planilha e dados de log"""
    
    @staticmethod
    def normalize_event(event):
        """
        Normaliza valores de eventos para comparação
        
        Args:
            event: Dicionário de evento para normalizar
            
        Returns:
            Dicionário de evento normalizado
        """
        return {k: str(v).strip() if v is not None else "" for k, v in event.items()}

    def compare(self, spreadsheet_events, log_events):
        """
        Compara eventos entre planilha e log
        
        Args:
            spreadsheet_events: Lista de eventos da planilha
            log_events: Lista de eventos dos logs
            
        Returns:
            Tupla contendo listas de (ausentes, propriedades_erradas, corretos)
        """
        missing = []
        wrong_properties = []
        correct = []
        normalized_logs = [self.normalize_event(e) for e in log_events]

        for event in spreadsheet_events:
            normalized_event = self.normalize_event(event)
            target_id = event.get("ID")

            # Tenta encontrar evento correspondente por ID
            match = next((e for e in normalized_logs if e.get("ID") == str(target_id)), None)

            # Se não encontrar correspondência por ID, tenta corresponder por todos os campos-chave
            if not match:
                match = next(
                    (e for e in normalized_logs if all(
                        normalized_event.get(field, "") == e.get(field, "") for field in KEY_FIELDS)),
                    None
                )

            if not match:
                missing.append(event)
                continue

            # Encontra diferenças em campos-chave
            diffs = {}
            for field in KEY_FIELDS:
                expected = normalized_event.get(field, "")
                found = match.get(field, "")
                if expected != found:
                    diffs[field] = {
                        "esperado": expected if expected else "[não definido]",
                        "log": found if found else "[não definido]"
                    }

            if diffs:
                wrong_properties.append({
                    "ID": event["ID"],
                    "evento": event,
                    "log": match,
                    "diferencas": diffs
                })
            else:
                correct.append(event)

        return missing, wrong_properties, correct

    @staticmethod
    def count_errors_by_field(wrong_properties):
        """
        Conta erros por tipo de campo
        
        Args:
            wrong_properties: Lista de eventos com propriedades erradas
            
        Returns:
            Dicionário com contagem de erros por nome de campo
        """
        all_fields = []
        for error in wrong_properties:
            all_fields.extend(error["diferencas"].keys())
        return dict(Counter(all_fields))


class ReportGenerator:
    """Gera relatórios em vários formatos a partir dos resultados da validação"""
    
    def __init__(self, output_dir):
        """
        Inicializa com diretório de saída
        
        Args:
            output_dir: Diretório onde os relatórios serão salvos
        """
        self.output_dir = output_dir
        self.file_handler = FileHandler()

    def generate_dashboard(self, data, template_path, output_path):
        """
        Gera dashboard HTML
        
        Args:
            data: Dados para o dashboard
            template_path: Caminho para o template HTML
            output_path: Caminho para salvar o dashboard
            
        Returns:
            None
        """
        with open(template_path, encoding="utf-8") as f:
            template_content = f.read()
            
        # Substitui placeholder por script que define variável global
        script_data = f"<script>window.__DADOS_DASHBOARD__ = {json.dumps(data, ensure_ascii=False)};</script>"
        html = template_content.replace("__DADOS_DASHBOARD__", script_data)
        
        # Corrige referências de assets - copia arquivos CSS e JS para o diretório de saída
        css_source = get_resource_path("template_dashboard.css")
        js_source = get_resource_path("dashboard.js")
        utils_js_source = get_resource_path("dashboard-utils.js")
        
        # Copia arquivos se existirem
        self.file_handler.copy_file(css_source, os.path.join(self.output_dir, "template_dashboard.css"))
        self.file_handler.copy_file(utils_js_source, os.path.join(self.output_dir, "dashboard-utils.js"))
        self.file_handler.copy_file(js_source, os.path.join(self.output_dir, "dashboard.js"))
        
        # Garante que o HTML tenha caminhos relativos, não caminhos absolutos
        html = html.replace('href="/template_dashboard.css"', 'href="template_dashboard.css"')
        html = html.replace('src="/dashboard-utils.js"', 'src="dashboard-utils.js"')
        html = html.replace('src="/dashboard.js"', 'src="dashboard.js"')
        
        # Escreve o HTML final
        self.file_handler.save_text(output_path, html)

    def generate_text_report(self, spreadsheet_events, missing, wrong_properties, correct, ai_analysis):
        """
        Gera relatório de validação detalhado e profissional
        
        Args:
            spreadsheet_events: Lista de eventos da planilha
            missing: Lista de eventos ausentes
            wrong_properties: Lista de eventos com propriedades erradas
            correct: Lista de eventos corretos
            ai_analysis: Análise gerada pela IA
                
        Returns:
            Caminho para o relatório gerado
        """
        from datetime import datetime
        current_date = datetime.now().strftime("%d/%m/%Y")
        current_time = datetime.now().strftime("%H:%M:%S")
        
        report_path = os.path.join(self.output_dir, "relatorio_validacao.txt")
        
        report_content = "\n# 📊 RELATÓRIO DE VALIDAÇÃO DE EVENTOS - ANÁLISE TÉCNICA\n\n"
        report_content += f"Data de execução: {current_date} às {current_time}\n"
        report_content += "==================================================\n\n"
        
        # Sumário Executivo
        report_content += "## 📈 SUMÁRIO EXECUTIVO\n"
        report_content += "==================================================\n"
        total = len(spreadsheet_events)
        correct_percent = (len(correct) / total * 100) if total > 0 else 0
        report_content += f"✅ Total de Eventos Corretos: {len(correct)} ({correct_percent:.1f}%)\n"
        report_content += f"❌ Total de Eventos Ausentes: {len(missing)} ({(len(missing) / total * 100):.1f}% se aplicável)\n"
        report_content += f"⚠️ Total com Propriedades Erradas: {len(wrong_properties)} ({(len(wrong_properties) / total * 100):.1f}% se aplicável)\n"
        report_content += f"🧾 Total Processado: {total} eventos\n\n"

        # Detalhamento dos eventos ausentes
        report_content += "## 📉 DETALHAMENTO DOS EVENTOS AUSENTES\n"
        report_content += "==================================================\n"
        if missing:
            for i, evento in enumerate(missing, 1):
                nome_evento = evento.get('NOME DO EVENTO', '[sem nome]')
                tela = evento.get('TELA', '[sem tela]')
                report_content += f"### Evento Ausente #{i}\n"
                report_content += f"- **ID:** {evento['ID']}\n"
                report_content += f"- **Tela:** {tela}\n"
                report_content += f"- **Evento:** {nome_evento}\n"
                # Adicionar detalhes adicionais do evento que estava faltando
                for key, value in evento.items():
                    if key not in ['ID', 'TELA', 'NOME DO EVENTO']:
                        report_content += f"- **{key}:** {value}\n"
                report_content += "\n"
        else:
            report_content += "Nenhum evento ausente detectado na verificação atual."

        # Detalhamento dos eventos com propriedades incorretas
        report_content += "## ⚠️ DETALHAMENTO DOS EVENTOS COM PROPRIEDADES INCORRETAS\n"
        report_content += "==================================================\n"
        if wrong_properties:
            for i, erro in enumerate(wrong_properties, 1):
                nome_evento = erro['evento'].get('NOME DO EVENTO', '[sem nome]')
                tela = erro['evento'].get('TELA', '[sem tela]')
                report_content += f"### Evento #{i} com Propriedades Incorretas\n"
                report_content += f"- **ID:** {erro['ID']}\n"
                report_content += f"- **Tela:** {tela}\n"
                report_content += f"- **Evento:** {nome_evento}\n"
                report_content += "#### Discrepâncias Detectadas:\n"
                for campo, diferenca in erro['diferencas'].items():
                    report_content += f"{campo}:\n"
                    report_content += f"- Esperado: {diferenca['esperado']}\n"
                    report_content += f"+ Registrado: {diferenca['log']}\n"
        else:
            report_content += "```\nNenhum erro de propriedades detectado na verificação atual.\n```\n\n"
        
        # Análise Geral detalhada e técnica
        report_content += "## 🔍 ANÁLISE TÉCNICA DETALHADA\n"
        report_content += "==================================================\n"
        if ai_analysis:
            report_content += f"{ai_analysis}\n"
        else:
            # Gerar análise básica mesmo sem IA
            report_content += "### Síntese da Validação\n"
            if len(correct) == total:
                report_content += "✅ **Resultado da Validação:** APROVADO\n\n"
                report_content += "Todos os eventos foram implementados corretamente conforme as especificações.\n"
            else:
                if len(missing) > 0 and len(wrong_properties) > 0:
                    report_content += "❌ **Resultado da Validação:** REPROVADO\n\n"
                    report_content += f"Foram encontrados {len(missing)} eventos ausentes e {len(wrong_properties)} eventos com propriedades incorretas.\n"
                elif len(missing) > 0:
                    report_content += "❌ **Resultado da Validação:** REPROVADO\n\n" 
                    report_content += f"Foram encontrados {len(missing)} eventos ausentes.\n"
                elif len(wrong_properties) > 0:
                    report_content += "⚠️ **Resultado da Validação:** REQUER ATENÇÃO\n\n"
                    report_content += f"Foram encontrados {len(wrong_properties)} eventos com propriedades incorretas.\n"
            
            report_content += "\n### Recomendações Técnicas\n"
            if len(missing) > 0:
                report_content += "1. **Para eventos ausentes:**\n"
                report_content += "   - Verificar se os elementos existem no DOM da página\n"
                report_content += "   - Confirmar a implementação dos gatilhos de eventos\n"
                report_content += "   - Revisar as condições que ativam o disparo dos eventos\n"
            if len(wrong_properties) > 0:
                report_content += "2. **Para propriedades incorretas:**\n"
                report_content += "   - Padronizar a nomenclatura dos campos conforme especificação\n"
                report_content += "   - Revisar o mapeamento de dados entre a interface e o rastreamento\n"
                report_content += "   - Implementar validações de formato nos campos críticos\n"

        # Conclusão do relatório
        report_content += "\n## 📋 CONCLUSÃO\n"
        report_content += "==================================================\n"
        if len(correct) == total:
            report_content += "✅ **VALIDAÇÃO APROVADA**\n\n"
            report_content += "O processo de validação foi concluído com sucesso. Todos os eventos estão implementados corretamente.\n"
        elif len(correct) / total >= 0.9:
            report_content += "⚠️ **VALIDAÇÃO COM RESSALVAS**\n\n"
            report_content += f"O processo de validação identificou {len(missing) + len(wrong_properties)} problemas que precisam de atenção, mas a implementação está majoritariamente correta ({correct_percent:.1f}%).\n"
        else:
            report_content += "❌ **VALIDAÇÃO REPROVADA**\n\n"
            report_content += f"Foram identificados problemas significativos na implementação. Apenas {correct_percent:.1f}% dos eventos estão corretos.\n"
        
        # Assinatura e metadados
        report_content += "\n==================================================\n"
        report_content += "Relatório gerado automaticamente pelo Sistema de Validação de Eventos\n"
        report_content += f"Versão: 1.0.2 | Data: {current_date} | Hora: {current_time}\n"
        
        self.file_handler.save_text(report_path, report_content)
        return report_path

    def generate_all_reports(self, spreadsheet_events, missing, wrong_properties, correct, ai_analysis):
        """
        Gera todos os relatórios (JSON, texto, dados do dashboard)
        
        Args:
            spreadsheet_events: Lista de eventos da planilha
            missing: Lista de eventos ausentes
            wrong_properties: Lista de eventos com propriedades erradas
            correct: Lista de eventos corretos
            ai_analysis: Análise gerada pela IA
            
        Returns:
            Dicionário com dados do dashboard
        """
        # Cria relatórios JSON
        self.file_handler.save_json(
            os.path.join(self.output_dir, "ausentes_log.json"),
            {"total_ausentes": len(missing), "eventos": missing}
        )

        self.file_handler.save_json(
            os.path.join(self.output_dir, "propriedades_erradas.json"),
            {"total_com_erro": len(wrong_properties), "eventos": wrong_properties}
        )

        # Cria relatório de texto
        self.generate_text_report(spreadsheet_events, missing, wrong_properties, correct, ai_analysis)

        # Conta eventos por tela
        eventos_por_tela = {}
        for event in spreadsheet_events:
            tela = event.get('TELA', '[Tela não especificada]')
            eventos_por_tela[tela] = eventos_por_tela.get(tela, 0) + 1

        # Formata eventos ausentes para o dashboard
        formatted_missing = []
        for evento in missing:
            formatted_missing.append({
                "ID": evento.get("ID", "N/A"),
                "evento": evento,  # Inclui os dados completos do evento
                "NOME_DO_EVENTO": evento.get("NOME DO EVENTO", "[sem nome]"),
                "TELA": evento.get("TELA", "[sem tela]"),
                "FUNCIONALIDADE": evento.get("FUNCIONALIDADE", "[sem funcionalidade]")
            })

        # Retorna dados do dashboard
        return {
            "resumo": {
                "corretos": len(correct),
                "ausentes": len(missing),
                "com_erro": len(wrong_properties),
                "total": len(spreadsheet_events)
            },
            "erros_por_campo": EventComparator.count_errors_by_field(wrong_properties),
            "eventos_por_tela": eventos_por_tela, 
            "eventos": {
                "corretos": correct,
                "ausentes": formatted_missing,
                "com_erro": wrong_properties
            },
            "analise_ia": ai_analysis
        }


class DirectoryManager:
    """Gerencia criação de diretórios e resolução de caminhos"""
    
    def __init__(self):
        """Inicializa com diretório do projeto"""
        self.project_dir = os.path.dirname(get_resource_path(__file__))
        
    def create_output_directory(self, base_dir, functionality, subfunctionality=None, use_prefix=True):
        """
        Cria um diretório de saída organizado por funcionalidade e subfuncionalidade
        
        Args:
            base_dir: Diretório base
            functionality: Nome da funcionalidade
            subfunctionality: Nome da subfuncionalidade, se disponível
            use_prefix: Se True, adiciona "relatorio-validacoes/eventos" ao caminho
            
        Returns:
            Caminho para o diretório de saída criado
        """
        # Sanitiza os nomes
        functionality_name = self.sanitize_functionality_name(functionality)
        
        if use_prefix:
            # Estrutura com prefixo: relatorio-validacoes/eventos/nome_da_funcionalidade[/nome_da_subfuncionalidade]
            prefix_path = os.path.join("relatorio-validacoes", "eventos")
        else:
            # Estrutura sem prefixo: nome_da_funcionalidade[/nome_da_subfuncionalidade]
            prefix_path = ""
        
        # Montar caminho completo
        if subfunctionality and subfunctionality.strip():
            subfunctionality_name = self.sanitize_functionality_name(subfunctionality)
            if prefix_path:
                output_dir = os.path.join(base_dir, prefix_path, functionality_name, subfunctionality_name)
            else:
                output_dir = os.path.join(base_dir, functionality_name, subfunctionality_name)
        else:
            if prefix_path:
                output_dir = os.path.join(base_dir, prefix_path, functionality_name)
            else:
                output_dir = os.path.join(base_dir, functionality_name)
            
        FileHandler.create_directory(output_dir)
        return output_dir

    @staticmethod
    def sanitize_functionality_name(name):
        """
        Sanitiza nome de funcionalidade para uso em caminhos de diretório
        
        Args:
            name: Nome da funcionalidade para sanitizar
            
        Returns:
            Nome sanitizado
        """
        if not name:
            return "default_funcionalidade"
            
        sanitized = ''.join(c for c in name if c.isalnum() or c in ' _-')
        return sanitized.strip().replace(' ', '_')


class TagValidator:
    """Classe principal para validação de tags entre dados de planilha e de log"""
    
    def __init__(self):
        """Inicializa componentes"""
        self.directory_manager = DirectoryManager()
        self.file_handler = FileHandler()
        self.comparator = EventComparator()
        self.ai_analyzer = AIAnalyzer(api_key=API_KEY)
        
    def process_files(self, spreadsheet_path, log_path, get_output_directory_func=None):
        """
        Processa arquivos CSV e gera relatórios
        
        Args:
            spreadsheet_path: Caminho para planilha CSV
            log_path: Caminho para log CSV
            get_output_directory_func: Função de callback para obter diretório de saída (opcional)
                
        Returns:
            Tupla contendo (funcionalidade, output_dir, dashboard_data, dashboard_path)
        """
        # Carrega eventos
        spreadsheet_events = self.file_handler.load_events_from_csv(spreadsheet_path)
        log_events = self.file_handler.load_events_from_csv(log_path)
        
        # Extrai nome da funcionalidade e subfuncionalidade para nomear pasta
        functionality = "default_funcionalidade"
        subfunctionality = None
        if spreadsheet_events:
            norm_event = self.comparator.normalize_event(spreadsheet_events[0])
            functionality = norm_event.get("FUNCIONALIDADE", "default_funcionalidade")
            # Verifica se tem SUBFUNCIONALIDADE
            subfunctionality = norm_event.get("SUBFUNCIONALIDADE", "")
            
        # Compara eventos
        missing, wrong_properties, correct = self.comparator.compare(spreadsheet_events, log_events)
        
        # Obtém análise abrangente da IA
        ai_analysis = self.ai_analyzer.generate_comprehensive_analysis(
            missing, 
            wrong_properties, 
            correct,
            len(spreadsheet_events)
        )
        
        # Salva no diretório do projeto (com prefixo padrão)
        project_output_dir = self.directory_manager.create_output_directory(
            self.directory_manager.project_dir, 
            functionality,
            subfunctionality,
            use_prefix=True  # use o prefixo padrão para o diretório do projeto
        )
        
        # Sempre gera relatórios no diretório do projeto
        project_dashboard_data = self._generate_reports_in_directory(
            project_output_dir, 
            spreadsheet_events, 
            missing, 
            wrong_properties, 
            correct, 
            ai_analysis
        )
        
        # Determina o nome do diretório para exibição ao usuário
        display_directory_name = f"{functionality}/{subfunctionality}" if subfunctionality else functionality
        
        # Verifica se a função para obter diretório do usuário foi fornecida
        if get_output_directory_func is not None:
            try:
                # Obtém diretório base selecionado pelo usuário
                user_base_dir = get_output_directory_func(display_directory_name)
                
                # Se o usuário cancelou a seleção, retorna apenas os dados do diretório do projeto
                if not user_base_dir:
                    return display_directory_name, project_output_dir, project_dashboard_data, os.path.join(project_output_dir, "dashboard.html")
                
                # Cria estrutura no diretório escolhido pelo usuário
                user_output_dir = self.directory_manager.create_output_directory(
                    user_base_dir, 
                    functionality,
                    subfunctionality,
                    use_prefix=False  # não use o prefixo para o diretório escolhido pelo usuário
                )
                
                # Gera relatórios no diretório do usuário
                user_dashboard_data = self._generate_reports_in_directory(
                    user_output_dir, 
                    spreadsheet_events, 
                    missing, 
                    wrong_properties, 
                    correct, 
                    ai_analysis
                )
                
                # Retorna valores para o diretório do usuário
                return display_directory_name, user_output_dir, user_dashboard_data, os.path.join(user_output_dir, "dashboard.html")
            
            except Exception as e:
                print(f"Erro ao salvar no diretório do usuário: {str(e)}")
                # Em caso de falha, retorna os dados do diretório do projeto
                pass
        
        # Se não há função para obter diretório ou se ocorreu erro, 
        # retorna apenas os dados do diretório do projeto
        return display_directory_name, project_output_dir, project_dashboard_data, os.path.join(project_output_dir, "dashboard.html")
        
    def _generate_reports_in_directory(self, output_dir, spreadsheet_events, missing, wrong_properties, correct, ai_analysis):
        """
        Gera todos os relatórios em um diretório específico
        
        Args:
            output_dir: Diretório de saída
            spreadsheet_events: Lista de eventos da planilha
            missing: Lista de eventos ausentes
            wrong_properties: Lista de eventos com propriedades erradas
            correct: Lista de eventos corretos
            ai_analysis: Análise gerada pela IA
            
        Returns:
            Dicionário com dados do dashboard
        """
        # Cria o diretório se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        # Gera relatórios
        report_generator = ReportGenerator(output_dir)
        dashboard_data = report_generator.generate_all_reports(
            spreadsheet_events, missing, wrong_properties, correct, ai_analysis
        )
        
        # Gera dashboard
        template_dashboard = get_resource_path("template_dashboard.html")
        dashboard_output = os.path.join(output_dir, "dashboard.html")
        report_generator.generate_dashboard(dashboard_data, template_dashboard, dashboard_output)
        
        return dashboard_data