
# 🏷️ Tag Validator

## ✅ Objetivo

Criar uma ferramenta standalone com interface gráfica para validação de tags de analytics em sites e dispositivos móveis. Inclui:

- Validação automática de tags no navegador e dispositivos Android/iOS.
- Análise inteligente com Flow AI.
- Dashboard interativo para exibição dos resultados.
- Empacotamento em executável (.exe, .app, Linux bin) para fácil distribuição.

---

## 🚀 Como Gerar o Executável

### 1️⃣ Usando Script de Build (Recomendado)

```bash
python3 build_app.py
```

O script:
- Usa PyInstaller para gerar o executável
- Inclui templates, JS, CSS, módulos AI
- Gera logs detalhados

### 2️⃣ Usando PyInstaller Manualmente

```bash
pyinstaller --onefile --windowed --name "TagValidator" \
  --add-data "template_dashboard.html:." \
  --add-data "template_dashboard.css:." \
  --add-data "dashboard.js:." \
  --add-data "dashboard-utils.js:." \
  --add-data "readme.md:." \
  --add-data "ai_analyzer.py:." \
  --add-data "devices.py:." \
  --add-data "dialog_utils.py:." \
  --add-data "file_utils.py:." \
  --add-data "log_processor.py:." \
  --add-data "ui_theme.py:." \
  main.py
```

---

## 📱 Configuração para Dispositivos Móveis

### Android

- Instalar ADB
- Ativar modo desenvolvedor e depuração USB
- Conectar o dispositivo via cabo

```bash
adb devices
```

### iOS

- Instalar `libimobiledevice`
- Conectar e confiar no computador
- Verificar conexão

```bash
idevice_id -l
```

---

## 📦 Instalação por Sistema Operacional

### Windows

- Executável: `dist/TagValidator.exe`
- Criar instalador: Use NSIS ou Inno Setup

### macOS

```bash
cp -R dist/TagValidator.app /Applications/
xattr -dr com.apple.quarantine "/Applications/TagValidator.app"
```

### Linux

```bash
sudo cp dist/TagValidator /opt/
sudo ln -s /opt/TagValidator /usr/local/bin/tagvalidator
```

---

## 🛠️ Estrutura do Projeto

```
TagValidator/
├── main.py
├── tag_validator.py
├── ai_analyzer.py
├── devices.py
├── dialog_utils.py
├── file_utils.py
├── log_processor.py
├── ui_theme.py
├── template_dashboard.html
├── template_dashboard.css
├── dashboard.js
├── dashboard-utils.js
├── build_app.py
├── readme.md
└── logs/
```

---

## ✅ Checklist Final

- [x] Interface gráfica abre corretamente
- [x] Tags validadas no browser e mobile
- [x] Integração com Flow AI funciona
- [x] Dashboard exibe resultados
- [x] Executável distribuído funcionalmente
- [x] Logs capturados em Android/iOS

---

## 🧪 Debug e Problemas Comuns

### App não abre?

- Verificar via terminal
- Atualizar PyInstaller
- Conferir dependências

### Módulo AI com erro?

- Verificar conexão, API, e importações

---

## 🚧 Monitoramento iOS em Fase Beta

### Status Atual

O sistema consegue detectar a conexão com dispositivos iOS e iniciar o monitoramento, porém existem limitações na captura de eventos de analytics específicos.

### Limitações Conhecidas

- **Captura Parcial de Eventos:** Falha em capturar parâmetros como Firebase Analytics, TAG_EVENTO, etc.
- **Filtros de Eventos:** Podem não detectar eventos no formato do iOS.
- **Permissões:** Possíveis restrições limitando acesso completo aos logs.

### Próximos Passos

- Análise dos formatos de log do iOS
- Criação de filtros específicos
- Testes com permissões e níveis de acesso
- Desenvolvimento de novos componentes de captura

### Recomendação Atual

Utilize ferramentas como **Firebase Debug View** até que a funcionalidade esteja totalmente implementada.

---

## 📝 Notas Finais

- A integração com Flow AI exige internet
- Subistituir a IA atual por outra a seu critério, a mesma está restrita a mim.
- Logs ficam na pasta `/logs`
- O script `build_app.py` automatiza tudo

---

## 🏁 Versão

**Tag Validator v1.1**
Ferramenta interna para validação de tags de analytics
