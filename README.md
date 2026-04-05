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