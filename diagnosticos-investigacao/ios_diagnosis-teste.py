#!/usr/bin/env python3
"""
Script de diagnóstico simplificado para detecção de dispositivos iOS
"""

import os
import sys
import subprocess
import platform
import shutil
import time

def run_command(cmd, shell=False):
    """Executa um comando e retorna o resultado"""
    try:
        if isinstance(cmd, list) and shell:
            cmd = ' '.join(cmd)
        
        print(f"Executando: {cmd}")
        
        result = subprocess.run(
            cmd,
            shell=shell,
            capture_output=True,
            text=True
        )
        
        return {
            'stdout': result.stdout.strip(),
            'stderr': result.stderr.strip(),
            'returncode': result.returncode
        }
    except Exception as e:
        return {
            'stdout': '',
            'stderr': str(e),
            'returncode': -1
        }

# Cabeçalho
print("\n===== DIAGNÓSTICO DE DISPOSITIVOS iOS =====\n")

# Informações básicas do sistema
print(f"Sistema: {platform.system()} {platform.release()}")
print(f"Python: {sys.version.split()[0]}")
print(f"Diretório atual: {os.getcwd()}")

# Verificar executáveis
print("\n----- FERRAMENTAS INSTALADAS -----")
ios_tools = ['idevice_id', 'ideviceinfo', 'idevicename', 'idevicesyslog']
for tool in ios_tools:
    path = shutil.which(tool)
    print(f"{tool}: {'✓ ' + path if path else '✗ não encontrado'}")

# Testar execução direta
print("\n----- TESTE DE idevice_id DIRETO -----")
cmd_result = run_command(['idevice_id', '-l'])
print(f"Saída: '{cmd_result['stdout']}'")
print(f"Erro: '{cmd_result['stderr']}'")
print(f"Código de retorno: {cmd_result['returncode']}")

# Testar com shell=True
print("\n----- TESTE DE idevice_id VIA SHELL -----")
cmd_result = run_command('idevice_id -l', shell=True)
print(f"Saída: '{cmd_result['stdout']}'")
print(f"Erro: '{cmd_result['stderr']}'")
print(f"Código de retorno: {cmd_result['returncode']}")

# Verificar permissões dos processos relevantes
print("\n----- PROCESSOS USB RELEVANTES -----")
if platform.system() == "Darwin":  # macOS
    cmd_result = run_command("ps aux | grep -E 'usbmuxd|idevice'", shell=True)
    print(cmd_result['stdout'])
elif platform.system() == "Linux":
    cmd_result = run_command("ps aux | grep -E 'usbmuxd|idevice'", shell=True)
    print(cmd_result['stdout'])
elif platform.system() == "Windows":
    cmd_result = run_command("tasklist | findstr idevice", shell=True)
    print(cmd_result['stdout'])

# Testar execuções alternativas
print("\n----- EXECUÇÕES ALTERNATIVAS -----")

# Usando o caminho absoluto se disponível
idevice_id_path = shutil.which('idevice_id')
if idevice_id_path:
    cmd_result = run_command([idevice_id_path, '-l'])
    print(f"Caminho absoluto - Saída: '{cmd_result['stdout']}'")

# Usando PATH explícito
if platform.system() != "Windows":
    paths = ["/usr/bin", "/usr/local/bin", "/opt/homebrew/bin"]
    for path in paths:
        if os.path.exists(f"{path}/idevice_id"):
            cmd = f"{path}/idevice_id -l"
            cmd_result = run_command(cmd, shell=True)
            print(f"{cmd} - Saída: '{cmd_result['stdout']}'")

print("\n----- TESTE COM TIMEOUT MAIOR -----")
try:
    process = subprocess.Popen(['idevice_id', '-l'], 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE)
    
    # Esperar 5 segundos
    print("Aguardando 5 segundos...")
    for _ in range(5):
        if process.poll() is not None:
            break
        time.sleep(1)
        print(".", end="", flush=True)
    print()
    
    stdout, stderr = process.communicate(timeout=1)
    print(f"Saída: '{stdout.decode('utf-8', errors='replace').strip()}'")
    if stderr:
        print(f"Erro: '{stderr.decode('utf-8', errors='replace').strip()}'")
except Exception as e:
    print(f"Erro no teste com timeout: {str(e)}")

print("\n===== SUGESTÕES DE SOLUÇÃO =====")
print("""
Com base nos resultados, considere:

1. Se nenhum comando detectou dispositivos:
   - Certifique-se que o dispositivo está desbloqueado 
   - Confirme que a mensagem "Confiar neste computador?" foi aceita
   - Tente usar outro cabo USB
   - Reinicie o dispositivo iOS

2. Se o comando funciona no terminal mas não no script:
   - Execute o script como administrador/sudo
   - Verifique a versão do Python usada pelo terminal vs. script
   - Adicione explicitamente o caminho completo ao executar o comando
   
3. Correção no código principal:
   - Use o caminho completo para o idevice_id
   - Use 'shell=True' se funcionou melhor nos testes
   - Aumente o timeout da execução do comando
""")