# AtendAI

AtendAI é um chatbot inteligente que funciona localmente, utilizando o modelo de linguagem **Mistral 7B via Ollama**. Ele permite interação em português, responde dúvidas, armazena histórico de conversas e não depende de APIs pagas.

## 🚀 Funcionalidades

- Respostas automáticas com IA local (Mistral 7B).
- Armazena histórico de conversas por sessão.
- Permite criação de base de conhecimento (FAQ).
- Interface Web simples e responsiva com HTML + CSS.
- Processamento de linguagem natural (NLP) offline via Ollama.
- Totalmente gratuito e privativo, roda localmente no seu PC.

## 🔧 Tecnologias Utilizadas

- Python 3.x
- Flask
- SQLite
- Ollama + Mistral 7B (IA local)
- HTML, CSS (Frontend básico)

## ⚙️ Instalação

### 1️⃣ Instalar dependências Python:

```bash
pip install -r requirements.txt
```

### 2️⃣ Instalar Ollama (backend de IA local)

- Acesse: [https://ollama.com/](https://ollama.com/)  
- Baixe e instale para Windows, Mac ou Linux.

### 3️⃣ Baixar o modelo Mistral:

```bash
ollama pull mistral
```

## ▶️ Como executar

Execute o servidor Flask:

```bash
python atendai.py
```

Acesse no navegador:

```
http://127.0.0.1:5000
```

## 🧠 Como funciona

- O chatbot verifica se existe uma resposta na base de dados (`SQLite`).
- Se não existir, ele consulta a IA local (Mistral via Ollama).
- Todo o histórico da sessão é enviado junto, permitindo conversas contextuais.
- Respostas podem ser armazenadas automaticamente para melhorar o atendimento.

## 📂 Estrutura do Projeto

```
atendai/
├── atendai.py
├── chatbot.db
├── requirements.txt
├── README.md
```

## 📝 Roadmap de Melhorias

- [ ] Adicionar painel administrativo para visualizar perguntas desconhecidas.
- [ ] Implementar exportação do histórico em PDF ou CSV.
- [ ] Melhorar a interface com Bootstrap ou Tailwind CSS.
- [ ] Suporte para múltiplos usuários com login.
- [ ] Deploy local via Docker.

## 🤝 Contribuição

Sinta-se livre para enviar melhorias, abrir issues ou sugerir novas funcionalidades.

## 💡 Créditos

Desenvolvido por Alexandre Vinhola utilizando IA Mistral 7B + Ollama + Flask + SQLite.