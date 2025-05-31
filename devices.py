"""
Este arquivo contém classes e funções relacionadas ao gerenciamento de dispositivos móveis.
Responsabilidades:
- Detecção de dispositivos conectados (Android via ADB, iOS via libimobiledevice)
- Iniciar e interromper a captura de logs
- Processamento e filtragem de logs de dispositivos

Estas funcionalidades são usadas pela aplicação principal para monitorar eventos de tagueamento
em dispositivos conectados.
"""

import subprocess
import platform
import os
import shutil
import time
from tkinter import messagebox

class AdbHelper:
    """
    Utilitário para interagir com dispositivos Android via ADB.
    """

    @staticmethod
    def get_connected_devices():
        """
        Obtém a lista de dispositivos Android conectados via ADB.

        Returns:
            list: Lista de IDs dos dispositivos conectados
        """
        try:
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
            
            # Processa a saída para extrair os dispositivos
            lines = result.stdout.strip().split('\n')[1:]  # Pula a primeira linha (cabeçalho)
            devices = []
            
            for line in lines:
                if line.strip():
                    device_id = line.split()[0]
                    devices.append(device_id)
            
            return devices
        except Exception as e:
            print(f"Erro ao verificar dispositivos ADB: {str(e)}")
            return []

    @staticmethod
    def start_logcat(device_id):
        """
        Inicia a captura de logs via ADB logcat.

        Args:
            device_id (str): ID do dispositivo para capturar logs
            
        Returns:
            subprocess.Popen: Processo do ADB em execução
        """
        cmd = ['adb', '-s', device_id, 'logcat', '-v', 'time']
        return subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True, 
            bufsize=1, 
            universal_newlines=True,
            errors='replace'
        )

    @staticmethod
    def stop_logcat(process):
        """
        Interrompe um processo de captura de logs.

        Args:
            process (subprocess.Popen): Processo a ser interrompido
        """
        if process and process.poll() is None:
            process.terminate()


class IosDeviceHelper:
    """
    Utilitário para interagir com dispositivos iOS via libimobiledevice.
    """
    
    @staticmethod
    def check_dependencies():
        """
        Verifica se as dependências necessárias estão instaladas.
        
        Returns:
            bool: True se todas as dependências estão disponíveis
        """
        try:
            # Verificar se libimobiledevice está instalado
            idevice_path = shutil.which('idevice_id')
            return idevice_path is not None
        except Exception:
            return False
        
        
    @staticmethod
    def diagnose_ios_detection():
        """
        Função para diagnosticar problemas na detecção de dispositivos iOS
        
        Returns:
            str: Resultados do diagnóstico formatados
        """
        results = []
        
        # 1. Verificar se libimobiledevice está instalado
        libimobile_tools = ['idevice_id', 'idevicename', 'ideviceinfo', 'idevicesyslog']
        tools_status = {}
        
        for tool in libimobile_tools:
            path = shutil.which(tool)
            tools_status[tool] = path
            
        if all(tools_status.values()):
            results.append("✓ Todas as ferramentas libimobiledevice estão instaladas")
        else:
            results.append("✗ Algumas ferramentas libimobiledevice estão faltando:")
            for tool, path in tools_status.items():
                results.append(f"  - {tool}: {'✓ ' + path if path else '✗ Não encontrado'}")
        
        # 2. Tentar execução direta do idevice_id
        try:
            path = tools_status.get('idevice_id')
            if path:
                # Executar com verbose para mais informações
                cmd = f"{path} -l -d"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                results.append("\nSaída direta do idevice_id -l -d:")
                results.append(result.stdout if result.stdout else "Sem saída")
                
                if result.stderr:
                    results.append(f"Erro: {result.stderr}")
                    
                # Tentar listar todos os dispositivos, mesmo não confiáveis
                cmd = f"{path} -l -n"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                results.append("\nDispositivos não-confiáveis (idevice_id -l -n):")
                results.append(result.stdout if result.stdout.strip() else "Nenhum dispositivo não-confiável")
        except Exception as e:
            results.append(f"Erro ao executar idevice_id: {str(e)}")
        
        # 3. Verificar o serviço usbmuxd que é necessário para iOS
        try:
            if platform.system() == "Darwin":  # macOS
                ps_cmd = "ps aux | grep usbmuxd | grep -v grep"
                result = subprocess.run(ps_cmd, shell=True, capture_output=True, text=True)
                results.append("\nServiço usbmuxd:")
                if result.stdout:
                    results.append("✓ usbmuxd está em execução")
                    results.append(result.stdout.strip())
                else:
                    results.append("✗ usbmuxd não parece estar em execução")
            elif platform.system() == "Linux":
                service_cmd = "systemctl status usbmuxd"
                result = subprocess.run(service_cmd, shell=True, capture_output=True, text=True)
                results.append("\nServiço usbmuxd:")
                results.append(result.stdout)
        except Exception as e:
            results.append(f"Erro ao verificar usbmuxd: {str(e)}")
        
        # 4. Verificar dispositivos USB fisicamente conectados
        try:
            if platform.system() == "Darwin":  # macOS
                usb_cmd = "system_profiler SPUSBDataType | grep -A 10 -B 2 'Apple Mobile Device'"
                result = subprocess.run(usb_cmd, shell=True, capture_output=True, text=True)
                results.append("\nDispositivos iOS conectados fisicamente (USB):")
                if result.stdout:
                    results.append(result.stdout.strip())
                else:
                    results.append("Nenhum dispositivo iOS parece estar conectado fisicamente")
        except Exception as e:
            results.append(f"Erro ao verificar USB: {str(e)}")
        
        return "\n".join(results)
    
    @staticmethod
    def get_connected_devices():
        """
        Obtém a lista de dispositivos iOS conectados via libimobiledevice.

        Returns:
            list: Lista de IDs dos dispositivos conectados
        """
        if not IosDeviceHelper.check_dependencies():
            print("libimobiledevice não está instalado. Instale usando:")
            if platform.system() == "Darwin":  # macOS
                print("brew install libimobiledevice")
            elif platform.system() == "Linux":
                print("apt-get install libimobiledevice")
            return []
            
        try:
            # Obter caminho completo para o idevice_id
            idevice_id_path = shutil.which('idevice_id')
            if not idevice_id_path:
                print("Erro: idevice_id não encontrado no PATH")
                return []

            # Primeiro, verificar se existem dispositivos não confiáveis
            cmd = f"{idevice_id_path} -l -n"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
            
            if result.returncode == 0 and result.stdout.strip():
                non_trusted_devices = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
                
                # Verificar dispositivos confiáveis
                trusted_cmd = f"{idevice_id_path} -l"
                trusted_result = subprocess.run(trusted_cmd, shell=True, capture_output=True, text=True, check=False)
                
                if trusted_result.returncode == 0:
                    trusted_devices = [line.strip() for line in trusted_result.stdout.strip().split('\n') if line.strip()]
                    
                    # Se há dispositivos não-confiáveis mas nenhum confiável, avisar
                    if non_trusted_devices and not trusted_devices:
                        print("AVISO: Dispositivos iOS foram detectados, mas não estão confiáveis.")
                        print("Desbloqueie seu dispositivo iOS e aceite o prompt 'Confiar neste computador'.")
                        print("Dispositivos não confiáveis:", non_trusted_devices)
                
                # Retornar dispositivos confiáveis ou não confiáveis
                if trusted_result.returncode == 0 and trusted_result.stdout.strip():
                    devices = [line.strip() for line in trusted_result.stdout.strip().split('\n') if line.strip()]
                    print(f"Detectados {len(devices)} dispositivos iOS confiáveis")
                    return devices
                else:
                    # Sem dispositivos confiáveis, verificar se há erros
                    if trusted_result.stderr:
                        print(f"Erro na detecção de iOS: {trusted_result.stderr}")
                        
                    # Retornar dispositivos não confiáveis se não houver confiáveis
                    print(f"Detectados {len(non_trusted_devices)} dispositivos iOS não confiáveis")
                    return non_trusted_devices
            else:
                # Se nem dispositivos não confiáveis foram encontrados
                if result.stderr:
                    print(f"Erro na detecção de iOS: {result.stderr}")
                
                # Último recurso: tentar muito diligentemente encontrar qualquer coisa
                print("Tentando método alternativo de detecção de dispositivos iOS...")
                
                # Em algumas configurações, pode ser necessário um curto atraso
                time.sleep(1)
                
                # Tentar com shell direto e verificação de saída bruta
                cmd = f"{idevice_id_path} -l"
                try:
                    process = subprocess.Popen(
                        cmd, 
                        shell=True, 
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE, 
                        text=True
                    )
                    stdout, stderr = process.communicate(timeout=5)
                    
                    if stdout and stdout.strip():
                        devices = [line.strip() for line in stdout.strip().split('\n') if line.strip()]
                        print(f"Detectados {len(devices)} dispositivos iOS (método alternativo)")
                        return devices
                    
                    if stderr:
                        print(f"Erro na detecção alternativa: {stderr}")
                except Exception as e:
                    print(f"Erro no método alternativo: {str(e)}")
                
                print("Nenhum dispositivo iOS detectado (nem não confiável)")
                return []
                
        except Exception as e:
            print(f"Erro ao verificar dispositivos iOS: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

    @staticmethod
    def start_syslog(device_id=None):
        """
        Inicia a captura de logs via idevicesyslog.

        Args:
            device_id (str, optional): ID do dispositivo para capturar logs.
                                      Se None, usa o primeiro dispositivo disponível.
            
        Returns:
            subprocess.Popen: Processo do idevicesyslog em execução
        """
        # Obter caminho completo do idevicesyslog
        idevicesyslog_path = shutil.which('idevicesyslog')
        if not idevicesyslog_path:
            print("Erro: idevicesyslog não encontrado no PATH")
            return None

        cmd = [idevicesyslog_path]
        if device_id:
            cmd.extend(['-u', device_id])
            
        return subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True, 
            bufsize=1, 
            universal_newlines=True,
            errors='replace'
        )

    @staticmethod
    def stop_syslog(process):
        """
        Interrompe um processo de captura de logs.

        Args:
            process (subprocess.Popen): Processo a ser interrompido
        """
        if process and process.poll() is None:
            process.terminate()
            
    @staticmethod
    def get_device_info(device_id):
        """
        Obtém informações sobre o dispositivo iOS.
        
        Args:
            device_id (str): ID do dispositivo
            
        Returns:
            dict: Informações do dispositivo (modelo, nome, iOS versão)
        """
        try:
            # Obter caminhos completos
            idevicename_path = shutil.which('idevicename')
            ideviceinfo_path = shutil.which('ideviceinfo')
            
            if not idevicename_path or not ideviceinfo_path:
                print("Erro: ferramentas idevice não encontradas no PATH")
                return {}

            # Usar shell=True e caminho completo para maior confiabilidade
            name_cmd = f"{idevicename_path} -u {device_id}"
            name_result = subprocess.run(name_cmd, shell=True, capture_output=True, text=True)
            
            info_cmd = f"{ideviceinfo_path} -u {device_id}"
            info_result = subprocess.run(info_cmd, shell=True, capture_output=True, text=True)
            
            info = {}
            if name_result.returncode == 0:
                info['name'] = name_result.stdout.strip()
            
            if info_result.returncode == 0:
                for line in info_result.stdout.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        if key.strip() in ['ProductName', 'ProductVersion', 'DeviceClass']:
                            info[key.strip()] = value.strip()
            
            return info
        except Exception as e:
            print(f"Erro ao obter informações do dispositivo iOS: {str(e)}")
            return {}

    @staticmethod
    def verify_trust_status(device_id):
        """
        Verifica se um dispositivo está em estado confiável.
        
        Args:
            device_id (str): ID do dispositivo iOS
            
        Returns:
            bool: True se o dispositivo estiver em estado confiável
        """
        try:
            ideviceinfo_path = shutil.which('ideviceinfo')
            if not ideviceinfo_path:
                return False
                
            cmd = f"{ideviceinfo_path} -u {device_id}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            # Se o comando executar com sucesso, o dispositivo é confiável
            return result.returncode == 0
        except Exception:
            return False
        
    @staticmethod
    def start_ios_logging(device_id=None):
        """
        Alias for start_syslog for backward compatibility.
        
        Args:
            device_id (str, optional): ID do dispositivo para capturar logs.
                                    Se None, usa o primeiro dispositivo disponível.
            
        Returns:
            subprocess.Popen: Processo do idevicesyslog em execução
        """
        return IosDeviceHelper.start_syslog(device_id)
    
    @staticmethod
    def stop_ios_logging(process=None):
        """
        Alias for stop_syslog for backward compatibility.
        
        Args:
            process (subprocess.Popen, optional): Process to be terminated.
                                                If None, only cleanup is performed.
        """
        return IosDeviceHelper.stop_syslog(process)


class DeviceManager:
    """
    Gerenciador unificado de dispositivos móveis (Android e iOS).
    """
    
    @staticmethod
    def get_all_connected_devices():
        """
        Obtém todos os dispositivos conectados de todas as plataformas.
        
        Returns:
            dict: Dispositivos conectados por plataforma
        """
        return {
            'android': AdbHelper.get_connected_devices(),
            'ios': IosDeviceHelper.get_connected_devices()
        }
    
    @staticmethod
    def start_logging(device_id, platform):
        """
        Inicia a captura de logs para o dispositivo especificado.
        
        Args:
            device_id (str): ID do dispositivo
            platform (str): 'android' ou 'ios'
            
        Returns:
            subprocess.Popen: Processo de captura de logs em execução
        """
        if platform.lower() == 'android':
            return AdbHelper.start_logcat(device_id)
        elif platform.lower() == 'ios':
            return IosDeviceHelper.start_syslog(device_id)
        else:
            raise ValueError(f"Plataforma não suportada: {platform}")
    
    def start_device_logging(self):
        """
        Inicia a captura de logs do dispositivo selecionado
        """
        selected_index = self.device_combo.current()
        
        if selected_index == -1 or not self.device_data:
            messagebox.showerror("Erro", "Nenhum dispositivo selecionado")
            return
        
        # Obtém os dados do dispositivo selecionado
        device_info = self.device_data[selected_index]
        device_id = device_info["id"]
        platform = device_info["platform"]
        
        try:
            # Inicia o processo de log apropriado para a plataforma
            log_process = DeviceManager.start_logging(device_id, platform)
            self.logging_process = log_process
            self.current_device_platform = platform
            
            # Configurar para ler as linhas do processo em uma thread separada
            if log_process:
                import threading
                
                def read_output():
                    while log_process and log_process.poll() is None:
                        line = log_process.stdout.readline()
                        if line:
                            # Processar a linha e exibir na UI
                            # Chamar método para processar e exibir log na UI
                            self.process_log_line(line.strip(), platform)
                
                # Iniciar thread para ler output
                self.log_thread = threading.Thread(target=read_output, daemon=True)
                self.log_thread.start()
                
                # Atualizar a UI para indicar que a captura está em andamento
                # [atualização da UI aqui]
            else:
                messagebox.showerror("Erro", "Não foi possível iniciar o processo de log")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao iniciar captura de logs: {str(e)}")

    def process_log_line(self, line, platform):
        """
        Processa uma linha de log conforme a plataforma e atualiza a UI
        
        Args:
            line (str): Linha de log capturada
            platform (str): 'android' ou 'ios'
        """
        try:
            # Inserir a linha no widget de texto/log da UI
            # Neste exemplo, assumimos que existe um widget Text chamado self.log_text
            
            # Talvez você queira aplicar filtros ou formatação específica para cada plataforma
            if platform == 'android':
                # Processamento específico para Android
                self.log_text.insert("end", line + "\n")
            elif platform == 'ios':
                # Processamento específico para iOS
                self.log_text.insert("end", line + "\n")
            
            # Auto-scroll para a última linha
            self.log_text.see("end")
        except Exception as e:
            print(f"Erro ao processar linha de log: {str(e)}")
    
    @staticmethod
    def stop_logging(process, platform_type):
        """
        Interrompe um processo de captura de logs.
        
        Args:
            process (subprocess.Popen): Processo a ser interrompido
            platform_type (str): 'android' ou 'ios'
        """
        if platform_type.lower() == 'android':
            AdbHelper.stop_logcat(process)
        elif platform_type.lower() == 'ios':
            IosDeviceHelper.stop_syslog(process)
        else:
            raise ValueError(f"Plataforma não suportada: {platform_type}")

    @staticmethod
    def diagnose_connection_issues():
        """
        Executa diagnóstico completo das conexões com dispositivos.
        
        Returns:
            str: Resultado do diagnóstico
        """
        results = []
        
        # Verificar dispositivos Android
        try:
            adb_path = shutil.which('adb')
            if adb_path:
                results.append(f"ADB encontrado: {adb_path}")
                
                # Verificar versão do ADB
                version_cmd = "adb version"
                version_result = subprocess.run(version_cmd, shell=True, capture_output=True, text=True)
                if version_result.stdout:
                    results.append(f"Versão ADB: {version_result.stdout.strip()}")
                    
                # Verificar status do servidor ADB
                devices_cmd = "adb devices"
                devices_result = subprocess.run(devices_cmd, shell=True, capture_output=True, text=True)
                if devices_result.stdout:
                    results.append(f"Status ADB: {devices_result.stdout.strip()}")
            else:
                results.append("ADB não encontrado no sistema")
        except Exception as e:
            results.append(f"Erro ao verificar ADB: {str(e)}")
            
        # Verificar dispositivos iOS
        results.append("\n=== Diagnóstico de Dispositivos iOS ===")
        ios_diagnostics = IosDeviceHelper.diagnose_ios_detection()
        results.append(ios_diagnostics)
        
        return "\n".join(results)


# Exemplo de uso:
if __name__ == "__main__":
    # Obtém todos os dispositivos conectados
    print("\n=== Verificando dispositivos conectados ===\n")
    devices = DeviceManager.get_all_connected_devices()
    
    print("Dispositivos Android conectados:")
    if devices['android']:
        for device in devices['android']:
            print(f" - {device}")
    else:
        print(" - Nenhum dispositivo Android conectado")
        
    print("\nDispositivos iOS conectados:")
    if devices['ios']:
        for device in devices['ios']:
            print(f" - {device}")
            # Verificar se o dispositivo é confiável
            is_trusted = IosDeviceHelper.verify_trust_status(device)
            trust_status = "Confiável" if is_trusted else "Não confiável"
            print(f"   Status: {trust_status}")
            
            # Tentar obter informações se for confiável
            if is_trusted:
                info = IosDeviceHelper.get_device_info(device)
                if info:
                    print(f"   Nome: {info.get('name', 'N/A')}")
                    print(f"   Modelo: {info.get('ProductName', 'N/A')}")
                    print(f"   iOS: {info.get('ProductVersion', 'N/A')}")
            else:
                print("   Desbloqueie o dispositivo e aceite o prompt 'Confiar neste computador'")
    else:
        print(" - Nenhum dispositivo iOS conectado")
        
        # Se nenhum dispositivo for encontrado, executar diagnóstico
        print("\n=== Executando diagnóstico de conexão iOS ===")
        print(IosDeviceHelper.diagnose_ios_detection())