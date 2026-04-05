# Solução Ministério Iluminação 

- Solução para escalas do ministérios de iluminação da minha igreja; 

### Problema: 
- Frequentemente, as pessoas esquecem que estão escaladas no dia em que estão na escala - por uma comunicação muitas vezes insuficiente. 

### Solução: 
- Farei uma automação que lerá a escala (lerá o arquivo PNG) e enviará uma mensagem no Whatsapp da pessoa escalada 12 horas antes do culto em que está escalada. 

### Funcionalidades: 
    - Leitura automática de imagem (OCR); 
    - Mapeamento de contatos; 
    - Agendamento de mensagens; 
    - Notificação de mensagem padronizada; 

### Tecnologias: 
    - Python; 
    - Leitura de imagem (OCR): Google Cloud Vision API 
    - Integração com Whatsapp : PyWhatKit;
    - Agendamento de tarefas :  
    - Hospedagem (Cloud): Oracle Cloud (Always Free VPS); 

### Como funcionará a integração? 
    1. Quando a aplicação rodar ela vai gerar um QR Code no terminal; 
    2. O usuário irá escanear esse QR Code com o celular que será o remetente das mensagens; 
    3. A biblioteca salvará automaticamente a sessão para que o software trabalhe 24/7; 

## 📂 Estrutura do Projeto

``` 
📦 solucao-ministerio-iluminacao
 ┣ 📂 src
 ┃ ┣ 📂 config           # Configurações gerais e variáveis
 ┃ ┣ 📂 services         # Lógica isolada (vision_api.py, whatsapp_bot.py)
 ┃ ┣ 📂 utils            # Funções auxiliares (formatadores, tratamento de strings)
 ┃ ┣ 📂 jobs             # Rotinas do scheduler para envio das mensagens
 ┃ ┗ 📜 main.py          # Arquivo principal que inicia o bot e o agendamento
 ┣ 📂 assets
 ┃ ┗ 📜 escala-mes.png   # Imagem atual da escala
 ┣ 📜 .env               # Variáveis de ambiente (Ex: Caminho do driver, credenciais)
 ┣ 📜 contatos.json      # Relação: "Nome na Escala" -> "5511999999999"
 ┣ 📜 requirements.txt   # Dependências do Python
 ┗ 📜 README.md

 ``` 


## 🚀 Instalação

### Passo 1: Clonar o Repositório

```bash
git clone <seu-repositorio>
cd "Projetos - NF Ti/SolucaoMinIluminacao"
```

### Passo 2: Criar Ambiente Virtual

**Windows PowerShell:**
```powershell
python -m venv venv
.\venv\Scripts\Activate
```

### Passo 3: Instalar Dependências

```bash
pip install -r requirements.txt
```


**Verificar instalação:**
```bash
pip list
```

Deve mostrar todos os 9 pacotes listados em `requirements.txt`.

---

## ⚙️ Configuração

### 1. Configurar Google Cloud Vision API

#### Passo A: Criar Projeto
1. Acesse [Google Cloud Console](https://console.cloud.google.com)
2. Clique em **Criar Projeto**
3. Nomeie como "ministerio-iluminacao"
4. Copie o **Project ID**

#### Passo B: Habilitar Vision API
1. Vá para **APIs & Services** → **Library**
2. Procure "Cloud Vision API"
3. Clique em **Enable**

#### Passo C: Criar Credenciais
1. Vá para **APIs & Services** → **Credentials**
2. Clique **Create Credentials** → **Service Account**
3. Preencha os dados básicos
4. Na aba **Keys**, clique **Add Key** → **Create new key** → **JSON**
5. Um arquivo `.json` será baixado

#### Passo D: Configurar Projeto
1. Renomeie o arquivo para `credentials.json`
2. Coloque na **raiz do projeto**:
   ```
   c:\Users\User\Desktop\Projetos - NF Ti\SolucaoMinIluminacao\credentials.json
   ```

### 2. Configurar Arquivo `.env`

Edite o arquivo `.env` na raiz:

```env
# Google Cloud
GOOGLE_PROJECT_ID=seu-project-id-aqui

# WhatsApp
WHATSAPP_SESSION_PATH=./session
WHATSAPP_DELAY_SECONDS=3

# Scheduler
SCHEDULER_ENABLED=True
MESSAGE_ADVANCE_HOURS=12
CHECK_INTERVAL_MINUTES=30

# File Paths
CONTACTS_FILE_PATH=./contatos.json
SCALE_IMAGE_PATH=./assets/escala-mes.png

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

### 3. Adicionar Contatos

Edite `contatos.json`:

```json
{
  "contatos": {
    "Nome da Pessoa": "5511999999999",
    "Outra Pessoa": "5511888888888"
  }
}
```

**Formato do número:** 55 + DDD (2 dígitos) + 9 + 8 dígitos
- ✅ Correto: `5511999999999`
- ❌ Errado: `(11) 99999-9999`

---

## 🎮 Como Usar

### Executar o Projeto

Com a venv ativada:

```bash
python -m src.main
```