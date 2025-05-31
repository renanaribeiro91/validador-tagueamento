"""
Este arquivo contém a interface principal da aplicação de validação de tagueamento.
Responsabilidades:

Criação e gerenciamento da interface gráfica
Fluxo de interação com o usuário
Integração com as funcionalidades de processamento de logs
Monitoramento de dispositivos e captura de eventos

É a classe principal que coordena a interação entre todas as outras partes do sistema referente a tela de execução,
incluindo dispositivos, processamento de logs e interface com o usuário.
"""

from multiprocessing import process
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import webbrowser
import time
import subprocess
from datetime import datetime

# Importando os módulos auxiliares
from devices import AdbHelper, DeviceManager, IosDeviceHelper
from log_processor import LogProcessor
from file_utils import FileHelper
from dialog_utils import DialogHelper

class ValidationApp:
    """
    Aplicação principal para validação de tagueamento.
    """

    def __init__(self, validator):
        """
        Inicializa a aplicação com um validador.
        
        Args:
            validator: Objeto responsável pela validação de tagueamento
        """
        self.validator = validator
        self.root = None
        self.monitoring_thread = None
        self.is_monitoring = False
        self.is_paused = False
        self.collected_logs = []
        self.adb_process = None
        self.ios_process = None
        self.device_data = []
        
        # Inicialização dos helpers
        self.log_processor = LogProcessor()
        self.adb_helper = AdbHelper()
        self.file_helper = FileHelper()
        self.dialog_helper = DialogHelper()

    def run(self):
        """
        Inicializa e executa a aplicação principal.
        """
        self.root = tk.Tk()
        self.root.title("Validador de Tagueamento")
        self.root.geometry("800x600")
        
        # Centraliza a janela na tela
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 800) // 2
        y = (screen_height - 600) // 2
        self.root.geometry(f"800x600+{x}+{y}")
        
        self.configure_style()
        self.setup_main_menu()
        self.root.mainloop()

    def configure_style(self):
        """
        Configura os estilos visuais da aplicação.
        """
        style = ttk.Style()
        style.configure("TButton", padding=10, font=("Arial", 12))
        style.configure("TLabel", font=("Arial", 12))
        style.configure("TFrame", padding=10)

    def setup_main_menu(self):
        """
        Configura o menu principal da aplicação.
        """
        # Limpa a janela
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Configuração do frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Título
        title_label = ttk.Label(main_frame, text="Validador de Tagueamento", 
                               font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Botões de ação
        validate_btn = ttk.Button(main_frame, text="Validar Tagueamento",
                                 command=self.open_validation_window)
        validate_btn.pack(fill="x", pady=10)
        
        monitor_btn = ttk.Button(main_frame, text="Monitorar Logs",
                                command=self.open_monitor_window)
        monitor_btn.pack(fill="x", pady=10)

    def open_validation_window(self):
        """
        Abre a janela de validação de tagueamento.
        """
        # Limpa a janela
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Configuração do frame de validação
        validation_frame = ttk.Frame(self.root)
        validation_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Título
        title_label = ttk.Label(validation_frame, text="Validação de Tagueamento", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Variáveis para os caminhos
        self.spreadsheet_path = tk.StringVar()
        self.log_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        
        # Frame para seleção de arquivos
        files_frame = ttk.Frame(validation_frame)
        files_frame.pack(fill="x", pady=10)
        
        # Configuração do grid
        files_frame.columnconfigure(0, weight=1)  # Coluna dos rótulos
        files_frame.columnconfigure(1, weight=2)  # Coluna das entradas
        files_frame.columnconfigure(2, weight=0)  # Coluna dos botões
        
        # Seleção do arquivo de planilha
        ttk.Label(files_frame, text="Planilha de eventos esperados:").grid(row=0, column=0, sticky="w", pady=5)
        entry_spreadsheet = ttk.Entry(files_frame, textvariable=self.spreadsheet_path, width=40)
        entry_spreadsheet.grid(row=0, column=1, padx=5, sticky="ew")
        
        select_spreadsheet_btn = ttk.Button(
            files_frame, text="Selecionar", 
            command=lambda: self.spreadsheet_path.set(
                filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
            )
        )
        select_spreadsheet_btn.grid(row=0, column=2, padx=(5, 0))
        
        # Seleção do arquivo de log
        ttk.Label(files_frame, text="Log de eventos coletados:").grid(row=1, column=0, sticky="w", pady=5)
        entry_log = ttk.Entry(files_frame, textvariable=self.log_path, width=40)
        entry_log.grid(row=1, column=1, padx=5, sticky="ew")
        
        select_log_btn = ttk.Button(
            files_frame, text="Selecionar", 
            command=lambda: self.log_path.set(
                filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
            )
        )
        select_log_btn.grid(row=1, column=2, padx=(5, 0))
        
        # Seleção do diretório de saída
        ttk.Label(files_frame, text="Diretório para salvar resultados:").grid(row=2, column=0, sticky="w", pady=5)
        entry_output = ttk.Entry(files_frame, textvariable=self.output_dir, width=40)
        entry_output.grid(row=2, column=1, padx=5, sticky="ew")
        
        select_output_btn = ttk.Button(
            files_frame, text="Selecionar", 
            command=lambda: self.output_dir.set(
                filedialog.askdirectory()
            )
        )
        select_output_btn.grid(row=2, column=2, padx=(5, 0))
        
        # Botões de ação
        buttons_frame = ttk.Frame(validation_frame)
        buttons_frame.pack(fill="x", pady=(20, 10))
        
        ttk.Button(buttons_frame, text="Voltar", 
                  command=self.setup_main_menu).pack(side="left", padx=5)
        
        ttk.Button(buttons_frame, text="Validar", 
                  command=self.run_validation).pack(side="right", padx=5)

    def run_validation(self):
        """
        Executa o processo de validação dos dados.
        """
        # Verificação básica
        if not self.spreadsheet_path.get() or not self.log_path.get():
            messagebox.showerror("Erro", "Selecione os arquivos de planilha e log")
            return
        
        # Mostrar indicador de progresso
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Processando")
        progress_window.geometry("300x100")
        progress_window.transient(self.root)
        progress_window.resizable(False, False)
        
        # Ensure the window is built before getting its size
        ttk.Label(progress_window, text="Validando eventos... vai ser rapidinho tá! 😉").pack(pady=10)
        progress = ttk.Progressbar(progress_window, mode="indeterminate")
        progress.pack(fill="x", padx=20)
        
        # Hide window during positioning calculations
        progress_window.withdraw()
        
        # Force geometry calculation by updating
        progress_window.update_idletasks()
        
        # Get dimensions and positions
        window_width = progress_window.winfo_reqwidth()
        window_height = progress_window.winfo_reqheight()
        
        # Center on screen (not just relative to parent)
        screen_width = progress_window.winfo_screenwidth()
        screen_height = progress_window.winfo_screenheight()
        
        position_x = (screen_width - window_width) // 2
        position_y = (screen_height - window_height) // 2
        
        # Position window and make visible
        progress_window.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")
        progress_window.deiconify()
        
        # Start the progress bar animation
        progress.start()
        
        # Define a função para obter diretório de saída
        def get_output_dir(functionality):
            if self.output_dir.get():
                # Verifica se a funcionalidade tem subfuncionalidade (formato: principal/sub)
                if "/" in functionality:
                    main_func, sub_func = functionality.split("/", 1)
                    # Cria estrutura principal/subfuncionalidade
                    output_dir = os.path.join(self.output_dir.get(), "relatorio-validações")
                else:
                    # Sem subfuncionalidade, salva diretamente na pasta da funcionalidade
                    output_dir = os.path.join(self.output_dir.get(), "relatorio-validações")
                
                os.makedirs(output_dir, exist_ok=True)
                return output_dir
            else:
                # Deixa o validator lidar com a estrutura de diretórios
                return self.validator.create_output_directory(
                    os.path.dirname(os.path.abspath(__file__)),
                    functionality
                )
        
        # Executa a validação em uma thread separada
        def validation_thread():
            try:
                functionality, output_dir, dashboard_data, dashboard_path = self.validator.process_files(
                    self.spreadsheet_path.get(),
                    self.log_path.get(),
                    get_output_dir
                )
                
                # Fecha a janela de progresso
                self.root.after(0, progress_window.destroy)
                
                # Pergunta se deseja abrir o relatório
                if messagebox.askyesno("Concluído", 
                                      f"Validação concluída com sucesso! Relatórios salvos em:\n{output_dir}\n\n"
                                      f"Deseja abrir o dashboard de resultados?"):
                    webbrowser.open(f"file://{dashboard_path}")
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro durante a validação: {str(e)}"))
                self.root.after(0, progress_window.destroy)
        
        # Inicia a thread
        threading.Thread(target=validation_thread).start()

    def open_monitor_window(self):
        """
        Abre a janela de monitoramento de logs via ADB ou iOS.
        """
        # Limpa a janela
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Configuração do frame de monitoramento
        monitor_frame = ttk.Frame(self.root)
        monitor_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Título
        title_label = ttk.Label(monitor_frame, text="Monitoramento de Logs (Android/iOS)", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Frame para seleção de dispositivo
        device_frame = ttk.Frame(monitor_frame)
        device_frame.pack(fill="x", pady=10)
        
        # Lista de dispositivos
        ttk.Label(device_frame, text="Dispositivo:").pack(side="left", padx=5)
        self.device_var = tk.StringVar()
        self.device_combo = ttk.Combobox(device_frame, textvariable=self.device_var, state="readonly")
        self.device_combo.pack(side="left", padx=5, fill="x", expand=True)
        
        # Botão para verificar dispositivos
        ttk.Button(device_frame, text="Verificar Dispositivos", 
                  command=self.check_devices).pack(side="right", padx=5)
        
        # Frame para logs
        log_frame = ttk.LabelFrame(monitor_frame, text="Logs")
        log_frame.pack(fill="both", expand=True, pady=10)
        
        # Área de texto para exibir logs
        self.log_text = tk.Text(log_frame, height=15, bg="#1e1e1e", fg="white")
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5, side="left")
        
        # Scrollbar para a área de texto
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Botões de controle
        control_frame = ttk.Frame(monitor_frame)
        control_frame.pack(fill="x", pady=(10, 5))
        
        ttk.Button(control_frame, text="Voltar", 
                  command=self.setup_main_menu).pack(side="left", padx=5)
        
        # Botões para controle do monitoramento
        self.monitoring_buttons_frame = ttk.Frame(control_frame)
        self.monitoring_buttons_frame.pack(side="right")
        
        self.save_btn = ttk.Button(self.monitoring_buttons_frame, text="Salvar Logs", 
                                  command=self.save_logs, state="disabled")
        self.save_btn.pack(side="right", padx=5)
        
        self.pause_btn = ttk.Button(self.monitoring_buttons_frame, text="Pausar", 
                                   command=self.pause_monitoring, state="disabled")
        self.pause_btn.pack(side="right", padx=5)
        
        self.start_btn = ttk.Button(self.monitoring_buttons_frame, text="Iniciar Monitoramento", 
                                   command=self.start_monitoring)
        self.start_btn.pack(side="right", padx=5)
        
        # Inicializa valores
        self.collected_logs = []
        self.is_monitoring = False
        self.is_paused = False
        
    def check_devices(self):
        """
        Verifica e lista os dispositivos Android e iOS conectados.
        """
        try:
            # Usar o DeviceManager para verificar ambos os tipos de dispositivos
            all_devices = DeviceManager.get_all_connected_devices()
            
            android_devices = all_devices['android']
            ios_devices = all_devices['ios']
            
            # Combinar dispositivos com informações da plataforma
            combined_devices = []
            
            # Adicionar dispositivos Android
            for device_id in android_devices:
                combined_devices.append({"id": device_id, "platform": "android", "display": f"Android: {device_id}"})
            
            # Adicionar dispositivos iOS
            for device_id in ios_devices:
                # Opcionalmente obter mais informações do dispositivo iOS
                try:
                    if IosDeviceHelper.verify_trust_status(device_id):
                        info = IosDeviceHelper.get_device_info(device_id)
                        device_name = info.get('name', device_id)
                        combined_devices.append({"id": device_id, "platform": "ios", "display": f"iOS: {device_name}"})
                    else:
                        combined_devices.append({"id": device_id, "platform": "ios", "display": f"iOS: {device_id} (Não confiável)"})
                except Exception:
                    combined_devices.append({"id": device_id, "platform": "ios", "display": f"iOS: {device_id}"})
            
            if combined_devices:
                # Atualiza o combobox com os dispositivos encontrados
                self.device_combo['values'] = [device["display"] for device in combined_devices]
                self.device_combo.current(0)
                
                # Armazena os dados completos dos dispositivos para uso posterior
                self.device_data = combined_devices
                
                messagebox.showinfo("Dispositivos", f"Encontrados {len(combined_devices)} dispositivos")
            else:
                messagebox.showinfo("Dispositivos", "Nenhum dispositivo encontrado")
                self.device_combo['values'] = []
                self.device_var.set("")
                self.device_data = []
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao verificar dispositivos: {str(e)}")

    def start_monitoring(self):
        """
        Inicia o monitoramento de logs do dispositivo selecionado.
        """
        if not self.device_var.get():
            messagebox.showerror("Erro", "Selecione um dispositivo")
            return
        
        self.is_monitoring = True
        self.is_paused = False
        self.log_text.delete(1.0, tk.END)
        self.collected_logs = []
        
        # Atualiza estado dos botões
        self.start_btn.config(text="Finalizar", command=self.stop_monitoring)
        self.pause_btn.config(state="normal")
        self.save_btn.config(state="disabled")
        
        # Inicia o monitoramento em uma thread separada
        self.monitoring_thread = threading.Thread(target=self.monitor_logs)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()

    def pause_monitoring(self):
        """
        Pausa ou retoma o monitoramento de logs.
        """
        if self.is_paused:
            # Retomar monitoramento
            self.is_paused = False
            self.pause_btn.config(text="Pausar")
            self.log_text.insert(tk.END, "\n[Monitoramento retomado]\n")
            self.log_text.see(tk.END)
            
            # Verifica qual plataforma está sendo usada
            selected_device_display = self.device_var.get()
            selected_platform = None
            
            for device in self.device_data:
                if device["display"] == selected_device_display:
                    selected_platform = device["platform"]
                    device_id = device["id"]
                    break
            
            # Reinicia o processo apropriado se estiver interrompido
            if selected_platform == "android" and (self.adb_process is None or self.adb_process.poll() is not None):
                # Reinicia o thread de monitoramento
                self.monitoring_thread = threading.Thread(target=self.monitor_logs)
                self.monitoring_thread.daemon = True
                self.monitoring_thread.start()
            elif selected_platform == "ios" and (self.ios_process is None or self.ios_process.poll() is not None):
                # Reinicia o thread de monitoramento
                self.monitoring_thread = threading.Thread(target=self.monitor_logs)
                self.monitoring_thread.daemon = True
                self.monitoring_thread.start()
        else:
            # Pausar monitoramento
            self.is_paused = True
            self.pause_btn.config(text="Retomar")
            self.log_text.insert(tk.END, "\n[Monitoramento pausado]\n")
            self.log_text.see(tk.END)
            
            # Verifica qual plataforma está sendo usada
            selected_device_display = self.device_var.get()
            selected_platform = None
            
            for device in self.device_data:
                if device["display"] == selected_device_display:
                    selected_platform = device["platform"]
                    break
            
            # Termina o processo apropriado se existente
            if selected_platform == "android" and self.adb_process and self.adb_process.poll() is None:
                self.adb_helper.stop_logcat(self.adb_process)
                self.adb_process = None
            elif selected_platform == "ios" and self.ios_process and self.ios_process.poll() is None:
                DeviceManager.stop_logging(process, 'ios')
                self.ios_process = None

    def stop_monitoring(self):
        """
        Finaliza o monitoramento atual de logs.
        """
        self.is_monitoring = False
        self.is_paused = False
        
        # Verifica qual plataforma está sendo usada
        selected_device_display = self.device_var.get()
        selected_platform = None
        
        for device in self.device_data:
            if device["display"] == selected_device_display:
                selected_platform = device["platform"]
                break
        
        # Termina o processo apropriado se existente
        if selected_platform == "android" and self.adb_process and self.adb_process.poll() is None:
            self.adb_helper.stop_logcat(self.adb_process)
            self.adb_process = None
        elif selected_platform == "ios" and self.ios_process and self.ios_process.poll() is None:
            IosDeviceHelper.stop_ios_logging(self.ios_process)
            self.ios_process = None
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            # Espera que a thread termine
            self.monitoring_thread.join(timeout=1.0)
        
        # Atualiza estado dos botões
        self.start_btn.config(text="Iniciar Monitoramento", command=self.start_monitoring)
        self.pause_btn.config(state="disabled", text="Pausar")
        
        # Habilita o botão de salvar logs apenas se houver logs coletados
        if self.collected_logs:
            self.save_btn.config(state="normal")
        
        self.log_text.insert(tk.END, "\n[Monitoramento finalizado]\n")
        self.log_text.see(tk.END)

    def monitor_logs(self):
        """
        Thread que monitora logs do dispositivo selecionado e filtra eventos de tagueamento.
        """
        try:
            # Encontra o dispositivo selecionado
            selected_device_display = self.device_var.get()
            selected_device = None
            
            for device in self.device_data:
                if device["display"] == selected_device_display:
                    selected_device = device
                    break
            
            if not selected_device:
                self.root.after(0, lambda: messagebox.showerror("Erro", "Dispositivo não encontrado"))
                return
                
            # Obtém informações sobre o dispositivo
            platform = selected_device["platform"]
            device_id = selected_device["id"]
            device_name = selected_device.get("name", "dispositivo")
            
            # Log inicial informando o início do monitoramento
            start_message = f"\n[Iniciando monitoramento de logs para {platform.upper()}: {device_name} ({device_id})]\n"
            self.root.after(0, lambda msg=start_message: self.update_log_text(msg))
            
            if platform == "android":
                # Para dispositivos Android, usamos ADB logcat
                self.adb_process = self.adb_helper.start_logcat(device_id)
                
                if not self.adb_process:
                    error_msg = "[Erro ao iniciar ADB logcat]\n"
                    self.root.after(0, lambda msg=error_msg: self.update_log_text(msg))
                    return
                
                # Lê e exibe as linhas em tempo real
                for line in iter(self.adb_process.stdout.readline, ''):
                    if not self.is_monitoring:
                        self.adb_helper.stop_logcat(self.adb_process)
                        break
                    
                    if self.is_paused:
                        # Se estiver pausado, não processa logs novos
                        time.sleep(0.1)
                        continue
                    
                    # Trata caracteres inválidos na linha
                    try:
                        # Limpa a linha de caracteres problemáticos
                        clean_line = line.encode('utf-8', 'replace').decode('utf-8')
                        
                        # Filtra e processa a linha de log
                        if any(tag in clean_line for tag in ['TAG_EVENTO', 'analytics', 'Analytics', 'evento']):
                            self.collected_logs.append(clean_line)
                            
                            # Atualiza a interface em thread segura
                            self.root.after(0, lambda l=clean_line: self.update_log_text(l))
                        
                    except UnicodeError:
                        # Caso ainda haja erro, ignora a linha problemática
                        continue
            
            elif platform == "ios":
                # Para dispositivos iOS, usamos libimobiledevice
                self.ios_process = IosDeviceHelper.start_ios_logging(device_id)
                
                if not self.ios_process:
                    error_msg = "[Erro ao iniciar monitoramento de logs iOS]\n"
                    self.root.after(0, lambda msg=error_msg: self.update_log_text(msg))
                    return
                
                # Lê e exibe as linhas em tempo real
                for line in iter(self.ios_process.stdout.readline, ''):
                    if not self.is_monitoring:
                        IosDeviceHelper.stop_ios_logging(self.ios_process)
                        break
                    
                    if self.is_paused:
                        # Se estiver pausado, não processa logs novos
                        time.sleep(0.1)
                        continue
                    
                    # Trata caracteres inválidos na linha
                    try:
                        # Limpa a linha de caracteres problemáticos
                        clean_line = line.encode('utf-8', 'replace').decode('utf-8')
                        
                        # Filtra e processa a linha de log - ajuste os tags conforme necessário para iOS
                        if any(tag in clean_line.lower() for tag in ['tag_evento', 'analytics', 'evento', 'firebase']):
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                            formatted_line = f"{timestamp} [{platform.upper()}] {clean_line}"
                            self.collected_logs.append(formatted_line)
                            
                            # Atualiza a interface em thread segura
                            self.root.after(0, lambda l=formatted_line: self.update_log_text(l))
                    
                    except UnicodeError:
                        # Caso ainda haja erro, ignora a linha problemática
                        continue
            
            # Se chegou aqui é porque o processo terminou
            if platform == "android":
                self.adb_process = None
            else:
                self.ios_process = None
            
        except Exception as e:
            error_msg = f"\n[Erro ao monitorar logs: {str(e)}]\n"
            self.root.after(0, lambda msg=error_msg: self.update_log_text(msg))
            self.is_monitoring = False
            self.adb_process = None
            self.ios_process = None
            self.root.after(0, lambda: self.start_btn.config(text="Iniciar Monitoramento", command=self.start_monitoring))

    def update_log_text(self, line):
        """
        Atualiza o widget de texto com uma nova linha de log.
        
        Args:
            line (str): Linha de log a ser adicionada ao widget de texto
        """
        self.log_text.insert(tk.END, line)
        self.log_text.see(tk.END)

    def save_logs(self):
        """
        Salva os logs coletados em arquivos CSV separados por funcionalidade.
        Se houver subfuncionalidade, organiza em subdiretórios.
        """
        if not self.collected_logs:
            # Mostra aviso de que não há logs para salvar
            self.dialog_helper.show_empty_logs_dialog(self.root)
            return
        
        # Agrupa logs por funcionalidade e subfuncionalidade
        logs_by_functionality = self.log_processor.group_logs_by_functionality(self.collected_logs)
        
        # 1. Salvar no diretório padrão do projeto (sem informar ao usuário)
        try:
            logs_base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs", "eventos")
            self.file_helper.save_logs_to_directory(logs_by_functionality, logs_base_dir, self.log_processor)
        except Exception as e:
            print(f"Erro ao salvar no diretório do projeto: {str(e)}")
        
        # 2. Perguntar ao usuário onde deseja salvar os logs
        try:
            custom_dir = filedialog.askdirectory(
                title="Selecione onde deseja salvar os dados",
                initialdir=os.path.expanduser("~")
            )
            
            if custom_dir:
                custom_logs_dir = os.path.join(custom_dir, "logs", "eventos")
                files_saved = self.file_helper.save_logs_to_directory(
                    logs_by_functionality, 
                    custom_logs_dir,
                    self.log_processor
                )
                
                if files_saved:
                    # Mostra diálogo de sucesso com a cor do botão corrigida
                    self.dialog_helper.show_success_dialog(
                        self.root,
                        "Sucesso",
                        "Logs salvos com sucesso!",
                        custom_logs_dir,
                        len(files_saved)
                    )
                else:
                    messagebox.showwarning("Aviso", "Nenhum arquivo de log foi salvo.")
            else:
                # Usuário cancelou a seleção de diretório
                messagebox.showinfo("Informação", "Operação de salvar cancelada.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao salvar os logs: {str(e)}")