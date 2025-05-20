import sqlite3
import uuid
from datetime import datetime
from typing import Optional, List, Dict

# Dependência para NLP (API OpenAI Chat)
import openai
from flask import Flask, request, jsonify, render_template_string

# Configurar API Key
openai.api_key = ''  # Defina sua chave aqui ou via variável de ambiente

DB_PATH = 'chatbot.db'

# -----------------------
# Módulo de Banco de Dados
# -----------------------
class KnowledgeDB:
    def __init__(self, db_path: str = DB_PATH):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_tables()
        self._populate_initial_data()

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS qa(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            question TEXT UNIQUE,
                            answer TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS history(
                            id TEXT,
                            session_id TEXT,
                            user_id TEXT,
                            role TEXT,
                            content TEXT,
                            timestamp TIMESTAMP)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS unknown(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            question TEXT,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS feedback(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            history_id TEXT,
                            useful BOOLEAN,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        self.conn.commit()

    def _populate_initial_data(self):
        questions_answers = [
            ("Como posso entrar em contato com o suporte?", "Você pode entrar em contato com o suporte pelo telefone, e-mail ou chat ao vivo."),
            ("Quais são os horários de atendimento?", "Nosso atendimento funciona de segunda a sexta-feira, das 9h às 18h."),
            ("O que devo fazer se minha conta foi hackeada?", "Se você suspeitar que sua conta foi hackeada, entre em contato imediatamente com nosso suporte para bloquear o acesso."),
            ("Como alterar meu endereço de e-mail?", "Você pode alterar seu endereço de e-mail acessando as configurações da sua conta."),
            ("Como posso recuperar minha senha?", "Se você esqueceu sua senha, clique em 'Esqueci minha senha' na página de login para redefini-la."),
            ("Como posso verificar o status do meu pedido?", "Você pode verificar o status do seu pedido acessando a seção 'Meus Pedidos' no seu perfil."),
            ("Quais serviços são oferecidos?", "Oferecemos serviços de atendimento bancário, incluindo consultas de saldo, transferências, pagamentos de contas, entre outros."),
            ("O que posso fazer no AtendAI?", "No AtendAI, você pode obter respostas rápidas sobre serviços, tirar dúvidas e registrar problemas."),
            ("Como posso registrar uma nova dúvida?", "Basta digitar sua dúvida na caixa de entrada e o AtendAI responderá automaticamente."),
            ("Como visualizar o histórico de conversas?", "Você pode acessar o histórico de conversas diretamente no painel de controle do seu perfil."),
            ("Posso revisar as respostas que dei anteriormente?", "Sim, você pode revisar suas interações anteriores acessando o histórico de conversas."),
            ("Como dar feedback sobre a resposta?", "Ao final de cada resposta, você pode selecionar se a resposta foi útil ou não."),
            ("Como encerrar minha sessão?", "Você pode encerrar sua sessão a qualquer momento clicando em 'Sair' no menu."),
            ("Como funciona o feedback no AtendAI?", "O feedback é usado para melhorar as respostas e a experiência de atendimento. Se a resposta for útil, você pode marcá-la como positiva."),
            ("O que acontece quando deixo um feedback útil?", "Quando um feedback é marcado como útil, ele ajuda a aprimorar o sistema de respostas e a melhorar as interações futuras."),
            ("Posso sugerir melhorias para o sistema?", "Sim, você pode sugerir melhorias entrando em contato com o suporte ou usando a funcionalidade de feedback."),
            ("Onde posso encontrar mais informações sobre o funcionamento do sistema?", "Você pode encontrar mais informações sobre o sistema no nosso site ou entrando em contato com o suporte."),
            ("Como o AtendAI aprende novas respostas?", "O AtendAI aprende com o feedback dos usuários e com as novas respostas adicionadas ao banco de dados do sistema."),
        ]
        
        cursor = self.conn.cursor()
        for question, answer in questions_answers:
            cursor.execute('INSERT OR IGNORE INTO qa(question, answer) VALUES(?, ?)', (question, answer))
        self.conn.commit()

    def get_answer(self, question: str) -> Optional[str]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT answer FROM qa WHERE question = ?', (question,))
        row = cursor.fetchone()
        return row[0] if row else None

    def save_qa(self, question: str, answer: str):
        cursor = self.conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO qa(question, answer) VALUES(?, ?)', (question, answer))
        self.conn.commit()

    def log_message(self, session_id: str, user_id: str, role: str, content: str):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO history(id, session_id, user_id, role, content, timestamp) VALUES(?,?,?,?,?,?)',
            (str(uuid.uuid4()), session_id, user_id, role, content, datetime.now())
        )
        self.conn.commit()

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT role, content FROM history WHERE session_id = ? ORDER BY timestamp', (session_id,))
        return [{'role': row[0], 'content': row[1]} for row in cursor.fetchall()]

    def log_unknown(self, question: str):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO unknown(question) VALUES(?)', (question,))
        self.conn.commit()

    def save_feedback(self, history_id: str, useful: bool):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO feedback(history_id, useful) VALUES(?,?)', (history_id, useful))
        self.conn.commit()

# -----------------------
# Módulo de NLP
# -----------------------
class NLPProcessor:
    SYSTEM_PROMPT = (
        "Você é um assistente virtual de atendimento ao cliente bancário. "
        "Responda de forma clara e amigável."
    )

    @staticmethod
    def generate_response(messages: List[Dict[str, str]]) -> str:
        chat = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=messages,
            max_tokens=150,
            temperature=0.7
        )
        return chat.choices[0].message['content'].strip()

# -----------------------
# Aplicação Flask
# -----------------------
app = Flask(__name__)

db = KnowledgeDB()

# Saudação padrão e variações reconhecidas
greetings = {"olá": "Olá! Como posso ajudar você hoje?", 
             "oi": "Oi! Em que posso ajudar?",
             "bom dia": "Bom dia! Como posso ajudar?",
             "boa tarde": "Boa tarde! Em que posso ajudar?",
             "boa noite": "Boa noite! Como posso ajudar?"}

# Template com Bootstrap
CHAT_TEMPLATE = '''
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AtendAI</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body { font-family: Arial; margin: 2rem; }
    #chat { border:1px solid #ccc; padding:1rem; height:300px; overflow-y:scroll; margin-bottom: 1rem; }
    .user { color: blue; } .bot { color: green; }
    .loading { display: none; font-style: italic; }
  </style>
</head>
<body>
  <div class="container">
    <h1 class="text-center">AtendAI</h1>
    <div id="chat"></div>
    <div id="loading" class="loading text-center">Carregando...</div>
    <div class="input-group">
      <input type="text" id="input" class="form-control" placeholder="Sua mensagem..."/>
      <button class="btn btn-primary" onclick="send()">Enviar</button>
    </div>
  </div>
  
  <script>
    function send() {
      const msg = document.getElementById('input').value;
      if (!msg) return;
      append('Você', msg, 'user');
      document.getElementById('loading').style.display = 'block';
      
      fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: msg, user_id: 'anon', session_id: window.session_id })
      })
      .then(r => r.json())
      .then(d => {
        append('Bot', d.answer, 'bot');
        document.getElementById('loading').style.display = 'none';
      });
      
      document.getElementById('input').value = '';
    }

    function append(who, text, cls) {
      const c = document.getElementById('chat');
      const p = document.createElement('p');
      p.className = cls;
      p.innerHTML = `<strong>${who}:</strong> ${text}`;
      c.appendChild(p);
      c.scrollTop = c.scrollHeight;
    }

    window.session_id = Math.random().toString(36).substring(2);
  </script>
</body>
</html>
'''

@app.route('/', methods=['GET'])
def index():
    return render_template_string(CHAT_TEMPLATE)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question', '').strip()
    user_id = data.get('user_id', 'anon')
    session_id = data.get('session_id', str(uuid.uuid4()))

    # Reconhecimento de saudações simples
    lower_q = question.lower()
    if lower_q in greetings:
        answer = greetings[lower_q]
        db.log_message(session_id, user_id, 'user', question)
        db.log_message(session_id, user_id, 'assistant', answer)
        return jsonify({'answer': answer})

    # Monta contexto para IA
    messages = [{'role':'system','content': NLPProcessor.SYSTEM_PROMPT}]
    history = db.get_history(session_id)
    messages.extend(history)
    messages.append({'role':'user','content': question})

    # Busca resposta prévia
    stored = db.get_answer(question)
    if stored:
        answer = stored
    else:
        answer = NLPProcessor.generate_response(messages)
        db.log_unknown(question)
        db.save_qa(question, answer)

    db.log_message(session_id, user_id, 'user', question)
    db.log_message(session_id, user_id, 'assistant', answer)

    return jsonify({'answer': answer})


if __name__ == '__main__':
    app.run(debug=True)
