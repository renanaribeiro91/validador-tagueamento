Guia de Build: Tag Validator

📋 Como Gerar o Executável do Tag Validator
✅ OBJETIVO

Gerar um executável independente (standalone) para Windows, macOS ou Linux que funcione com interface gráfica, permitindo:

Validação automática de tags no navegador e dispositivos móveis (Android e iOS)
Análise inteligente com Flow AI
Visualização de resultados em dashboard interativo
Distribuição simplificada para equipes de Analytics

🚀 Métodos de Build

1️⃣ GERAR EXECUTÁVEL USANDO O SCRIPT DE BUILD (RECOMENDADO)

# Método automatizado (mais simples)
python3 build_app.py
O que este script faz:

Configura todos os parâmetros do PyInstaller
Inclui automaticamente templates HTML, CSS e arquivos JS
Integra o módulo de análise AI (ai_analyzer.py)
Verifica e alerta sobre arquivos ausentes
Gera log detalhado do processo de build

2️⃣ GERAR EXECUTÁVEL MANUALMENTE (ALTERNATIVA)

Para macOS/windows/linux:
pyinstaller --onefile --windowed \
  --name "TagValidator" \
  --add-data "template_dashboard.html:." \
  --add-data "template_dashboard.css:." \
  --add-data "dashboard.js:." \
  --add-data "dashboard-utils.js:." \
  --add-data "readme.md:." \
  --hidden-import requests \
  --hidden-import json \
  --hidden-import subprocess \
  --hidden-import os \
  --hidden-import sys \
  --hidden-import re \
  --hidden-import time \
  --hidden-import datetime \
  --add-data "ai_analyzer.py:." \
  --add-data "devices.py:." \
  --add-data "dialog_utils.py:." \
  --add-data "file_utils.py:." \
  --add-data "log_processor.py:." \
  --add-data "ui_theme.py:." \
  main.py

3️⃣ PERSONALIZAR BUILD COM ARQUIVO .SPEC (OPICIONAL)

# 1. Gere primeiro o arquivo .spec básico
pyinstaller --windowed --name "TagValidator" tag_validator.py

# 2. Edite o arquivo TagValidator.spec conforme necessário 
# (adicione recursos, configure caminhos)

# 3. Use o arquivo .spec para o build final
pyinstaller "TagValidator.spec"

📱 Configuração para Dispositivos Móveis
Android (ADB)
Requisitos:

Instalar ADB (Android Debug Bridge):

Windows:
# Opção 1: Instalar via Chocolatey
choco install adb

# Opção 2: Baixar manualmente
# Baixe o Platform Tools do Android SDK:
# https://developer.android.com/studio/releases/platform-tools
# Extraia e adicione ao PATH do sistema

macOS:

brew install android-platform-tools

Linux:

sudo apt-get install adb       # Debian/Ubuntu
sudo pacman -S android-tools   # Arch Linux
sudo dnf install android-tools # Fedora
Configurar dispositivo Android:

Ative o modo de desenvolvedor:
Vá para Configurações > Sobre o telefone > Informações do software
Toque 7 vezes no "Número da versão" ou "Build number"
Ative a Depuração USB:
Vá para Configurações > Opções do desenvolvedor
Ative "Depuração USB"
Conecte o dispositivo via cabo USB
Autorize o computador quando solicitado no dispositivo
Verificar conexão:


adb devices
Deve mostrar seu dispositivo na lista com status "device"

iOS (libimobiledevice)
Requisitos:

Instalar libimobiledevice:

macOS:
brew install libimobiledevice

Windows:
# Opção 1: Instalar via Chocolatey
choco install libimobiledevice

# Opção 2: Baixar versão compilada:
# https://github.com/libimobiledevice-win32/imobiledevice-net
# Extrair e adicionar ao PATH

Linux:
sudo apt-get install libimobiledevice6 libimobiledevice-utils   # Debian/Ubuntu
sudo pacman -S libimobiledevice                                # Arch Linux
sudo dnf install libimobiledevice libimobiledevice-utils       # Fedora

Configurar dispositivo iOS:

Conecte o dispositivo via cabo USB (não Bluetooth)
Desbloqueie o dispositivo com seu código
Quando perguntado "Confiar neste computador?", selecione "Confiar"
Digite seu código quando solicitado
Verificar conexão:


idevice_id -l
Deve mostrar o UDID (identificador único) do seu dispositivo.

📦 Distribuição e Instalação
Para Windows:
# O executável estará em:
dist/TagValidator.exe

# Para criar um instalador (opcional)
# Use NSIS ou Inno Setup com o executável gerado

Para macOS:
# Mover para pasta Applications (todo o sistema)
cp -R dist/TagValidator.app /Applications/

# OU para pasta Applications do usuário atual
cp -R dist/TagValidator.app ~/Applications/

Para Linux:
# Copiar para /opt (recomendado para aplicações de terceiros)
sudo cp dist/TagValidator /opt/

# Criar link simbólico para PATH
sudo ln -s /opt/TagValidator /usr/local/bin/tagvalidator

# Criar arquivo .desktop para menu de aplicativos
cat > ~/.local/share/applications/tagvalidator.desktop << EOF

[Desktop Entry]
Name=Tag Validator
Exec=/opt/TagValidator
Icon=/opt/tagvalidator/icon.png
Type=Application
Categories=Development;
EOF
Remover Restrições de Segurança (macOS)

# Remove restrições de segurança do macOS
xattr -dr com.apple.quarantine "/Applications/TagValidator.app"
Empacotar para Distribuição


# Windows - criar arquivo ZIP
cd dist
powershell Compress-Archive -Path TagValidator.exe -DestinationPath TagValidator.zip

# macOS - criar arquivo ZIP
cd dist
zip -r "TagValidator.zip" "TagValidator.app"

# Linux - criar arquivo tar.gz
cd dist
tar -czvf TagValidator-linux.tar.gz TagValidator

🔍 Verificação e Depuração
Executar via Terminal (para debug)

# Windows
dist\TagValidator.exe

# macOS
/Applications/TagValidator.app/Contents/MacOS/TagValidator

# Linux
/opt/TagValidator
Verificar se Arquivos Foram Incluídos

# Windows
dir /s dist\TagValidator.exe

# macOS
find /Applications/TagValidator.app -type f | grep -v "__pycache__"

# Linux
find /opt/TagValidator -type f
🧪 Resolução de Problemas Comuns
Se o app não abrir:


# Verificar erros de execução via terminal/prompt
# Atualizar PyInstaller para a versão mais recente
pip3 install --upgrade pyinstaller

# Garantir que todas as dependências estão instaladas
pip3 install requests
Se recursos (templates, CSS, JS) não forem encontrados:


# Refazer o build especificando caminhos absolutos:
pyinstaller --onefile --windowed --name TagValidator \
  --add-data "$(pwd)/template_dashboard.html:." \
  tag_validator.py
Se o módulo AI Analyzer falhar:


# Verificar credenciais da API Flow
# Testar conexão internet
# Verificar se os imports necessários foram incluídos no build
🛠️ Estrutura do Projeto

TagValidator/
├── main.py                  # Script principal
├── tag_validator.py         # Módulo de validação
├── ai_analyzer.py           # Integração com Flow AI
├── devices.py               # Gerenciamento de dispositivos móveis
├── dialog_utils.py          # Utilitários de interface para diálogos
├── file_utils.py            # Utilitários para manipulação de arquivos
├── log_processor.py         # Processamento e análise de logs
├── ui_theme.py              # Configurações de UI
├── template_dashboard.html  # Template HTML do dashboard
├── template_dashboard.css   # Estilos do dashboard
├── dashboard.js             # Scripts do dashboard
├── dashboard-utils.js       # Funções utilitárias JS
├── build_app.py             # Script de build
├── readme.md                # Documentação
└── logs/                    # Diretório de logs

✅ Checklist Antes de Distribuir
 App abre corretamente com duplo clique
 Interface gráfica carrega sem erros
 Tags são validadas corretamente
 Integração com Flow AI está funcionando
 Templates e recursos são encontrados e carregados
 Dashboard exibe os resultados corretamente
 Arquivo ZIP está completo e não corrompido
 Detecção de dispositivos Android funciona
 Detecção de dispositivos iOS funciona
 Logs de dispositivos móveis são capturados corretamente

📝 Notas Importantes
O script de build (build_app.py) foi otimizado para detectar automaticamente os arquivos do projeto
A integração com Flow AI requer conexão com internet
O arquivo readme.md contém a documentação completa do aplicativo
Logs são armazenados na pasta logs/ para facilitar debugging
A captura de logs em dispositivos Android requer ADB configurado
A captura de logs em dispositivos iOS requer libimobiledevice instalado

🚧 Funcionalidades em Desenvolvimento
Validação de tags em dispositivos móveis (Android/iOS)
Dashboard avançado com filtros personalizados
Integração expandida da API Flow para análise preditiva
Suporte para validação batch de múltiplos sites
Tag Validator v1.1 | Ferramenta interna para validação de implementações de tags e analytics

🚧 Monitoramento iOS em Fase Beta
Status Atual
O monitoramento de eventos para dispositivos iOS está parcialmente implementado. Atualmente, o sistema consegue detectar a conexão com dispositivos iOS e iniciar o processo de monitoramento, porém existem limitações na captura de eventos de analytics específicos.

Limitações Conhecidas
Captura Parcial de Eventos: Embora o sistema consiga estabelecer conexão e monitorar logs do dispositivo iOS, a captura dos parâmetros específicos de analytics (como Firebase Analytics, TAG_EVENTO e similares) ainda não está funcionando adequadamente.
Filtros de Eventos: Os filtros atuais podem não estar detectando corretamente os eventos de analytics no formato específico em que são emitidos pelos aplicativos iOS.
Permissões: Estamos investigando possíveis restrições de permissões que podem estar limitando o acesso aos logs completos de analytics.
Próximos Passos
Análise detalhada dos formatos de log emitidos por aplicações iOS contendo eventos analytics
Implementação de filtros adicionais específicos para a estrutura de logs do iOS
Teste com diferentes configurações de permissões e níveis de acesso
Possível desenvolvimento de componentes adicionais para melhorar a interceptação dos eventos
Recomendação Atual
Para validação completa de eventos em aplicativos iOS, recomendamos temporariamente o uso de ferramentas complementares como o Firebase Debug View ou ferramentas nativas de logging do iOS até que esta funcionalidade seja completamente implementada.