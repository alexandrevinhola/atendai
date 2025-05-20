
# 🤖 AtendAI - Chatbot Inteligente para Atendimento ao Cliente

**AtendAI** é um assistente virtual desenvolvido com Flask, inteligência artificial (OpenAI GPT), interface web responsiva e banco de dados local. Ele é projetado para responder perguntas, armazenar histórico de conversas, aprender com feedback dos usuários e facilitar o atendimento automatizado.

---

## 📌 Propósito

Proporcionar um atendimento simples, direto e automatizado para usuários que buscam informações rápidas e registro de interações, com capacidade de evolução baseada em aprendizado contínuo.

---

## 👥 Público-alvo

Qualquer pessoa que precise de atendimento automatizado básico, como clientes de serviços digitais, bancários, e-commerces e sistemas de suporte geral.

---

## 🛠️ Funcionalidades

- Processamento de linguagem natural com OpenAI GPT-3.5
- Interface web simples com Bootstrap
- Histórico de conversas por sessão e usuário
- Banco de dados SQLite com perguntas e respostas reutilizáveis
- Aprendizado de perguntas desconhecidas
- Feedback sobre respostas úteis
- Sugestões de comandos mais comuns
- Encerramento e limpeza de sessão

---

## 💡 Tecnologias Utilizadas

- **Python 3**
- **Flask**
- **SQLite3**
- **OpenAI GPT (API)**
- **HTML + CSS + Bootstrap 5**
- **UUID / Datetime / JSON**

---

## 📁 Estrutura do Projeto

```
atendai/
│
├── app.py                  # Aplicação principal Flask
├── chatbot.db              # Banco de dados SQLite
├── templates/              # Interface HTML
├── static/                 # Arquivos CSS e JS (opcional)
├── requirements.txt        # Dependências
└── README.md               # Este arquivo
```

---

## 🚀 Como Executar Localmente

### 1. Clone o projeto

```bash
git clone https://github.com/seu-usuario/atendai.git
cd atendai
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

> Se você não tiver um arquivo `requirements.txt`, use:
```bash
pip install flask openai
```

### 3. Defina sua chave da API OpenAI

No `app.py`, edite esta linha:

```python
openai.api_key = 'sua-api-key-aqui'
```

### 4. Execute o servidor

```bash
python app.py
```

Acesse no navegador:  
[http://localhost:5000](http://localhost:5000)

---

## 📊 Estrutura do Banco de Dados

- `qa`: Base de conhecimento com perguntas e respostas
- `history`: Histórico de mensagens por sessão e usuário
- `unknown`: Registro de perguntas não reconhecidas
- `feedback`: Armazenamento de feedbacks úteis/não úteis

---

## 🧠 Inteligência Artificial

O AtendAI utiliza a API GPT-3.5 para gerar respostas em linguagem natural, com base no histórico da conversa e contexto do usuário. Se a pergunta já estiver na base de dados, a resposta é retornada diretamente. Caso contrário, a IA gera uma nova resposta.

---

## ✍️ Contribuições

Pull requests são bem-vindos!  
Abra uma issue para sugestões de novas funcionalidades ou melhorias.

---

## 🧾 Licença

Este projeto está sob a licença MIT.  
Sinta-se livre para utilizar, modificar e redistribuir com os devidos créditos.

---

## 📷 Screenshot

![Tela do Chatbot](https://via.placeholder.com/800x400.png?text=AtendAI+-+Chatbot+Inteligente)

---

## 📬 Contato

Desenvolvido por **Alexandre Vinhola** 
